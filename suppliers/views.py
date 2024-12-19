from django.db.models import BooleanField, Case, F, Value, When
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.views.exceptions import GameLogicError
from common.views.services import get_db_record_select_prefetch_or_404, get_serializer_or_400
from people.models import Player, Team
from rd.models import DynamicRD
from suppliers.exceptions import ForbiddenSupplierAssignmentError, InvalidCategoryError
from suppliers.models import Supplier
from suppliers.serializers import SetSupplierSerializer, SupplierSerializer


@extend_schema_view(
    get_suppliers=extend_schema(tags=["Suppliers"], responses=SupplierSerializer),
    set_supplier=extend_schema(tags=["Suppliers"], responses=int, request=SetSupplierSerializer),
)
class SuppliersView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = None

    class ENDPOINTS:
        GET_SUPPLIERS = "get_suppliers"
        SET_SUPPLIER = "set_supplier"

    @action(methods=["get"], detail=False, url_path=ENDPOINTS.GET_SUPPLIERS)
    def get_suppliers(self, request: Request) -> Response:
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team

        completed_dynamic_rd_objs_categories = self._get_completed_dynamic_rd_objs_categories(team=team)

        # get suppliers whose rd_category is in the categories of the completed_dynamic_rd_objs
        suppliers = Supplier.objects.filter(rd_category__in=completed_dynamic_rd_objs_categories)

        serialized_suppliers = SupplierSerializer(suppliers, many=True)
        response = {
            "suppliers": serialized_suppliers.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False, url_path=ENDPOINTS.SET_SUPPLIER)
    def set_supplier(self, request: Request) -> Response:
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        json_body = self._get_supplier_json_body(request.data)
        completed_categories = self._get_completed_dynamic_rd_objs_categories(team=team)

        category = json_body["rd_category"]
        supplier_id = json_body["supplier_id"]

        supplier: Supplier = get_db_record_select_prefetch_or_404(Supplier, id=supplier_id)

        if supplier.rd_category not in completed_categories:
            raise ForbiddenSupplierAssignmentError(category=category)

        if supplier.rd_category != category:
            raise InvalidCategoryError(supplier_id=supplier_id, category=category)

        updated_rds = DynamicRD.objects.filter(team=team, type=DynamicRD.RDTypes.PRODUCT, category=category).update(
            supplier=supplier
        )
        serialized_supplier_data = SupplierSerializer(supplier).data

        if updated_rds != 1:
            raise GameLogicError(f"Expected to update 1 DynamicRD object, but updated {updated_rds} instead")
        response = {"new_supplier": serialized_supplier_data}
        return Response(response, status=status.HTTP_200_OK)

    def _get_supplier_json_body(self, data: dict):
        serialized_data = get_serializer_or_400(SetSupplierSerializer, data)
        return serialized_data.validated_data

    def _get_completed_dynamic_rd_objs_categories(self, team: Team):
        # annotating is_completed. Refer to DynamicRD model properties at rd.models
        completed_dynamic_rd_objs_categories = (
            DynamicRD.objects.filter(team=team, type=DynamicRD.RDTypes.PRODUCT)
            .annotate(
                is_completed=Case(
                    When(
                        time_spent_developing=F("development_duration"),
                        started_at__gt=0,
                        time_spent_developing__gt=0,
                        then=Value(True),
                    ),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            .filter(is_completed=True)
            .values_list("category", flat=True)
        )

        return completed_dynamic_rd_objs_categories
