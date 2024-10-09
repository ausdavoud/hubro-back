from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Prefetch

from simulation.models.common import StateVariable

from ..models.people import CustomUser, Player
from ..models.rd import RDProduct, RDStates, RDStatic, RDUpgrade
from ..serializers.rd import (
    CreateRDProductSerializer,
    CreateRDUpgradeSerializer,
    RDProductSerializer,
    RDStaticSerializer,
    RDUpgradeSerializer,
)


class RDAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def get(self, request: Request):
        user = request.user
        player = get_object_or_404(Player, user=user)
        all_rd_data = []

        products = Prefetch("products", queryset=RDProduct.objects.filter(player=player))
        upgrades = Prefetch("upgrades", queryset=RDUpgrade.objects.filter(player=player))
        static_rd_objects = RDStatic.objects.prefetch_related(products).prefetch_related(upgrades)

        for static_obj in static_rd_objects:
            rd_product_obj = static_obj.products.first()
            rd_upgrade_obj = static_obj.upgrades.first()

            if not rd_product_obj and not rd_upgrade_obj:
                context = {"player": player}
                rd_static_data = RDStaticSerializer(static_obj, context=context).data
                all_rd_data.append(rd_static_data)

            elif static_obj.type == RDStatic.RDTypes.PRODUCT:
                rd_product_data = RDProductSerializer(rd_product_obj).data
                all_rd_data.append(rd_product_data)

            elif static_obj.type == RDStatic.RDTypes.UPGRADE:
                rd_upgrade_data = RDUpgradeSerializer(rd_upgrade_obj).data
                all_rd_data.append(rd_upgrade_data)

        return Response(all_rd_data, status=status.HTTP_200_OK)

    @extend_schema(request=CreateRDProductSerializer)
    def post(self, request: Request):
        user: CustomUser = request.user
        player = get_object_or_404(Player, user=user)

        # Validating category and order
        rd_serializer = CreateRDUpgradeSerializer(data=request.data)
        if not rd_serializer.is_valid():
            response = {"status": "error", "data": rd_serializer.errors}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        category = rd_serializer.validated_data["category"]
        order = rd_serializer.validated_data["order"]

        # Finding the static object for which the request has been sent
        static_obj = get_object_or_404(RDStatic, category=category, order=order)

        # Validating alias and icon_link only if the request is for a product
        if static_obj.type == RDStatic.RDTypes.PRODUCT:
            rd_serializer = CreateRDProductSerializer(data=request.data)
            if not rd_serializer.is_valid():
                response = {"status": "error", "data": rd_serializer.errors}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        alias = rd_serializer.validated_data.get("alias", "")
        icon_link = rd_serializer.validated_data.get("icon_link", "")
        current_quarter = StateVariable.get_player_quarter(player=player)

        # Check if the static object is available for development
        if static_obj.get_state(player) != RDStates.AVAILABLE:
            response = {
                "status": "error",
                "data": f"R&D Project '{static_obj.title}' is not available for development",
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Get or Create the RDProduct
        if static_obj.type == RDStatic.RDTypes.PRODUCT:
            rd_product_obj: RDProduct | None = static_obj.get_product(player=player)
            if rd_product_obj:
                response = {
                    "status": "error",
                    "data": f"R&D Product '{static_obj.title}' with alias {rd_product_obj.alias} already exists for {player.user.email}",
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                rd_product_obj = RDProduct.objects.create(
                    player=player, static=static_obj, started_at=current_quarter, alias=alias, icon_link=icon_link
                )
                rd_product_serializer = RDProductSerializer(rd_product_obj)
                response = {"status": "success", "data": rd_product_serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)

        # Get or Create the RDUpgrade
        elif static_obj.type == RDStatic.RDTypes.UPGRADE:
            rd_upgrade_obj = static_obj.get_upgrade(player=player)
            if rd_upgrade_obj:
                response = {
                    "status": "error",
                    "data": f"R&D Upgrade '{static_obj.title}' already exists for {player.user.email}",
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                rd_upgrade_obj: RDUpgrade
                # Production Upgrades don't need the `updated_product` field
                if static_obj.category == RDStatic.Categories.PRODUCTION:
                    rd_upgrade_obj = RDUpgrade.objects.create(
                        player=player, static=static_obj, started_at=current_quarter
                    )
                else:
                    # Find the first item of this category (e.g. Basic Jetpack)
                    product_of_category = get_object_or_404(
                        RDProduct, player=player, static__category=category, static__order=1
                    )
                    rd_upgrade_obj = RDUpgrade.objects.create(
                        player=player,
                        static=static_obj,
                        started_at=current_quarter,
                        updated_product=product_of_category,
                    )

                rd_upgrade_serializer = RDUpgradeSerializer(rd_upgrade_obj)
                response = {"status": "success", "data": rd_upgrade_serializer.data}
                return Response(response, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_200_OK)
