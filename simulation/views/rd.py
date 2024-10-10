from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..helper.rd import get_previous_rd_items
from ..models.common import RippleTask
from ..models.people import CustomUser, Player
from ..models.rd import DynamicRD, RDStates, StaticRD
from ..serializers.rd import BaseCreateRDSerializer, CreateRDProductSerializer, DynamicRDSerializer
from .error_codes.rd import RDErrorCodes


class RDAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def get(self, request: Request) -> Response:
        user = request.user
        try:
            player = Player.objects.prefetch_related("rd", "state_variables").get(user=user)
        except Player.DoesNotExist:
            response = {"error": RDErrorCodes.PLAYER_NOT_FOUND(user)}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        current_quarter = player.state_variables.quarter
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

    @extend_schema(request=CreateRDProductSerializer)
    def post(self, request: Request) -> Response:
        user: CustomUser = request.user

        try:
            player = Player.objects.prefetch_related("rd", "state_variables").get(user=user)
        except Player.DoesNotExist:
            response = {"error": RDErrorCodes.PLAYER_NOT_FOUND(user)}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Validating category and order
        base_rd_serializer = BaseCreateRDSerializer(data=request.data)
        if not base_rd_serializer.is_valid():
            response = {"error": RDErrorCodes.SERIALIZER_ERROR(base_rd_serializer.errors)}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        category = base_rd_serializer.validated_data["category"]
        order = base_rd_serializer.validated_data["order"]

        try:
            # Finding the static object for which the request has been sent
            dynamic_rd_object: DynamicRD = player.rd.get(category=category, order=order)
        except DynamicRD.DoesNotExist:
            response = {"error": RDErrorCodes.RD_NOT_FOUND(category, order)}
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        # Validating alias and icon_link only if the request is for a product
        if dynamic_rd_object.type == StaticRD.RDTypes.PRODUCT:
            product_rd_serializer = CreateRDProductSerializer(data=request.data)
            alias = product_rd_serializer.validated_data.get("alias")
            icon_link = product_rd_serializer.validated_data.get("icon_link")
            dynamic_rd_object.alias = alias
            dynamic_rd_object.icon_link = icon_link

            if not product_rd_serializer.is_valid():
                response = {"error": RDErrorCodes.SERIALIZER_ERROR(product_rd_serializer.errors)}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Check if the dynamic object is available for development,
        # since only available R&D items can be developed
        dynamic_rd_objects: list[DynamicRD] | None = player.rd.all()
        current_quarter = player.state_variables.quarter
        previous_rd_items = get_previous_rd_items(dynamic_rd_objects)
        state = dynamic_rd_object.get_state(current_quarter, previous_rd_items)
        if state != RDStates.AVAILABLE:
            response = {"error": RDErrorCodes.RD_STATE_ERROR(state)}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        dynamic_rd_object.started_at = current_quarter
        dynamic_rd_object.save()

        # Create ripple task to increase dev time at the end of the quarter
        ripple_task = RippleTask.objects.create(
            player=player,
            run_at_quarter=current_quarter + 1,
            type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
            rd_object=dynamic_rd_object,
        )

        serialized_response = DynamicRDSerializer(dynamic_rd_object)
        response = {"data": serialized_response.data}

        return Response(data=response, status=status.HTTP_201_CREATED)
