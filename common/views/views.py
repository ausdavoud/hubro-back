# Create your views here.
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

from common.models import DecisionPool, RippleTask
from common.views.services import get_db_record_or_404
from finance.views.services import new_loan
from people.models import CustomUser
from people.views.services import get_player_or_404
from production.views.services import new_factory, select_product, set_activity_level
from rd.models import DynamicRD
from rd.views.services import pause_rd, resume_rd, start_rd


@extend_schema_view(post=extend_schema(tags=["Finish Quarter"]))
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

        decision_states = []
        response = {}
        for decision in player.decision_pool.all():
            decision: DecisionPool
            try:
                match decision.endpoint:
                    case "rd/start":
                        response = start_rd(player, decision)
                        decision_states.append((decision.endpoint, response))
                    case "rd/pause":
                        response = pause_rd(player, decision)
                        decision_states.append((decision.endpoint, response))
                    case "rd/resume":
                        response = resume_rd(player, decision)
                        decision_states.append((decision.endpoint, response))

                    case "finance/new_loan":
                        response = new_loan(player, decision)
                        decision_states.append((decision.endpoint, response))

                        # case "finance/cancel_loan":
                        """
                        Loans cannot be canceled after being received,
                        so we do not have any actions defined to undo
                        the process of giving a player some loan.
                        """

                    case "production/new_factory":
                        response = new_factory(player=player, decision=decision)
                        decision_states.append((decision.endpoint, response))
                    case "production/select_product":
                        response = select_product(player=player, decision=decision)
                        decision_states.append((decision.endpoint, response))

                    case "production/set_activity_level":
                        response = set_activity_level(player=player, decision=decision)
                        decision_states.append((decision.endpoint, response))
                    case _:
                        decision_states.append((decision.endpoint, False))
            except APIException:
                decision_states.append((decision.endpoint, False))

        print(decision_states)

        # TODO: Implement pre-quarter-finish logic
        # Increment quarter
        if player.state_variables.quarter == player.state_variables.simulation_duration:
            response = {
                "data": {
                    "message": "simulation finished",
                    "quarter": player.state_variables.quarter,
                    "actions": response,
                }
            }
            return Response(response, status=status.HTTP_200_OK)

        player.state_variables.quarter = F("quarter") + 1
        player.state_variables.save()
        player.state_variables.refresh_from_db()
        print(f"Incremented quarter to {player.state_variables.quarter} for {user.email}")

        # Do ripple tasks
        current_quarter = player.state_variables.quarter
        ripple_tasks: list[RippleTask] | None = RippleTask.objects.filter(player=player, run_at_quarter=current_quarter)
        dynamic_rd_objects_to_update = []
        tasks_to_update = []
        tasks_to_delete = []
        for ripple_task in ripple_tasks:
            if ripple_task.type == RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME:
                dynamic_rd_object = get_db_record_or_404(DynamicRD, id=ripple_task.json_body["dynamic_rd_id"])
                time_spent_developing = dynamic_rd_object.time_spent_developing
                dynamic_rd_object.time_spent_developing = F("time_spent_developing") + 1
                dynamic_rd_objects_to_update.append(dynamic_rd_object)
                """
                Replicating the 'is_researching' to see if it'll be researching in the next quarter
                Can't use ripple_task.dynamic_rd_object.time_spent_developing directly since it hasn't
                been saved yet
                """
                time_spent_developing += 1
                if time_spent_developing < dynamic_rd_object.development_duration and dynamic_rd_object.started_at > 0:
                    # If research is still ongoing, run next quarter, too
                    ripple_task.run_at_quarter = F("run_at_quarter") + 1
                    tasks_to_update.append(ripple_tasks)
                else:
                    tasks_to_delete.append(ripple_task)

            if ripple_task.type == RippleTask.TaskTypes.PRODUCTION:
                pass

        """
        This may cause problem in the future since more and more ripple task types will be added
        But note that it still needs to be outside the for loop for the bulk update to mean.
        Otherwise it'll be updated one by one
        """
        if dynamic_rd_objects_to_update:
            DynamicRD.objects.bulk_update(dynamic_rd_objects_to_update, ["time_spent_developing"])
        if tasks_to_update:
            RippleTask.objects.bulk_update(tasks_to_update, ["run_at_quarter"])
        if tasks_to_delete:
            RippleTask.objects.filter(id__in=[task.id for task in tasks_to_delete]).delete()

        response = {"data": {"current_quarter": current_quarter, "actions": decision_states}}
        return Response(response, status=status.HTTP_200_OK)
