from collections import defaultdict

from django.db.models import OuterRef, Subquery
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool
from common.views.services import get_db_record_select_prefetch_or_404
from contracts.models import ContractAssignment, ContractPriority
from people.models import CustomUser, Player, Team
from production.models import Factory, Storage
from production.views.views import ProductionView
from rd.models import DynamicRD


@extend_schema_view(get=extend_schema(tags=["Reports"]))
class MarketReportView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        """
        get assigned contracts
        get deliverable products
        get storage of each product
        order contracts by the user's desired order
        give product from total storage to each contract
        total storage =
            storage of this product
            + storage of this product in production

        Output = {
            contract 1:
                {
                    product: 1,
                    storage: 500,
                    desired: 500,
                },
            contract 2:
                {
                    product: 1,
                    storage: 100,
                    desired: 500
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
        current_quarter: int = team.state_variables.quarter

        # At current quarter, we produce products for contracts which have been
        # closed the previous quarter. So it must have been assigned to us
        # at the previous quarter as well.
        #
        # Having no seniors looking at your
        # project makes a lot of difficulties: Deciding at each step of the
        # project to do the best. It's like being an orphan, ofc in a much smaller
        # scale. Anyway...
        assigned_contracts = ContractAssignment.objects.filter(
            team=team, contract__closure_quarter=current_quarter - 1
        )
        deliverable_products = assigned_contracts.values_list(
            "contract__deliverable_product", flat=True
        )
        deliverable_products = list(set(deliverable_products))
        productions = defaultdict(float)
        print("FuUuuuúuuuuuuuuck")

        for deliverable_product in deliverable_products:
            # find rd object
            dynamic_rd = get_db_record_select_prefetch_or_404(
                DynamicRD, team=team, category=deliverable_product, order=1
            )
            # find factories producing it in decision
            factory_production_decisions = DecisionPool.objects.filter(
                team=team,
                endpoint=ProductionView.ENDPOINTS.SELECT_PRODUCT,
                json_body__product_id=dynamic_rd.pk,
            )
            factory_ids = factory_production_decisions.values_list(
                "json_body__factory_id", flat=True
            )

            for factory_id in factory_ids:
                factory: Factory = get_db_record_select_prefetch_or_404(
                    Factory, id=factory_id
                )
                # find activity level of those facts
                decision = DecisionPool.objects.filter(
                    team=team,
                    endpoint=ProductionView.ENDPOINTS.SET_ACTIVITY_LEVEL,
                    json_body__factory_id=factory_id,
                )
                if decision.exists():
                    activity_level = (
                        float(decision.last().json_body["activity_level"])
                        / 100
                    )
                else:
                    activity_level = 1
                # multiply activity level by factory base
                factory_base = factory.base
                factory_production = factory_base * activity_level
                productions[deliverable_product] += factory_production

            # find storage and sum it up
            storage = Storage.objects.filter(
                team=team, product=dynamic_rd
            ).first()
            if storage:
                productions[deliverable_product] += storage.quantity

        # find contracts
        # > assigned_contracts (fetched above)
        # order by priority
        print(productions)

        priority_qs = ContractPriority.objects.filter(
            team=team,
            contract=OuterRef("contract"),
            quarter=current_quarter,  # or another desired quarter value
        ).values("priority")[:1]

        assigned_contracts = (
            ContractAssignment.objects.filter(
                team=team, contract__closure_quarter=current_quarter - 1
            )
            .annotate(priority=Subquery(priority_qs))
            .order_by("priority")  # lower numbers come first
        )

        # fulfill contracts
        fulfillments = list()
        for assigned_contract in assigned_contracts:
            contract = assigned_contract.contract
            deliverable_product = contract.deliverable_product
            desired = contract.quantity
            storage = productions[deliverable_product]
            if storage >= desired:
                print(storage)
                productions[deliverable_product] -= desired
                fulfillments.append(
                    {
                        "contract_id": contract.pk,
                        "product": dynamic_rd.pk,
                        "storage": storage,
                        "desired": desired,
                    }
                )
                storage -= desired
                print(fulfillments)
            else:
                fulfillments.append(
                    {
                        "contract_id": contract.pk,
                        "product": dynamic_rd.pk,
                        "storage": storage,
                        "desired": desired,
                    }
                )
                productions[deliverable_product] = 0

        return Response({"data": fulfillments}, status=status.HTTP_200_OK)
