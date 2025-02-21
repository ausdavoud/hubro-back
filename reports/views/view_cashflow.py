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
from contracts.views.views import ContractView
from finance.models import FinancialAccount, Transaction
from finance.views.views import FinanceView
from people.models import CustomUser, Player, Team
from production.views.services import factories
from production.views.views import ProductionView
from rd.models import DynamicRD
from rd.views.views import RDView
from reports.views.exceptions import InvalidQuarter


@extend_schema_view(get=extend_schema(tags=["Reports"]))
class CashFlowReportView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request, quarter: int) -> Response:
        """
        Current Quarter:
        {
            "operating_activities":
                RippleTask.type["maintenance"].maintenance_cost
            "investing_activities":
                Decision.R&D.cost
                Factory.cost
            "financing":
                Decision.Finance.NewLoan
                RippleTask.LoanRepayment
        }

        Past Quarters:
        {
            "operating_activities":
                Transaction.type["maintenance"].credit["cash"].debit["maintenance"]
            "investing_activities":
                Transaction.type["R&D"]
                Transaction.type["Factory"]
            "financing":
                Transaction.type["Loan"]
                Transaction.type["LoanRepayment"]
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
        if quarter > current_quarter or quarter < 1:
            raise InvalidQuarter()

        # Operating Activities
        operating_activities = self._operating_activities(
            team=team,
            requested_quarter=quarter,
            current_quarter=current_quarter,
        )
        # Investing Activities
        investing_activities = self._investing_activities(
            team=team,
            requested_quarter=quarter,
            current_quarter=current_quarter,
        )
        # Financing
        financing_activities = self._financing_activities(
            team=team,
            requested_quarter=quarter,
            current_quarter=current_quarter,
        )

        response = {
            "data": {
                "operating_activities": operating_activities,
                "investing_activities": investing_activities,
                "financing": financing_activities,
            }
        }
        return Response(response, status=status.HTTP_200_OK)

    def _operating_activities(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        operating_activities = 0
        if requested_quarter == current_quarter:
            maintenance_ripple_tasks = RippleTask.objects.filter(
                team=team,
                type=RippleTask.TaskTypes.FACTORY_MAINTENANCE,
                run_at_quarter=requested_quarter,
            )
            maintenance_cost = sum(
                task.json_body["maintenance_cost"]
                for task in maintenance_ripple_tasks
            )
            operating_activities += maintenance_cost

            marketing_budget = DecisionPool.objects.filter(
                team=team,
                made_at_quarter=requested_quarter,
                endpoint=ContractView.ENDPOINTS.SET_CONTRACTS_ORDER,
            )
            marketing_budget = sum(
                decision.json_body["marketing_budget"]
                for decision in marketing_budget
            )
            operating_activities += marketing_budget
        if requested_quarter < current_quarter:
            cash_financial_account = get_db_record_select_prefetch_or_404(
                FinancialAccount, code=FinancialAccount.AccountCodes.CASH
            )
            maintenance_transactions = Transaction.objects.filter(
                team=team,
                quarter=requested_quarter,
                category=Transaction.Categories.MAINTENANCE,
                financial_account=cash_financial_account,
            )
            for transaction in maintenance_transactions:
                operating_activities += transaction.credit_amount

        return operating_activities

    def _investing_activities(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        investing_activities = 0

        ## RD
        rd_activities_cost = self._investing_activities_rd_activities(
            team=team,
            requested_quarter=requested_quarter,
            current_quarter=current_quarter,
        )

        ## Factory
        factory_activities_cost = (
            self._investing_activities_factory_activities(
                team=team,
                requested_quarter=requested_quarter,
                current_quarter=current_quarter,
            )
        )

        # Total
        investing_activities = -rd_activities_cost - factory_activities_cost

        return investing_activities

    def _investing_activities_rd_activities(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        rd_activities = 0
        if requested_quarter == current_quarter:
            rd_decisions = DecisionPool.objects.filter(
                team=team,
                made_at_quarter=requested_quarter,
                endpoint=RDView.ENDPOINTS.START_RD,
            )
            for rd_decision in rd_decisions:
                category = rd_decision.json_body["category"]
                order = rd_decision.json_body["order"]
                dynamic_rd: DynamicRD = get_db_record_select_prefetch_or_404(
                    DynamicRD, team=team, category=category, order=order
                )
                cost = dynamic_rd.development_cost
                rd_activities += cost

        if requested_quarter < current_quarter:
            cash_financial_account = get_db_record_select_prefetch_or_404(
                FinancialAccount, code=FinancialAccount.AccountCodes.CASH
            )
            rd_transactions = Transaction.objects.filter(
                team=team,
                quarter=requested_quarter,
                category=Transaction.Categories.RESEARCH_PROJECTS,
                financial_account=cash_financial_account,
            )
            rd_activities += sum(
                transaction.credit_amount for transaction in rd_transactions
            )

        return rd_activities

    def _investing_activities_factory_activities(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        factory_activities = 0
        if requested_quarter == current_quarter:
            factory_decisions = DecisionPool.objects.filter(
                team=team,
                made_at_quarter=requested_quarter,
                endpoint=ProductionView.ENDPOINTS.NEW_FACTORY,
            )
            for factory_decision in factory_decisions:
                ownership = factory_decision.json_body["ownership"]
                factory_activities += factories[ownership]["build_cost"]

        if requested_quarter < current_quarter:
            cash_financial_account = get_db_record_select_prefetch_or_404(
                FinancialAccount, code=FinancialAccount.AccountCodes.CASH
            )
            factory_transactions = Transaction.objects.filter(
                team=team,
                quarter=requested_quarter,
                category=Transaction.Categories.NEW_FACTORY,
                financial_account=cash_financial_account,
            )
            factory_activities += sum(
                transaction.credit_amount
                for transaction in factory_transactions
            )

        return factory_activities

    def _financing_activities(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        financing_activities = 0

        financing_activities += self._financing_activities_new_loan(
            team, requested_quarter, current_quarter
        )
        financing_activities -= self._financing_activities_loan_repayment(
            team, requested_quarter, current_quarter
        )

        return financing_activities

    def _financing_activities_new_loan(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        financing_activities = Decimal(0)
        if requested_quarter == current_quarter:
            ## New Loan
            new_loan_decisions = DecisionPool.objects.filter(
                team=team,
                made_at_quarter=requested_quarter,
                endpoint=FinanceView.ENDPOINTS.NEW_LOAN,
            )
            financing_activities += sum(
                Decimal(decision.json_body["amount"])
                for decision in new_loan_decisions
            )

        if requested_quarter < current_quarter:
            long_term_notes_payable_financial_account = (
                get_db_record_select_prefetch_or_404(
                    FinancialAccount,
                    code=FinancialAccount.AccountCodes.LONG_TERM_NOTES_PAYABLE,
                )
            )
            new_loan_transactions = Transaction.objects.filter(
                team=team,
                quarter=requested_quarter,
                category=Transaction.Categories.NEW_LOANS,
                financial_account=long_term_notes_payable_financial_account,
            )
            financing_activities += sum(
                transaction.credit_amount
                for transaction in new_loan_transactions
            )

        return financing_activities

    def _financing_activities_loan_repayment(
        self, team: Team, requested_quarter: int, current_quarter: int
    ):
        financing_activities = 0
        if requested_quarter == current_quarter:
            ## Loan Repayment
            loan_repayment_ripple_tasks = RippleTask.objects.filter(
                team=team,
                type=RippleTask.TaskTypes.LOAN_REPAYMENT,
                run_at_quarter=requested_quarter,
            )
            financing_activities += sum(
                task.json_body["amount"]
                for task in loan_repayment_ripple_tasks
            )

        if requested_quarter < current_quarter:
            long_term_notes_payable_financial_account = (
                get_db_record_select_prefetch_or_404(
                    FinancialAccount,
                    code=FinancialAccount.AccountCodes.LONG_TERM_NOTES_PAYABLE,
                )
            )
            current_portion_transactions = Transaction.objects.filter(
                team=team,
                quarter=requested_quarter,
                category=Transaction.Categories.CURRENT_PORTION_OF_LOANS,
                financial_account=long_term_notes_payable_financial_account,
            )
            financing_activities += sum(
                transaction.debit_amount
                for transaction in current_portion_transactions
            )

            loan_repayment_transactions = Transaction.objects.filter(
                team=team,
                quarter=requested_quarter,
                category=Transaction.Categories.LOAN_REPAYMENT,
                financial_account=long_term_notes_payable_financial_account,
            )
            financing_activities += sum(
                transaction.debit_amount
                for transaction in loan_repayment_transactions
            )

        return financing_activities
