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
from common.views.services import get_db_record_select_prefetch_or_404, get_serializer_or_400
from finance.models import Loan
from finance.serializer import LoanSerializer, NewLoanSerializer, TransactionSerializer
from people.models import CustomUser, Player, Team


@extend_schema_view(
    new_loan=extend_schema(tags=["Finance"], request=NewLoanSerializer),
    cancel_loan=extend_schema(tags=["Finance"]),
    get_loans=extend_schema(tags=["Finance"], responses=LoanSerializer(many=True)),
)
class FinanceView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = None

    class ENDPOINTS:
        NEW_LOAN = "finance/new_loan"
        CANCEL_LOAN = "finance/cancel_loan"
        GET_LOANS = "finance/get_loans"

    @action(methods=["get"], detail=False)
    def get_loans(self, request):
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user, prefetch_related_tables=["decision_pool"])
        team = player.team
        current_quarter = team.state_variables.quarter
        loans = Loan.objects.filter(team=team)
        serialized_loans = LoanSerializer(loans, many=True)
        decisions = team.decision_pool.filter(
            team=team, endpoint=FinanceView.ENDPOINTS.NEW_LOAN, made_at_quarter=current_quarter
        )
        serialized_decisions = DecisionPoolSerializer(decisions, many=True)
                # Include decisions inside the response
        serialized_json_body = []
        for loan in serialized_decisions.data:
            loan["json_body"]["is_new"] = True
            loan["json_body"]["issued_quarter"] = loan["made_at_quarter"]
            serialized_json_body.append(loan["json_body"])
        serialized_loans = serialized_json_body + serialized_loans.data
        response = {
            "loans": serialized_loans,
        }
        return Response(response, status=status.HTTP_200_OK)

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

    def _create_decision(
        self, player: Player, team: Team, current_quarter: int, endpoint: str, json_body
    ) -> DecisionPool:
        """Create a new decision in the DecisionPool.\n
        We do not use get_or_create here because the user may ask for a loan with
        different amount or payback period (namely a different json body) and yet
        they should not be able to make a new decision. (one loan per quarter policy)
        """

        decision, created = DecisionPool.objects.get_or_create(
            team=team,
            made_at_quarter=current_quarter,
            endpoint=endpoint,
            defaults={"player": player, "json_body": json_body},
        )
        serialized_decision = DecisionPoolSerializer(decision)
        if not created:
            raise common_exceptions.DuplicateDecisionError(context={"decision": serialized_decision.data})
        return decision

    def _delete_loan_decision(self, team: Team, current_quarter: int) -> dict:
        """Delete the loan application made at this quarter from the DecisionPool."""

        try:
            decision = DecisionPool.objects.get(
                team=team, made_at_quarter=current_quarter, endpoint=self.ENDPOINTS.NEW_LOAN
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
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter: int = team.state_variables.quarter
        json_body = self._get_json_body(request.data)

        decision = self._create_decision(
            player=player,
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.NEW_LOAN,
            json_body=json_body,
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_201_CREATED)

    @action(methods=["post"], detail=False)
    def cancel_loan(self, request):
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter: int = team.state_variables.quarter

        serialized_deleted_decision = self._delete_loan_decision(team=team, current_quarter=current_quarter)
        response = {
            "data": {"message": "Loan application cancelled successfully", "canceled_loan": serialized_deleted_decision}
        }
        return Response(response, status=status.HTTP_200_OK)


@extend_schema_view(get_transactions=extend_schema(tags=["Finance"], responses=TransactionSerializer(many=True)))
class TransactionView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = None

    @action(methods=["get"], detail=False)
    def get_transactions(self, request):
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team: Team = get_db_record_select_prefetch_or_404(Team, prefetch_related_tables=["rd"], id=player.team_id)
        transactions = team.transactions.all()
        serialized_transactions = TransactionSerializer(transactions, many=True)
        response = {"data": serialized_transactions.data}
        return Response(response, status=status.HTTP_200_OK)
