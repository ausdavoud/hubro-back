from decimal import Decimal

from django.db import DatabaseError, transaction
from django.db.models import F, Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool, RippleTask, StateVariable
from common.serializers import CompanyInfoSerializer, StateVariableSerializer
from common.views import exceptions as common_exceptions
from common.views.exceptions import GameLogicError
from common.views.services import (
    get_db_record_select_prefetch_or_404,
    get_serializer_or_400,
)
from contracts.models import ContractAssignment
from contracts.views.services import (
    assign_contracts_to_teams,
    create_contracts,
    get_winner_teams,
    set_contracts_order,
)
from contracts.views.views import ContractView
from esg_reporting.views.services import enable_esg_reporting
from esg_reporting.views.views import ESGReportingView
from finance.models import FinancialAccount, Transaction
from finance.views.services import create_transaction, new_loan
from finance.views.views import FinanceView
from people.models import CustomUser, Player, SimulationClass, Team
from people.views.services import get_simulation_teams
from production.models import Production, Storage
from production.views.services import (
    new_factory,
    select_product,
    set_activity_level,
)
from production.views.views import ProductionView
from rd.models import DynamicRD, RDCategories
from rd.views.services import (
    create_dynamic_rd_items,
    pause_rd,
    resume_rd,
    start_rd,
)
from rd.views.views import RDView


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.role == CustomUser.UserRoles.INSTRUCTOR
        )


