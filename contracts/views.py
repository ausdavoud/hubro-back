from pprint import pprint

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from ahmad.contracts import generate_contract_data
from common.management.data_fixtures import (
    BASIC_JETPACK_CONTRACT,
    GREEN_JETPACK_CONTRACT,
    SAFE_JETPACK_CONTRACT,
    SPORTY_JETPACK_CONTRACT,
)
from common.models import DecisionPool
from common.serializers import DecisionPoolSerializer
from common.views.exceptions import DuplicateDecisionError
from common.views.services import get_db_record_or_404, get_serializer_or_400
from contracts.models import Contract
from contracts.serializers import ContractSerializer, ContractsOrderSerializer
from people.views.services import get_player_or_404
from rd.models import DynamicRD, StaticRD


@extend_schema_view(
    get_contracts=extend_schema(
        tags=["Contracts"],
        responses=ContractSerializer(many=True),
    ),
    set_contracts_order=extend_schema(
        tags=["Contracts"],
        request=ContractsOrderSerializer,
    ),
)
class ContractViewSet(ViewSet):
    class ENDPOINTS:
        GET_CONTRACTS = "get_contracts"
        SET_CONTRACTS_ORDER = "set_contracts_order"

    @action(detail=False, methods=["get"])
    def get_contracts(self, request: Request):
        user = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter
        # New contracts should be Created when quarter is incremented
        # creating contracts:
        for JETPACK_CONTRACT in [
            BASIC_JETPACK_CONTRACT,
            SPORTY_JETPACK_CONTRACT,
            SAFE_JETPACK_CONTRACT,
            GREEN_JETPACK_CONTRACT,
        ]:
            if JETPACK_CONTRACT.get(current_quarter, None) is None:
                continue
            # Generate new contracts
            dynamic_rd_product: DynamicRD = get_db_record_or_404(
                DynamicRD, player=player, category=JETPACK_CONTRACT["product_type"], type=StaticRD.RDTypes.PRODUCT
            )
            contracts = generate_contract_data(
                current_quarter,
                JETPACK_CONTRACT[current_quarter]["product_demand"],
                JETPACK_CONTRACT[current_quarter]["contracts"],
                JETPACK_CONTRACT[current_quarter]["contract_price_start"],
                JETPACK_CONTRACT[current_quarter]["contract_price_end"],
                JETPACK_CONTRACT[current_quarter]["required_esg_index"],
                dynamic_rd_product,
            )
            # make a new key for each contract called "player" whose
            # value is the player
            for contract in contracts:
                contract["player"] = player

            pprint(contracts)
            return Response(data=contracts)

            Contract.objects.bulk_create()

        contracts = Contract.objects.filter(player=player, created_at_quarter=current_quarter)
        serialized_contracts = ContractSerializer(contracts, many=True)
        response = {"contracts": serialized_contracts.data}
        return response

    @action(detail=False, methods=["post"])
    def set_contracts_order(self, request: Request):
        """Receives marketing_budget and contract_ids"""
        user = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter
        json_body = self._get_contracts_order_json_body(request.data)

        decision = self._make_contracts_order_decision(
            player=player, current_quarter=current_quarter, json_body=json_body
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"decision": serialized_decision.data}
        return Response(response, status=status.HTTP_200_OK)

    def _get_contracts_order_json_body(self, data):
        serializer = get_serializer_or_400(ContractsOrderSerializer, data)
        marketing_budget = serializer.validated_data["marketing_budget"]
        contract_ids = serializer.validated_data["contract_ids"]
        return {"marketing_budget": str(marketing_budget), "contract_ids": contract_ids}

    def _make_contracts_order_decision(self, player, current_quarter, json_body):
        try:
            decision = DecisionPool.objects.get(
                player=player, made_at_quarter=current_quarter, endpoint=self.ENDPOINTS.SET_CONTRACTS_ORDER
            )
            if decision.json_body == json_body:
                raise DuplicateDecisionError(context={"json_body": json_body})
            decision.json_body = json_body
            decision.save()
        except DecisionPool.DoesNotExist:
            decision = DecisionPool.objects.create(
                player=player,
                made_at_quarter=current_quarter,
                endpoint=self.ENDPOINTS.SET_CONTRACTS_ORDER,
                json_body=json_body,
            )
        return decision
