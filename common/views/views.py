# Create your views here.
from django.db.models import F, Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool, RippleTask
from people.models import CustomUser
from people.views.services import get_player_or_404
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
        for decision in player.decision_pool.all():
            match decision.endpoint:
                case "rd/start":
                    response = start_rd(player, decision.json_body)
                    decision_states.append((decision.endpoint, response))
                case "rd/pause":
                    response = pause_rd(player, decision.json_body)
                    decision_states.append((decision.endpoint, response))

                case "rd/resume":
                    response = resume_rd(player, decision.json_body)
                    decision_states.append((decision.endpoint, response))
                case _:
                    decision_states.append((decision.endpoint, False))
                    continue

        print(decision_states)

        # TODO: Implement pre-quarter-finish logic
        # Increment quarter
        if player.state_variables.quarter == player.state_variables.simulation_duration:
            response = {"data": "simulation finished"}
            return Response(response, status=status.HTTP_200_OK)

        player.state_variables.quarter = F("quarter") + 1
        player.state_variables.save()
        player.state_variables.refresh_from_db()
        print(f"Incremented quarter to {player.state_variables.quarter} for {user.email}")

        # Do ripple tasks
        current_quarter = player.state_variables.quarter
        ripple_tasks: list[RippleTask] | None = RippleTask.objects.filter(
            player=player, run_at_quarter=current_quarter
        ).select_related("dynamic_rd_object")
        dynamic_rd_objects_to_update = []
        tasks_to_update = []
        tasks_to_delete = []
        for ripple_task in ripple_tasks:
            if ripple_task.type == RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME:
                time_spent_developing = ripple_task.dynamic_rd_object.time_spent_developing
                ripple_task.dynamic_rd_object.time_spent_developing = F("time_spent_developing") + 1
                dynamic_rd_objects_to_update.append(ripple_task.dynamic_rd_object)
                """
                Replicating the 'is_researching' to see if it'll be researching in the next quarter
                Can't use ripple_task.dynamic_rd_object.time_spent_developing directly since it hasn't
                been saved yet
                """
                time_spent_developing += 1
                if (
                    time_spent_developing < ripple_task.dynamic_rd_object.development_duration
                    and ripple_task.dynamic_rd_object.started_at > 0
                ):
                    # If research is still ongoing, run next quarter, too
                    ripple_task.run_at_quarter = F("run_at_quarter") + 1
                    tasks_to_update.append(ripple_tasks)
                else:
                    tasks_to_delete.append(ripple_task)

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

        response = {"data": {"current_quarter": current_quarter}}
        return Response(response, status=status.HTTP_200_OK)
