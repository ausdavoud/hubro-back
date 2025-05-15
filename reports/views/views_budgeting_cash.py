from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.views.services import get_db_record_select_prefetch_or_404
from people.models import CustomUser, Player, Team
from reports.views.services.cost_calculator import get_budgeted_cash_by_quarter


@extend_schema_view(get=extend_schema(tags=["Reports"]))
class BudgetCashReport(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request, quarter: int = 0) -> Response:
        user: CustomUser = request.user
        player: Player = get_db_record_select_prefetch_or_404(
            Player, user=user
        )
        team: Team = get_db_record_select_prefetch_or_404(
            Team, prefetch_related_tables=["rd"], id=player.team_id
        )
        current_quarter: int = team.simulation_class.current_quarter

        quarter = quarter if quarter else current_quarter
        if quarter > current_quarter:
            return Response(
                {"error": "You cannot get a report for a future quarter."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if quarter < 1:
            return Response(
                {
                    "error": "You cannot get a report for a quarter less than 1."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        budgeted_cash = get_budgeted_cash_by_quarter(
            team=team, quarter=quarter, current_quarter=current_quarter
        )
        return Response(
            {"quarter": quarter, "budgeted_cash": budgeted_cash},
            status=status.HTTP_200_OK,
        )
