# Create your views here.
import random
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool, RippleTask, StateVariable
from common.views.services import get_db_record_or_404
from contracts.models import ContractAssignment, ContractPriority
from contracts.services import assign_contracts_to_teams, create_contracts, get_winner_teams, set_contracts_order
from finance.models import CashChange, Loan, Overdraft, Repayment, Transaction
from finance.views.services import new_loan
from people.models import CustomUser, Player, SimulationClass, Team
from people.views.services import get_player_or_404, get_simulation_teams
from production.models import Factory, Production, Storage
from production.views.services import new_factory, select_product, set_activity_level
from rd.models import DynamicRD
from rd.views.services import create_dynamic_rd_items, pause_rd, resume_rd, start_rd


@extend_schema_view(post=extend_schema(tags=["Quarter-Wise"]))
class StartNewSimulation(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def _start_new_simulation(self, player: Player, team_mode: bool) -> None:
        DynamicRD.objects.filter(player=player).delete()
        Storage.objects.filter(player=player).delete()
        Production.objects.filter(player=player).delete()
        Factory.objects.filter(player=player).delete()
        if player.team and player.team.simulation_class:
            player.team.simulation_class.delete()
            # Contracts and Team will be deleted automatically
            # since it's on_delete cascade
        Transaction.objects.filter(player=player).delete()
        Repayment.objects.filter(player=player).delete()
        Overdraft.objects.filter(player=player).delete()
        Loan.objects.filter(player=player).delete()
        CashChange.objects.filter(player=player).delete()
        ContractPriority.objects.filter(player=player).delete()
        ContractAssignment.objects.filter(player=player).delete()
        StateVariable.objects.filter(player=player).delete()
        RippleTask.objects.filter(player=player).delete()
        DecisionPool.objects.filter(player=player).delete()

        simulation_class = SimulationClass.objects.create(name=f"{player}'s Simulation Class")
        # 1. Create a Team for the single user
        player_team = Team(name=f"{player}'s Team", simulation_class=simulation_class)
        bot_teams = [Team(name=f"{player}'s Bot {i+1}", simulation_class=simulation_class) for i in range(4)]
        teams_to_create = [player_team] + bot_teams
        teams = Team.objects.bulk_create(teams_to_create)
        player.team = teams[0]
        player.save()

        # 2. Create Contracts
        create_contracts(simulation_class=simulation_class)
        # 4. Create Dynamic RD Items
        create_dynamic_rd_items(player=player)
        # 5. Create State Variables
        state_variables = StateVariable.objects.create(player=player)

    def post(self, request: Request) -> Response:
        # Get player
        user: CustomUser = request.user
        player = get_player_or_404(user, select_related_tables=["team"])
        team_mode = request.data.get("team_mode", False)

        self._start_new_simulation(player, team_mode)

        return Response("Welcome to the new simulation!", status=status.HTTP_200_OK)


@extend_schema_view(post=extend_schema(tags=["Quarter-Wise"]))
class FinishQuarter(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    @transaction.atomic
    def post(self, request: Request) -> Response:
        # Get player
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter
        prefetch_decision_pool = Prefetch(
            "decision_pool", queryset=DecisionPool.objects.filter(made_at_quarter=current_quarter)
        )
        player = get_player_or_404(user, [prefetch_decision_pool])

        # Process Player's decisions
        decision_states = [self._process_decision(player, decision=decision) for decision in player.decision_pool.all()]

        # calculate each production's produced quantity
        productions: list[Production] = player.productions.filter(quarter=current_quarter)
        print(f"A total of {len(productions)} at quarter {current_quarter} was found.")
        for production in productions:
            base = production.factory.base
            factor = production.activity_level / 100
            production.produced_quantity = base * (3 - factor) * factor**2 / 2
            # FIXME: Use bulk_update for fewer queries
            production.save()
            print(f"Factory base is {base}, factor is {factor}, produced quantity is {production.produced_quantity}")
        # add produced units to storage
        for production in productions:
            storage, _ = Storage.objects.get_or_create(
                player=player,
                product=production.product,
            )
            # finished_good_inventory = production.produced_quantity * production.product.final_cost
            storage.quantity = F("quantity") + production.produced_quantity
            # storage.finished_good_inventory = F("finished_good_inventory") + finished_good_inventory
            storage.save()

        # feed contracts from storage
        assigned_contracts: list[ContractAssignment] = player.contracts.filter(
            contract__closure_quarter=current_quarter - 1
        )
        for assigned_contract in assigned_contracts:
            if (
                assigned_contract.status == ContractAssignment.Statuses.FULFILLED
                or assigned_contract.status == ContractAssignment.Statuses.EXPIRED
            ):
                continue

            dynamic_rd_obj = get_db_record_or_404(
                DynamicRD,
                player=player,
                category=assigned_contract.contract.deliverable_product,
                order=1,
            )
            storage: Storage = Storage.objects.filter(player=player, product=dynamic_rd_obj).first()
            if not storage or storage.quantity < assigned_contract.contract.quantity:
                assigned_contract.status = ContractAssignment.Statuses.EXPIRED
                assigned_contract.save()
                continue

            storage.quantity = F("quantity") - assigned_contract.contract.quantity
            storage.save()
            assigned_contract.status = ContractAssignment.Statuses.FULFILLED
            assigned_contract.save()

        # expire non-fulfilled contracts
        # they got expired, didn't they?

        # Do ripple tasks
        self._process_ripple_tasks(player=player, current_quarter=current_quarter)

        # self._receive_fulfilled_contracts_money(player=player, current_quarter=current_quarter)

        self._increment_quarter(player)

        response = self._generate_response(player=player)
        return Response(response, status=status.HTTP_200_OK)

    def _process_decision(self, player: Player, decision: DecisionPool):
        try:
            match decision.endpoint:
                case "rd/start":
                    return decision.endpoint, start_rd(player=player, decision=decision)
                # create pause, resume, new loan, new factory, select_product, set_activity_level and set_contracts_order
                case "rd/pause":
                    return decision.endpoint, pause_rd(player=player, decision=decision)
                case "rd/resume":
                    return decision.endpoint, resume_rd(player=player, decision=decision)
                case "finance/new_loan":
                    return decision.endpoint, new_loan(player=player, decision=decision)
                case "production/new_factory":
                    return decision.endpoint, new_factory(player=player, decision=decision)
                case "production/select_product":
                    return decision.endpoint, select_product(player=player, decision=decision)
                case "production/set_activity_level":
                    return decision.endpoint, set_activity_level(player=player, decision=decision)
                case "contracts/set_contracts_order":
                    # FIXME: We need bots or teams for get_winner_teams
                    # A better response is needed
                    response = set_contracts_order(player=player, decision=decision)
                    bots = get_simulation_teams(team=player.team)
                    # replace first random with bot's esg index and second random with bot's marketing budget
                    winners = get_winner_teams(
                        [
                            (
                                player,
                                player.state_variables.esg_index,
                                Decimal(player.state_variables.marketing_budget),
                            ),
                            *[(bot, random.randrange(0, 2), random.randrange(5000, 10_000)) for bot in bots],
                        ]
                    )
                    assignment_response = assign_contracts_to_teams(winners, current_quarter=decision.made_at_quarter)
                    print(assignment_response)
                    return decision.endpoint, response

        except APIException as e:
            return decision.endpoint, str(e)

    def _process_ripple_tasks(self, player: Player, current_quarter: int):
        ripple_tasks: list[RippleTask] | None = RippleTask.objects.filter(player=player, run_at_quarter=current_quarter)
        dynamic_rd_objects_to_update = []
        tasks_to_update: list[RippleTask] = []
        tasks_to_delete: list[RippleTask] = []
        for ripple_task in ripple_tasks:
            if ripple_task.type == RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME:
                self._increment_rd_dev_time(
                    ripple_task=ripple_task,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                    dynamic_rd_objects_to_update=dynamic_rd_objects_to_update,
                )
            if ripple_task.type == RippleTask.TaskTypes.PRODUCTION:
                self._inject_products_into_storage(player=player, ripple_task=ripple_task)

        if dynamic_rd_objects_to_update:
            DynamicRD.objects.bulk_update(dynamic_rd_objects_to_update, ["time_spent_developing"])
        if tasks_to_update:
            RippleTask.objects.bulk_update(tasks_to_update, ["run_at_quarter"])
        if tasks_to_delete:
            RippleTask.objects.filter(pk__in=[task.pk for task in tasks_to_delete]).delete()

    def _increment_rd_dev_time(
        self,
        ripple_task: RippleTask,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
        dynamic_rd_objects_to_update: list[DynamicRD],
    ):
        dynamic_rd_object = get_db_record_or_404(DynamicRD, id=ripple_task.json_body["dynamic_rd_id"])
        time_spent_developing = dynamic_rd_object.time_spent_developing
        dynamic_rd_object.time_spent_developing = F("time_spent_developing") + 1
        dynamic_rd_objects_to_update.append(dynamic_rd_object)

        """
        Replicating the 'is_researching' to see if it'll be researching in the next quarter
        Can't use ripple_task.dynamic_rd_object.time_spent_developing directly since it hasn't
        been saved yet ;)
        """
        if time_spent_developing + 1 < dynamic_rd_object.development_duration and dynamic_rd_object.started_at > 0:
            # If research is still ongoing, run next quarter, too
            ripple_task.run_at_quarter = F("run_at_quarter") + 1
            ripple_tasks_to_update.append(ripple_task)
        else:
            ripple_tasks_to_delete.append(ripple_task)

    def _inject_products_into_storage(player: Player, ripple_task: RippleTask): ...

    def _increment_quarter(self, player: Player) -> None:
        player.state_variables.quarter = F("quarter") + 1
        player.state_variables.save()
        player.state_variables.refresh_from_db()

    def _generate_response(self, player: Player):
        if player.state_variables.quarter == player.state_variables.simulation_duration:
            response = {
                "data": {
                    "message": "simulation finished",
                    "current_quarter": player.state_variables.quarter,
                }
            }
        response = {"data": {"current_quarter": player.state_variables.quarter}}
        return response
