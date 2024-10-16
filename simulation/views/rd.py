from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models.common import RippleTask
from ..models.people import CustomUser
from ..models.rd import DynamicRD, StaticRD
from ..serializers.rd import BaseUpdateRDSerializer, DynamicRDSerializer, UpdateRDProductSerializer
from ..views.services.rd import start_rd_development
from .exceptions import rd as rd_exceptions
from .exceptions.rd import PauseRDError, ResumeRDError
from .services.common import get_player_or_404, get_serializer_or_400
from .services.rd import get_dynamic_rd_or_404, get_previous_rd_items
from .services.ripple_tasks import delete_dynamic_rd_ripple_task_or_404


@extend_schema_view(
    get_rds=extend_schema(tags=["R&D"]),
    start_rd=extend_schema(tags=["R&D"], request=BaseUpdateRDSerializer),
    pause_rd=extend_schema(tags=["R&D"], request=BaseUpdateRDSerializer),
    resume_rd=extend_schema(tags=["R&D"], request=BaseUpdateRDSerializer),
)
class RDView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(methods=["get"], detail=False)
    def get_rds(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user, ["rd", "state_variables"])

        current_quarter: int = player.state_variables.quarter
        dynamic_rd_objects: list[DynamicRD] | None = player.rd.all()

        previous_rd_items = get_previous_rd_items(dynamic_rd_objects)

        serialized_data = DynamicRDSerializer(
            dynamic_rd_objects,
            many=True,
            context={"current_quarter": current_quarter, "previous_rd_items": previous_rd_items},
        )

        response = {"data": serialized_data.data}
        return Response(
            response,
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False)
    def start_rd(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)

        # Validating category and order
        base_rd_serializer = get_serializer_or_400(BaseUpdateRDSerializer, request.data)
        category = base_rd_serializer.validated_data["category"]
        order = base_rd_serializer.validated_data["order"]

        # Finding the static object for which the request has been sent
        dynamic_rd_object = get_dynamic_rd_or_404(player, category=category, order=order)

        # Validating alias and icon_link only if the request is for a product
        if dynamic_rd_object.type == StaticRD.RDTypes.PRODUCT:
            product_rd_serializer = get_serializer_or_400(UpdateRDProductSerializer, request.data)
            dynamic_rd_object.alias = product_rd_serializer.validated_data.get("alias")
            dynamic_rd_object.icon_link = product_rd_serializer.validated_data.get("icon_link")

        serialized_dynamic_rd_object = start_rd_development(player, dynamic_rd_object=dynamic_rd_object)

        response = {"data": serialized_dynamic_rd_object.data}
        return Response(data=response, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def pause_rd(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)

        # Validating category and order
        base_rd_serializer = get_serializer_or_400(BaseUpdateRDSerializer, request.data)
        category = base_rd_serializer.validated_data["category"]
        order = base_rd_serializer.validated_data["order"]

        # Finding the static object for which the request has been sent
        dynamic_rd_object = get_dynamic_rd_or_404(player, category=category, order=order)
        if not dynamic_rd_object.is_researching:
            raise PauseRDError("R&D item is not being researched, so its research process cannot be paused")
        delete_response = delete_dynamic_rd_ripple_task_or_404(player, dynamic_rd_object)

        response = {"data": delete_response}
        return Response(data=response, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def resume_rd(self, request: Request):
        user: CustomUser = request.user
        player = get_player_or_404(user)

        # Validating category and order
        base_rd_serializer = get_serializer_or_400(BaseUpdateRDSerializer, request.data)
        category = base_rd_serializer.validated_data["category"]
        order = base_rd_serializer.validated_data["order"]

        # Finding the static object for which the request has been sent
        dynamic_rd_object = get_dynamic_rd_or_404(player, category=category, order=order)
        if not dynamic_rd_object.is_researching:
            raise rd_exceptions.ResumeRDError("The R&D item is not being researched at all, so it cannot be resumed")
        try:
            ripple_task: RippleTask = player.ripple_tasks.get(dynamic_rd_object=dynamic_rd_object)
            raise ResumeRDError("The R&D item is already being researched")
        except RippleTask.DoesNotExist:
            ripple_task = RippleTask.objects.create(
                player,
                run_at_quarter=player.state_variables.current_quarter,
                type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
                dynamic_rd_object=dynamic_rd_object,
            )
            response = {"data": {"description": "Auto increment ripple task was created successfully"}}
            return Response(response, status=status.HTTP_200_OK)
