from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication


from .services.ripple_tasks import increment_rd_dev_time
from ..models.common import RippleTask
from ..models.people import CustomUser, Player
from .exceptions import common as common_exceptions


@extend_schema_view(post=extend_schema(tags=["Finish Quarter"]))
class QuarterFinish(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def post(self, request: Request) -> Response:
        # Get player
        user: CustomUser = request.user
        try:
            player = Player.objects.prefetch_related("rd", "state_variables", "ripple_tasks").get(user=user)
        except Player.DoesNotExist:
            context = {"user_email": user.email}
            raise common_exceptions.DatabaseRecordNotFound(Player, context)

        # TODO: Implement pre-quarter-finish logic

        # Increment quarter
        player.state_variables.quarter += 1
        player.state_variables.save()
        print(f"Incremented quarter to {player.state_variables.quarter} for {user.email}")

        # Do ripple tasks
        ripple_tasks: list[RippleTask] = player.ripple_tasks.filter(run_at_quarter=player.state_variables.quarter)
        for ripple_task in ripple_tasks:
            if ripple_task.run_at_quarter != player.state_variables.quarter:
                continue

            if ripple_task.type == RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME:
                # Increment the development time of all R&D items
                incremented_dynamic_rd_item = increment_rd_dev_time(ripple_task.rd_object)
                ripple_task.delete()
                if ripple_task.rd_object.is_researching:
                    # Create a ripple task to increment the development time of the R&D item again
                    # after the next quarter
                    ripple_task = RippleTask.objects.create(
                        player=player,
                        run_at_quarter=player.state_variables.quarter + 1,
                        type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
                        rd_object=incremented_dynamic_rd_item,
                    )
                print(f"Incremented development time of {incremented_dynamic_rd_item.title} for {user.email}")

        return Response(status=status.HTTP_200_OK)
