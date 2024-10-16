from django.db.models import F
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from simulation.models.rd import DynamicRD

from ..models.common import RippleTask
from ..models.people import CustomUser
from .services.common import get_player_or_404


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
        player = get_player_or_404(user, ["rd", "state_variables", "ripple_tasks"])

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
        ripple_tasks: list[RippleTask] = player.ripple_tasks.filter(run_at_quarter=current_quarter)
        rd_objects_to_update = []
        tasks_to_update = []
        tasks_to_delete = []
        for ripple_task in ripple_tasks:
            if ripple_task.type == RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME:
                time_spent_developing = ripple_task.rd_object.time_spent_developing
                ripple_task.rd_object.time_spent_developing = F("time_spent_developing") + 1
                rd_objects_to_update.append(ripple_task.rd_object)
                # Replicating the 'is_researching' to see if it'll be researching in the next quarter
                time_spent_developing += 1
                if (
                    time_spent_developing < ripple_task.rd_object.development_duration
                    and ripple_task.rd_object.started_at > 0
                ):
                    # If research is still ongoing, run next quarter, too
                    ripple_task.run_at_quarter = F("run_at_quarter") + 1
                    tasks_to_update.append(ripple_tasks)
                else:
                    tasks_to_delete.append(ripple_task)

                if rd_objects_to_update:
                    DynamicRD.objects.bulk_update(rd_objects_to_update, ["time_spent_developing"])
                if tasks_to_update:
                    RippleTask.objects.bulk_update(tasks_to_update, ["run_at_quarter"])
                if tasks_to_delete:
                    RippleTask.objects.filter(id__in=[task.id for task in tasks_to_delete]).delete()

        return Response(status=status.HTTP_200_OK)
