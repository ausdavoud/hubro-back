from decimal import Decimal

from django.db.models import Sum
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.views.services import get_db_record_select_prefetch_or_404
from finance.models import FinancialAccount, Transaction
from people.models import CustomUser, Player, Team
from reports.serializers import QuarterlyReportSerializer
from reports.views.services.cost_calculator import get_budgeted_cash_by_quarter


@extend_schema_view(
    get=extend_schema(tags=["Reports"], responses=QuarterlyReportSerializer)
)
class QuarterlyReportView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        """
        { quarter: data }
        {
            1:  {
                "revenue": Decimal,
                "gross_profit": Decimal,
                "gross_profit_margin": Decimal,
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
        quarterly_report_dict = {}
        for quarter in range(1, current_quarter):
            cash_financial_account = get_db_record_select_prefetch_or_404(
                FinancialAccount,
                team=team,
                name=FinancialAccount.AccountCodes.CASH,
            )
            revenue = Transaction.objects.filter(
                team=team,
                quarter=quarter,
                category=Transaction.Categories.SALES,
                financial_account=cash_financial_account,
            ).aggregate(total=Sum("debit_amount"))["total"] or Decimal("0")
            gross_profit = get_budgeted_cash_by_quarter(team, quarter)

            gross_profit_margin = (
                gross_profit / revenue * 100 if revenue else 0
            )

            quarterly_report_dict[quarter] = {
                "revenue": revenue,
                "gross_profit": gross_profit,
                "gross_profit_margin": gross_profit_margin,
            }
        response = {"data": quarterly_report_dict}
        return Response(data=response, status=status.HTTP_200_OK)
