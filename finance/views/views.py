from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool
from common.serializers import DecisionPoolSerializer
from common.views import exceptions as common_exceptions
from common.views.services import get_serializer_or_400
from finance.serializer import NewLoanSerializer
from people.models import CustomUser, Player
from people.views.services import get_player_or_404


@extend_schema_view(
    new_loan=extend_schema(tags=["Finance"], request=NewLoanSerializer),
    cancel_loan=extend_schema(tags=["Finance"]),
)
class FinanceView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    class ENDPOINTS:
        NEW_LOAN = "finance/new_loan"
        CANCEL_LOAN = "finance/cancel_loan"

    def _get_json_body(self, data) -> dict:
        """Using .validated_data instead of .data, converts `amount`
        to decimal and we can't encode decimal to json in order to
        save it inside DecisionPool.json_body"""
        serialized_data = get_serializer_or_400(NewLoanSerializer, data)
        amount = serialized_data.validated_data["amount"]
        payback_period = serialized_data.validated_data["payback_period"]

        json_body = {
            "amount": str(amount),
            "payback_period": str(payback_period),
        }

        return json_body

    def _create_decision(self, player: Player, current_quarter: int, endpoint: str, json_body) -> DecisionPool:
        """Create a new decision in the DecisionPool.\n
        We do not use get_or_create here because the user may ask for a loan with
        different amount or payback period (namely a different json body) and yet
        they should not be able to make a new decision. (one loan per quarter policy)
        """

        try:
            previous_decision = DecisionPool.objects.get(
                player=player, made_at_quarter=current_quarter, endpoint=endpoint
            )
            serialized_decision = DecisionPoolSerializer(previous_decision)
            raise common_exceptions.DuplicateDecision(context={"decision": serialized_decision.data})
        except DecisionPool.DoesNotExist:
            decision = DecisionPool.objects.create(
                player=player, made_at_quarter=current_quarter, endpoint=endpoint, json_body=json_body
            )
            return decision

    def _delete_loan_decision(self, player: Player, current_quarter: int) -> dict:
        """Delete the loan application made at this quarter from the DecisionPool."""

        try:
            decision = DecisionPool.objects.get(
                player=player, made_at_quarter=current_quarter, endpoint=self.ENDPOINTS.NEW_LOAN
            )
            serialized_decision = DecisionPoolSerializer(decision)
            serialized_decision_data = serialized_decision.data
            decision.delete()
            return serialized_decision_data
        except DecisionPool.DoesNotExist:
            raise common_exceptions.DatabaseRecordNotFound(DecisionPool, context={"endpoint": self.ENDPOINTS.NEW_LOAN})

    @action(methods=["post"], detail=False)
    def new_loan(self, request):
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter: int = player.state_variables.quarter
        json_body = self._get_json_body(request.data)

        decision = self._create_decision(
            player=player, current_quarter=current_quarter, endpoint=self.ENDPOINTS.NEW_LOAN, json_body=json_body
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=False)
    def cancel_loan(self, request):
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter: int = player.state_variables.quarter

        serialized_deleted_decision = self._delete_loan_decision(player=player, current_quarter=current_quarter)
        response = {
            "data": {"message": "Loan application cancelled successfully", "canceled_loan": serialized_deleted_decision}
        }
        return Response(response, status=status.HTTP_200_OK)
