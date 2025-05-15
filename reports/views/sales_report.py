from collections import defaultdict
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from common.views.services import get_db_record_select_prefetch_or_404
from contracts.models import Contract, ContractAssignment
from people.models import CustomUser, Player, Team
from production.models import Production
from rd.models import DynamicRD
from reports.serializers import QuarterlyReportSerializer


@extend_schema_view(
    get=extend_schema(tags=["Reports"], responses=QuarterlyReportSerializer)
)
class SalesReportView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        """
        {
            product_id: {
                price: ...
                unit_cost: ...
                contribution_margin: ...
                revenue: ...
                material cost: ...
                labor cost: ...
                profit: ...
            }
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
        response = {"data": defaultdict(dict)}
        for quarter in range(1, current_quarter):
            # find all fulfilled contracts whose payment was due previous quarters:
            assigned_contracts = ContractAssignment.objects.filter(
                team=team,
                status=ContractAssignment.Statuses.FULFILLED,
                contract__payment_quarter__lt=quarter,
            )
            for assigned in assigned_contracts:
                info = {
                    "price": 0,
                    "unit_cost": 0,
                    "contribution_margin": 0,
                    "revenue": 0,
                    "material_cost": 0,
                    "labour_cost": 0,
                    "profit": 0,
                }
                # find the factories building that product in the contract
                contract: Contract = assigned.contract
                product: DynamicRD = get_db_record_select_prefetch_or_404(
                    DynamicRD,
                    team=team,
                    category=contract.deliverable_product,
                    order=1,
                )
                # find the factory building the product
                productions = Production.objects.filter(
                    team=team, quarter=quarter, product=product
                )
                if not productions:
                    continue
                quantity = 0
                for production in productions:
                    quantity += production.produced_quantity
                    info["labour_cost"] += production.labor_cost

                info["price"] = contract.unit_price
                info["material_cost"] = product.supplier.price
                info["unit_cost"] += (
                    info["material_cost"] + info["labour_cost"]
                )
                info["contribution_margin"] = info["price"] - info["unit_cost"]
                info["profit"] = info["contribution_margin"] * quantity
                info["revenue"] = info["price"] * quantity
                info["material_cost"] *= quantity
                info["labour_cost"] *= quantity
                response["data"][quarter][product.pk] = info
        return Response(response, status=status.HTTP_200_OK)