@extend_schema_view(get=extend_schema(tags=["Quarter-Wise"]))
class StateVariableView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]
    serializer_class = StateVariableSerializer

    def get(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        state_variable = team.state_variables
        serialized_state_variable = StateVariableSerializer(state_variable)
        response = {"data": serialized_state_variable.data}
        return Response(response, status=status.HTTP_200_OK)


@extend_schema_view(post=extend_schema(tags=["Quarter-Wise"]))
class SetCompanyInfo(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = CompanyInfoSerializer

    def post(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        if team.state_variables.quarter != 1:
            raise GameLogicError(
                description="You can only set company info in the first quarter."
            )
        json_body = self._get_company_info_json_body(request.data)

        team.state_variables.company_name = json_body["company_name"]
        team.state_variables.company_slogan = json_body["company_slogan"]
        team.state_variables.company_icon = json_body["company_icon"]
        team.state_variables.company_icon_bg = json_body["company_icon_bg"]
        team.state_variables.company_icon_color = json_body[
            "company_icon_color"
        ]
        team.state_variables.company_icon_font = json_body["company_icon_font"]
        team.state_variables.save()

        response = CompanyInfoSerializer(team.state_variables).data
        return Response(response, status=status.HTTP_200_OK)

    def _get_company_info_json_body(self, post_data: dict) -> dict:
        serialized_data = get_serializer_or_400(
            CompanyInfoSerializer, post_data
        )
        return serialized_data.validated_data


@extend_schema_view(post=extend_schema(tags=["Quarter-Wise"]))
class StartNewSimulation(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = None

    def post(self, request: Request) -> Response:
        # Get player
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(
            Player, select_related_tables=["team"], user=user
        )

        team_mode = request.data.get("team_mode", False)

        delete_previous_simulation_data(player=player)
        create_new_simulation_data(player=player)

        return Response(
            "Welcome to the new simulation!", status=status.HTTP_200_OK
        )


def delete_previous_simulation_data(player: Player):
    team = player.team
    # Delete old data
    if team:
        if team.simulation_class:
            team.simulation_class.teams.filter(
                team_type=Team.TeamType.BOT
            ).delete()
            team.simulation_class.delete()
        team.delete()


def create_new_simulation_data(player: Player):
    simulation_class = SimulationClass.objects.create(
        name=f"{player}'s Simulation Class"
    )
    # 1. Create a Team for the single user
    player_team = Team(
        name=f"{player}'s Team", simulation_class=simulation_class
    )
    bot_teams = [
        Team(
            name=f"{player}'s Bot {i+1}",
            simulation_class=simulation_class,
            team_type=Team.TeamType.BOT,
        )
        for i in range(4)
    ]
    teams_to_create = [player_team] + bot_teams
    teams = Team.objects.bulk_create(teams_to_create)
    team = teams[0]
    player.team = teams[0]
    player.save()

    # 2. Create Contracts
    create_contracts(simulation_class=simulation_class)
    # 4. Create Dynamic RD Items
    create_dynamic_rd_items(team=team)
    # 5. Create State Variables
    state_variables = [StateVariable(team=team) for team in teams]
    StateVariable.objects.bulk_create(state_variables)


@extend_schema_view(post=extend_schema(tags=["Quarter-Wise"]))
class FinishQuarter(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = None

    @transaction.atomic
    def post(self, request: Request) -> Response:
        # Get player
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        current_quarter = player.team.state_variables.quarter
        prefetch_decision_pool = Prefetch(
            "decision_pool",
            queryset=DecisionPool.objects.filter(
                made_at_quarter=current_quarter
            ),
        )
        team = get_db_record_select_prefetch_or_404(
            Team,
            prefetch_related_tables=[prefetch_decision_pool],
            id=player.team.id,
        )

        # Check if it is the last quarter
        if (
            team.state_variables.quarter
            == team.state_variables.simulation_duration
        ):
            response = {
                "data": {
                    "message": "Simulation is over!",
                    "current_quarter": team.state_variables.quarter,
                }
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Process Team's decisions
        decisions = DecisionPool.objects.filter(
            team=team, made_at_quarter=current_quarter
        )
        decision_states = [
            self._process_decision(team=team, decision=decision)
            for decision in decisions
        ]

        # calculate each production's produced quantity
        productions: list[Production] = team.productions.filter(
            quarter=current_quarter
        )
        for production in productions:
            base = production.factory.base
            factor = production.activity_level / 100
            production.produced_quantity = base * (3 - factor) * factor**2 / 2
            # FIXME: Use bulk_update for fewer queries
            production.save()
        # add produced units to storage
        for production in productions:
            storage, _ = Storage.objects.get_or_create(
                team=team,
                product=production.product,
            )
            # finished_good_inventory = production.produced_quantity * production.product.final_cost
            storage.quantity = F("quantity") + production.produced_quantity
            # storage.finished_good_inventory = F("finished_good_inventory") + finished_good_inventory
            storage.save()

        # feed contracts from storage
        assigned_contracts: list[ContractAssignment] = team.contracts.filter(
            contract__closure_quarter=current_quarter - 1
        )
        for assigned_contract in assigned_contracts:
            if (
                assigned_contract.status
                == ContractAssignment.Statuses.FULFILLED
                or assigned_contract.status
                == ContractAssignment.Statuses.EXPIRED
            ):
                continue

            dynamic_rd_obj = get_db_record_select_prefetch_or_404(
                DynamicRD,
                team=team,
                category=assigned_contract.contract.deliverable_product,
                order=1,
            )
            storage: Storage = Storage.objects.filter(
                team=team, product=dynamic_rd_obj
            ).first()
            if (
                not storage
                or storage.quantity < assigned_contract.contract.quantity
            ):
                assigned_contract.status = ContractAssignment.Statuses.EXPIRED
                assigned_contract.save()
                continue

            storage.quantity = (
                F("quantity") - assigned_contract.contract.quantity
            )
            storage.save()
            assigned_contract.status = ContractAssignment.Statuses.FULFILLED
            assigned_contract.save()

        # expire non-fulfilled contracts
        # they got expired, didn't they?

        # Do ripple tasks
        self._process_ripple_tasks(team=team, current_quarter=current_quarter)

        # self._receive_fulfilled_contracts_money(team=team, current_quarter=current_quarter)

        self._increment_quarter(team=team)

        response = self._generate_response(team=team)
        return Response(response, status=status.HTTP_200_OK)

    def _process_decision(self, team: Team, decision: DecisionPool):
        try:
            match decision.endpoint:
                case RDView.ENDPOINTS.START_RD:
                    return decision.endpoint, start_rd(
                        team=team, decision=decision
                    )
                # create pause, resume, new loan, new factory, select_product, set_activity_level and set_contracts_order
                case RDView.ENDPOINTS.PAUSE_RD:
                    return decision.endpoint, pause_rd(
                        team=team, decision=decision
                    )
                case RDView.ENDPOINTS.RESUME_RD:
                    return decision.endpoint, resume_rd(
                        team=team, decision=decision
                    )
                case FinanceView.ENDPOINTS.NEW_LOAN:
                    return decision.endpoint, new_loan(
                        team=team, decision=decision
                    )
                case ProductionView.ENDPOINTS.NEW_FACTORY:
                    return decision.endpoint, new_factory(
                        team=team, decision=decision
                    )
                case ProductionView.ENDPOINTS.SELECT_PRODUCT:
                    return decision.endpoint, select_product(
                        team=team, decision=decision
                    )
                case ProductionView.ENDPOINTS.SET_ACTIVITY_LEVEL:
                    return decision.endpoint, set_activity_level(
                        team=team, decision=decision
                    )
                case ContractView.ENDPOINTS.SET_CONTRACTS_ORDER:
                    # FIXME: We need bots or teams for get_winner_teams
                    # A better response is needed
                    response = set_contracts_order(
                        team=team, decision=decision
                    )
                    simulation_teams = get_simulation_teams(team=team)
                    # replace first random with bot's esg index and second random with bot's marketing budget
                    winners = get_winner_teams(
                        [
                            (
                                team,
                                team.state_variables.esg_index,
                                Decimal(team.state_variables.marketing_budget),
                            )
                            for team in simulation_teams
                        ]
                    )
                    assignment_response = assign_contracts_to_teams(
                        winners, current_quarter=decision.made_at_quarter
                    )
                    return decision.endpoint, response
                case ESGReportingView.ENDPOINTS.ENABLE_ESG_REPORTING:
                    return decision.endpoint, enable_esg_reporting(team=team)

        except APIException as e:
            return decision.endpoint, str(e)

    def _process_ripple_tasks(self, team: Team, current_quarter: int):
        ripple_tasks: list[RippleTask] | None = RippleTask.objects.filter(
            team=team, run_at_quarter=current_quarter
        )
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
            if ripple_task.type == RippleTask.TaskTypes.ESG_REPORTING:
                self._pay_esg_reporting_fee(
                    team=team,
                    current_quarter=current_quarter,
                    ripple_task=ripple_task,
                    ripple_tasks_to_update=tasks_to_update,
                )
            if ripple_task.type == RippleTask.TaskTypes.LOAN_REPAYMENT:
                self._loan_repayment(
                    ripple_task=ripple_task,
                    team=team,
                    current_quarter=current_quarter,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                )
            if ripple_task.type == RippleTask.TaskTypes.LOAN_INTEREST:
                self._loan_interest(
                    ripple_task=ripple_task,
                    team=team,
                    current_quarter=current_quarter,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                )
            if ripple_task.type == RippleTask.TaskTypes.FACTORY_DEPRECIATION:
                self._factory_depreciation(
                    ripple_task=ripple_task,
                    team=team,
                    current_quarter=current_quarter,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                )

            if ripple_task.type == RippleTask.TaskTypes.FACTORY_MAINTENANCE:
                self._factory_maintenance_cost(
                    ripple_task=ripple_task,
                    team=team,
                    current_quarter=current_quarter,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                )

            if ripple_task.type == RippleTask.TaskTypes.PAY_RD_COST:
                self._pay_rd_cost(
                    ripple_task=ripple_task,
                    team=team,
                    current_quarter=current_quarter,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                )

            if (
                ripple_task.type
                == RippleTask.TaskTypes.AMORTIZATION_OF_PROJECTS
            ):
                self._pay_product_amortization(
                    ripple_task=ripple_task,
                    team=team,
                    current_quarter=current_quarter,
                    ripple_tasks_to_update=tasks_to_update,
                    ripple_tasks_to_delete=tasks_to_delete,
                )

        if dynamic_rd_objects_to_update:
            DynamicRD.objects.bulk_update(
                dynamic_rd_objects_to_update, ["time_spent_developing"]
            )
        if tasks_to_update:
            RippleTask.objects.bulk_update(tasks_to_update, ["run_at_quarter"])
        if tasks_to_delete:
            RippleTask.objects.filter(
                pk__in=[task.pk for task in tasks_to_delete]
            ).delete()

    def _increment_rd_dev_time(
        self,
        ripple_task: RippleTask,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
        dynamic_rd_objects_to_update: list[DynamicRD],
    ):
        team = ripple_task.team
        dynamic_rd_object: DynamicRD = get_db_record_select_prefetch_or_404(
            DynamicRD,
            id=ripple_task.json_body["dynamic_rd_id"],
        )
        time_spent_developing = dynamic_rd_object.time_spent_developing
        dynamic_rd_object.time_spent_developing = (
            F("time_spent_developing") + 1
        )
        dynamic_rd_objects_to_update.append(dynamic_rd_object)

        """
        Replicating the 'is_researching' to see if it'll be researching in the next quarter
        Can't use ripple_task.dynamic_rd_object.time_spent_developing directly since it hasn't
        been saved yet ;)
        """
        if (
            time_spent_developing + 1 < dynamic_rd_object.development_duration
            and dynamic_rd_object.started_at > 0
        ):
            # If research is still ongoing, run next quarter, too
            ripple_task.run_at_quarter = F("run_at_quarter") + 1
            ripple_tasks_to_update.append(ripple_task)
        else:
            # If research is done, delete the task

            # if dynamic rd object is of type Production, we should update emission_effect of all products
            if dynamic_rd_object.category == RDCategories.PRODUCTION:
                DynamicRD.objects.filter(
                    team=team,
                    type=DynamicRD.RDTypes.PRODUCT,
                ).update(
                    emission_effect=F("emission_effect")
                    + dynamic_rd_object.emission_reduction,
                )
            # if it's not production but it's an upgrade, upgrade the mat_cost_effect of its product
            elif dynamic_rd_object.type == DynamicRD.RDTypes.UPGRADE:
                DynamicRD.objects.filter(
                    team=team,
                    category=dynamic_rd_object.category,
                    order=1,
                ).update(
                    unit_mat_cost_effect=F("unit_mat_cost_effect")
                    + dynamic_rd_object.unit_mat_cost_reduction,
                )
            ripple_tasks_to_delete.append(ripple_task)

    def _pay_esg_reporting_fee(
        self,
        team: Team,
        current_quarter: int,
        ripple_task: RippleTask,
        ripple_tasks_to_update: list[RippleTask],
    ):
        try:
            with transaction.atomic():
                amount = ripple_task.json_body["amount"]
                # Transaction
                # finding cash account
                cash_account = get_db_record_select_prefetch_or_404(
                    FinancialAccount,
                    code=FinancialAccount.AccountCodes.CASH,
                )
                # finding marketing account
                promotion_account = get_db_record_select_prefetch_or_404(
                    FinancialAccount,
                    code=FinancialAccount.AccountCodes.PROMOTION,
                )

                credit_transaction = Transaction.objects.create(
                    team=team,
                    category=Transaction.Categories.EXTRAORDINARY_PR_EXPENSES,
                    quarter=current_quarter,
                    debit_amount=0,
                    credit_amount=amount,
                    financial_account=cash_account,
                )
                debit_transaction = Transaction.objects.create(
                    team=team,
                    category=Transaction.Categories.EXTRAORDINARY_PR_EXPENSES,
                    quarter=current_quarter,
                    debit_amount=amount,
                    credit_amount=0,
                    financial_account=promotion_account,
                )

                if amount != 3000_00:
                    ripple_task.json_body["amount"] = 3000_00
                ripple_task.save()

                # We update the `run_at_quarter` using the bulk_update
                ripple_task.run_at_quarter += 1
                ripple_tasks_to_update.append(ripple_task)
        except DatabaseError:
            raise common_exceptions.AtomicTransactionError(
                "Ripple task: ESG reporting"
            )

    def _increment_quarter(self, team: Team) -> None:
        team.state_variables.quarter = F("quarter") + 1
        team.state_variables.save()
        team.state_variables.refresh_from_db()

    def _loan_repayment(
        self,
        ripple_task: RippleTask,
        team: Team,
        current_quarter: int,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
    ) -> None:
        current_portion_of_loans_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.CURRENT_PORTION_OF_LOANS_PAYABLE,
        )
        cash_account = get_db_record_select_prefetch_or_404(
            FinancialAccount, code=FinancialAccount.AccountCodes.CASH
        )
        amount = ripple_task.json_body["amount"]
        create_transaction(
            team=team,
            quarter=current_quarter,
            amount=amount,
            category=Transaction.Categories.LOAN_REPAYMENT,
            debit_account=current_portion_of_loans_account,
            credit_account=cash_account,
        )
        ripple_task.json_body["quarters_paid"] += 1
        if (
            ripple_task.json_body["quarters_paid"]
            == ripple_task.json_body["quarters_to_pay"]
        ):
            ripple_tasks_to_delete.append(ripple_task)
        ripple_tasks_to_update.append(ripple_task)

    def _loan_interest(
        self,
        ripple_task: RippleTask,
        team: Team,
        current_quarter: int,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
    ) -> None:
        interest_expenses_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.INTEREST_EXPENSES,
        )
        cash_account = get_db_record_select_prefetch_or_404(
            FinancialAccount, code=FinancialAccount.AccountCodes.CASH
        )
        amount = ripple_task.json_body["amount"]
        create_transaction(
            team=team,
            quarter=current_quarter,
            amount=amount,
            category=Transaction.Categories.LOAN_INTEREST,
            debit_account=interest_expenses_account,
            credit_account=cash_account,
        )
        ripple_task.json_body["quarters_paid"] += 1
        if (
            ripple_task.json_body["quarters_paid"]
            == ripple_task.json_body["quarters_to_pay"]
        ):
            ripple_tasks_to_delete.append(ripple_task)
        ripple_tasks_to_update

    def _factory_depreciation(
        ripple_task: RippleTask,
        team: Team,
        current_quarter: int,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
    ):
        factories_financial_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.FACTORIES,
        )
        depreciation_of_factories_financial_account = (
            get_db_record_select_prefetch_or_404(
                FinancialAccount,
                code=FinancialAccount.AccountCodes.DEPRECIATION_OF_FACTORIES,
            )
        )
        create_transaction(
            team=team,
            quarter=current_quarter,
            amount=ripple_task.json_body["depreciation_cost"],
            category=Transaction.Categories.DEPRECIATION_OF_FACTORIES,
            credit_account=factories_financial_account,
            debit_account=depreciation_of_factories_financial_account,
        )

        if (
            ripple_task.json_body["depreciation_duration"]
            == ripple_task.json_body["quarters_paid"]
        ):
            pass
            # commented this section because depreciation happens
            # only for the first 20 quarters, and if we delete the
            # ripple task, we can't keep track of the depreciation
            # in the next quarters (21, 22, ...)
            # ripple_tasks_to_delete.append(ripple_task)
        else:
            ripple_task.json_body["quarters_paid"] += 1
            ripple_task.run_at_quarter += 1
            ripple_tasks_to_update.append(ripple_task)

    def _factory_maintenance_cost(
        ripple_task: RippleTask,
        team: Team,
        current_quarter: int,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
    ):
        cash_financial_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.CASH,
        )
        maintenance_financial_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.MAINTENANCE,
        )
        create_transaction(
            team=team,
            quarter=current_quarter,
            amount=ripple_task.json_body["maintenance_cost"],
            category=Transaction.Categories.MAINTENANCE,
            credit_account=cash_financial_account,
            debit_account=maintenance_financial_account,
        )
        ripple_task.run_at_quarter += 1
        ripple_tasks_to_update.append(ripple_task)

    def _pay_rd_cost(
        self,
        ripple_task: RippleTask,
        team: Team,
        current_quarter: int,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
    ):
        products_blueprints_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.PRODUCTS_BLUEPRINTS,
        )
        cash_account = get_db_record_select_prefetch_or_404(
            FinancialAccount, code=FinancialAccount.AccountCodes.CASH
        )
        pay_dynamic_rd_cost = create_transaction(
            team=team,
            quarter=ripple_task.run_at_quarter,
            amount=ripple_task.json_body["amount"],
            category=Transaction.Categories.RESEARCH_PROJECTS,
            debit_account=products_blueprints_account,
            credit_account=cash_account,
        )
        if (
            ripple_task.json_body["quarters_paid"] + 1
            == ripple_task.json_body["development_duration"]
        ):
            ripple_tasks_to_delete.append(ripple_task)
        else:
            ripple_task.run_at_quarter += 1
            ripple_task.json_body["quarters_paid"] += 1
            ripple_tasks_to_update.append(ripple_task)

    def _pay_product_amortization(
        self,
        ripple_task: RippleTask,
        team: Team,
        current_quarter: int,
        ripple_tasks_to_update: list[RippleTask],
        ripple_tasks_to_delete: list[RippleTask],
    ):
        products_blueprint_financial_account = (
            get_db_record_select_prefetch_or_404(
                FinancialAccount,
                code=FinancialAccount.AccountCodes.PRODUCTS_BLUEPRINTS,
            )
        )
        amortization_financial_account = get_db_record_select_prefetch_or_404(
            FinancialAccount,
            code=FinancialAccount.AccountCodes.AMORTIZATION,
        )
        create_transaction(
            team=team,
            quarter=current_quarter,
            amount=ripple_task.json_body["amount"],
            category=Transaction.Categories.AMORTIZATION_OF_PROJECTS,
            credit_account=products_blueprint_financial_account,
            debit_account=amortization_financial_account,
        )
        if (
            ripple_task.json_body["quarters_paid"] + 1
            == ripple_task.json_body["amortization_length"]
        ):
            ripple_tasks_to_delete.append(ripple_task)
        else:
            ripple_task.run_at_quarter += 1
            ripple_task.json_body["quarters_paid"] += 1
            ripple_tasks_to_update.append(ripple_task)

    def _generate_response(self, team: Team):
        if (
            team.state_variables.quarter
            == team.state_variables.simulation_duration
        ):
            response = {
                "data": {
                    "message": "Simulation is over!",
                    "current_quarter": team.state_variables.quarter,
                }
            }
            return response
        response = {"data": {"current_quarter": team.state_variables.quarter}}
        return response
