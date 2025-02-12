from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool
from common.serializers import DecisionPoolSerializer
from common.views.exceptions import DuplicateDecisionError
from common.views.services import (
    get_db_record_select_prefetch_or_404,
    get_serializer_or_400,
)
from contracts.models import Contract, ContractAssignment
from contracts.serializers import (
    ContractAssignmentSerializer,
    ContractSerializer,
    ContractsOrderSerializer,
)
from people.models import Player
from rd.views.services import get_available_rd_dynamics_at_next_quarter


@extend_schema_view(
    get_contracts=extend_schema(
        tags=["Contracts"],
        responses=ContractSerializer(many=True),
    ),
    get_assigned_contracts=extend_schema(
        tags=["Contracts"],
        responses=ContractAssignmentSerializer(many=True),
    ),
    set_contracts_order=extend_schema(
        tags=["Contracts"],
        request=ContractsOrderSerializer,
    ),
    get_contracts_order=extend_schema(
        tags=["Contracts"],
        responses=ContractsOrderSerializer,
    ),
)
class ContractView(ViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = None

    class ENDPOINTS:
        GET_CONTRACTS = "contracts/get_contracts"
        GET_ASSIGNED_CONTRACTS = "contracts/get_assigned_contracts"
        SET_CONTRACTS_ORDER = "contracts/set_contracts_order"

    @action(detail=False, methods=["get"])
    def get_contracts(self, request: Request):
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        esg_index = team.state_variables.esg_index

        """
        get decisions for r&d
        if development_time - time_spent_developing <= 1 and started_at != 0
        or
        start decision was made for a product that has a development time of 1
        => show contracts

        development_duration - time_spent_developing <= 1 and started_at is not zero
        """
        dynamic_rd_objects = get_available_rd_dynamics_at_next_quarter(
            team=team, current_quarter=current_quarter
        )

        available_products_set = {
            dynamic_rd_object.category
            for dynamic_rd_object in dynamic_rd_objects
        }

        available_contracts = Contract.objects.filter(
            simulation_class=team.simulation_class,
            closure_quarter=current_quarter,
            minimum_esg_index__lte=esg_index,
            deliverable_product__in=available_products_set,
        )

        serialized_available_contracts = ContractSerializer(
            available_contracts, many=True
        )
        response = {
            "available_contracts": serialized_available_contracts.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def get_assigned_contracts(self, request: Request):
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        assigned_contracts = ContractAssignment.objects.filter(team=team)
        serialized_assigned_contracts = ContractAssignmentSerializer(
            assigned_contracts, many=True
        )
        response = {
            "assigned_contracts": serialized_assigned_contracts.data,
        }
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def set_contracts_order(self, request: Request):
        """Receives marketing_budget and contract_ids"""
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        json_body = self._get_contracts_order_json_body(request.data)

        decision = self._make_contracts_order_decision(
            player=player,
            team=team,
            current_quarter=current_quarter,
            json_body=json_body,
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"decision": serialized_decision.data}
        return Response(response, status=status.HTTP_200_OK)

    def _get_contracts_order_json_body(self, data):
        serializer = get_serializer_or_400(ContractsOrderSerializer, data)
        marketing_budget = serializer.validated_data["marketing_budget"]
        contract_ids = serializer.validated_data["contract_ids"]
        return {
            "marketing_budget": str(marketing_budget),
            "contract_ids": contract_ids,
        }

    def _make_contracts_order_decision(
        self, player, team, current_quarter, json_body
    ):
        try:
            decision = DecisionPool.objects.get(
                team=team,
                made_at_quarter=current_quarter,
                endpoint=self.ENDPOINTS.SET_CONTRACTS_ORDER,
            )
            if decision.json_body == json_body:
                raise DuplicateDecisionError(context={"json_body": json_body})
            decision.json_body = json_body
            decision.save()
        except DecisionPool.DoesNotExist:
            decision = DecisionPool.objects.create(
                player=player,
                team=team,
                made_at_quarter=current_quarter,
                endpoint=self.ENDPOINTS.SET_CONTRACTS_ORDER,
                json_body=json_body,
            )
        return decision

    @action(detail=False, methods=["get"])
    def get_contracts_order(self, request: Request):
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        decision = get_db_record_select_prefetch_or_404(
            DecisionPool,
            player=player,
            team=team,
            made_at_quarter=current_quarter,
            endpoint=self.ENDPOINTS.SET_CONTRACTS_ORDER,
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_200_OK)
