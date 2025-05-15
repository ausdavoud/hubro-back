from collections import defaultdict

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.views.services import get_db_record_select_prefetch_or_404
from finance.models import Transaction
from finance.serializer import TransactionSerializer
from people.models import CustomUser, Player, Team
from reports.serializers import QuarterlyReportSerializer


@extend_schema_view(
    get=extend_schema(tags=["Reports"], responses=QuarterlyReportSerializer)
)
class TrialReportView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        """
        {
            (quarter as integer): {
                Financial Account Name: [Transactions]
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
        response = {"data": defaultdict(lambda: defaultdict(list))}
        for quarter in range(1, current_quarter):
            transactions = Transaction.objects.filter(quarter=quarter)
            for transaction in transactions:
                response["data"][quarter][
                    transaction.financial_account.code
                ].append(TransactionSerializer(transaction).data)

        return Response(response, status=status.HTTP_200_OK)
