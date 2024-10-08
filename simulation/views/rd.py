from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ..models.people import Player
from ..models.rd import RDStatic
from ..serializers.rd import RDProductSerializer, RDStaticSerializer, RDUpgradeSerializer


class RDAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def get(self, request: Request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        all_rd_data = []

        static_rd_objects = RDStatic.objects.all()
        for static_obj in static_rd_objects:
            rd_product_obj = static_obj.get_product(player=player)
            rd_upgrade_obj = static_obj.get_upgrade(player=player)

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

    def post(self, request: Request):
        pass
        # is it product or upgrade

        # product creation

        # upgrade creation: has updated_product or not?

        # create ripple task to increment development time by 1
