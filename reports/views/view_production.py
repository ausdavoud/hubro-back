from decimal import Decimal

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool, RippleTask
from common.views.services import get_db_record_select_prefetch_or_404
from contracts.models import ContractAssignment
from people.models import CustomUser, Player, Team
from production.models import Factory, Storage
from production.views.views import ProductionView
from rd.models import DynamicRD
from reports.serializers import (
    ProductionReportErrorSerializer,
    ProductionReportSerializer,
)


@extend_schema_view(
    get=extend_schema(tags=["Reports"], responses=ProductionReportSerializer)
)
class ProductionReportView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request, factory_id: int) -> Response:
        """
        return the whole table, not giving a damn about the fact
        that it can be calculated in the frontend
        returns ->
        {
            materials: produced quantity of each factory * supplier cost
            labor cost OR outsourcing fee per unit: f(x) = 47.05(x / 100) + 14.79
            variable costs: sum of above, no need to send
            fixed cost: maintenance cost / units produced, in a way that it sums
            total: variable + fixed
        }
        """
        user: CustomUser = request.user
        player: Player = get_db_record_select_prefetch_or_404(
            Player, user=user
        )
        team: Team = get_db_record_select_prefetch_or_404(
            Team, prefetch_related_tables=["rd"], id=player.team_id
        )
        current_quarter: int = team.simulation_class.current_quarter

        factory: Factory = get_db_record_select_prefetch_or_404(
            Factory, id=factory_id, team=team
        )
        selected_product_decision = DecisionPool.objects.filter(
            team=team,
            made_at_quarter=current_quarter,
            endpoint=ProductionView.ENDPOINTS.SELECT_PRODUCT,
            json_body__factory_id=factory_id,
        )
        if not selected_product_decision:
            response = {
                "data": {
                    "fixed_cost_total": factory.maintenance_cost_per_quarter
                },
                "error": "No product was selected for this factory",
            }
            serialized_response = ProductionReportErrorSerializer(
                data=response
            )
            return Response(
                serialized_response.data, status=status.HTTP_400_BAD_REQUEST
            )

        selected_rd_product: DynamicRD = get_db_record_select_prefetch_or_404(
            DynamicRD,
            team=team,
            id=selected_product_decision.first().json_body["product_id"],
        )
        product_category = selected_rd_product.category
        product_alias = selected_rd_product.alias

        activity_level_decision = DecisionPool.objects.filter(
            team=team,
            made_at_quarter=current_quarter,
            endpoint=ProductionView.ENDPOINTS.SET_ACTIVITY_LEVEL,
            json_body__factory_id=factory_id,
        )
        activity_level = 100
        if activity_level_decision.exists():
            activity_level = float(
                activity_level_decision.first().json_body["activity_level"]
            )

        produced_quantity = activity_level * factory.base
        material_cost_per_unit = selected_rd_product.supplier.price
        material_cost_total = material_cost_per_unit * produced_quantity
        labor_cost_per_unit = 0
        labor_cost_total = 0
        outsourcing_fee_per_unit = 0
        outsourcing_fee_total = 0
        if factory.ownership == Factory.OwnershipTypes.OWNED:
            labor_cost_per_unit = 47.05 * (activity_level / 100) + 14.79
            labor_cost_total = labor_cost_per_unit * produced_quantity
        elif factory.ownership == Factory.OwnershipTypes.RENTED:
            outsourcing_fee_per_unit = 47.05 * (activity_level / 100) + 14.79
            outsourcing_fee_total = (
                outsourcing_fee_per_unit * produced_quantity
            )
        variable_costs_per_unit = (
            material_cost_per_unit
            + labor_cost_per_unit
            + outsourcing_fee_per_unit
        )
        variable_costs_total = (
            material_cost_total + labor_cost_total + outsourcing_fee_total
        )
        fixed_cost_per_unit = factory.maintenance_cost_per_quarter / Decimal(
            produced_quantity
        )
        fixed_cost_total = factory.maintenance_cost_per_quarter
        total_cost_per_unit = (
            Decimal(variable_costs_per_unit) + fixed_cost_per_unit
        )
        total_cost_total = Decimal(variable_costs_total) + fixed_cost_total

        # Depreciation
        depreciation_ripple_task = RippleTask.objects.filter(
            team=team, type=RippleTask.TaskTypes.FACTORY_DEPRECIATION
        ).first()
        factory_current_value = factory.build_cost
        depreciation_this_quarter = 0
        if depreciation_ripple_task:
            if depreciation_ripple_task.run_at_quarter == current_quarter:
                depreciation_this_quarter = depreciation_ripple_task.json_body[
                    "depreciation_cost"
                ]

            factory_current_value -= Decimal(
                depreciation_ripple_task.json_body["depreciation_cost"]
            ) * Decimal(depreciation_ripple_task.json_body["quarters_paid"])

        # storage
        storage = Storage.objects.filter(
            team=team, product=selected_rd_product
        ).first()
        stored_quantity = 0
        if storage:
            stored_quantity = storage.quantity

        # These are used at the production home page
        materials_emission_total = (
            selected_rd_product.supplier.emission * produced_quantity
        )
        production_emission_total = factory.emissions_per_unit * Decimal(
            produced_quantity
        )
        total_emission = (
            Decimal(materials_emission_total) + production_emission_total
        )

        # Demand
        assigned_contracts = ContractAssignment.objects.filter(
            team=team, contract__closure_quarter=current_quarter - 1
        )

        total_demand = (
            sum(
                [contract.contract.quantity for contract in assigned_contracts]
            )
            if assigned_contracts
            else 0
        )
        response = {
            "data": {
                "product_category": product_category,
                "product_alias": product_alias,
                "produced_quantity": produced_quantity,
                "material_cost_per_unit": material_cost_per_unit,
                "material_cost_total": material_cost_total,
                "labor_cost_per_unit": labor_cost_per_unit,
                "labor_cost_total": labor_cost_total,
                "outsourcing_fee_per_unit": outsourcing_fee_per_unit,
                "outsourcing_fee_total": outsourcing_fee_total,
                "variable_costs_per_unit": variable_costs_per_unit,
                "variable_costs_total": variable_costs_total,
                "fixed_cost_per_unit": fixed_cost_per_unit,
                "fixed_cost_total": fixed_cost_total,
                "total_cost_per_unit": total_cost_per_unit,
                "total_cost_total": total_cost_total,
                "depreciation_this_quarter": depreciation_this_quarter,
                "factory_current_value": factory_current_value,
                "stored_quantity": stored_quantity,
                "materials_emission_total": materials_emission_total,
                "production_emission_total": production_emission_total,
                "total_emission": total_emission,
                "total_demand": total_demand,
            }
        }
        serialized_response = ProductionReportSerializer(data=response)
        return Response(serialized_response.data, status=status.HTTP_200_OK)
