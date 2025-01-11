from decimal import Decimal

from django.db import DatabaseError, transaction
from rest_framework.response import Response

from ahmad.financials import (
    calculate_interest,
    calculate_payback_per_quarter,
)
from common.models import DecisionPool
from common.views import exceptions as common_exceptions
from finance.models import FinancialAccount, Loan, Transaction
from finance.serializer import LoanSerializer, TransactionSerializer
from people.models import Team


def get_financial_account_or_404(account_name: str):
    try:
        return FinancialAccount.objects.get(name=account_name)
    except FinancialAccount.DoesNotExist:
        raise common_exceptions.DatabaseRecordNotFound(f"Account {account_name} does not exist")


def new_loan(team: Team, decision: DecisionPool) -> Response:
    """Create a new loan for the team."""

    json_body = decision.json_body
    current_quarter = decision.made_at_quarter
    fixed_interest = team.state_variables.fixed_interest
    simulation_duration = team.state_variables.simulation_duration
    esg_index = team.state_variables.esg_index

    amount_str = json_body["amount"]
    amount_decimal = Decimal(amount_str)
    payback_period = json_body["payback_period"]

    long_term_notes_payable_account = get_financial_account_or_404(
        account_name=FinancialAccount.AccountNames.LONG_TERM_NOTES_PAYABLE
    )
    cash_account = get_financial_account_or_404(account_name=FinancialAccount.AccountNames.CASH)

    try:
        with transaction.atomic():
            interest = calculate_interest(
                payback_period=payback_period,
                esg_index=esg_index,
                simulation_duration=simulation_duration,
                current_quarter=current_quarter,
            )
            payback_per_quarter = calculate_payback_per_quarter(
                payback_period=payback_period, interest=interest, amount=amount_decimal
            )
            total_payback = payback_per_quarter * payback_period

            loan = Loan.objects.create(
                team=team,
                amount=amount_decimal,
                issued_quarter=current_quarter,
                interest=interest,
                payback_period=payback_period,
                total_payback=total_payback,
                payback_per_quarter=payback_per_quarter,
            )
            credit_transaction = Transaction.objects.create(
                team=team,
                category=Transaction.Categories.NEW_LOANS,
                quarter=current_quarter,
                debit_amount=0,
                credit_amount=amount_decimal,
                financial_account=long_term_notes_payable_account,
            )
            debit_transaction = Transaction.objects.create(
                team=team,
                category=Transaction.Categories.NEW_LOANS,
                quarter=current_quarter,
                debit_amount=amount_decimal,
                credit_amount=0,
                financial_account=cash_account,
            )
    except DatabaseError:
        raise common_exceptions.AtomicTransactionError(state="Error at making a loan object")

    serialized_loan = LoanSerializer(loan)
    serialized_credit_transaction = TransactionSerializer(credit_transaction)
    serialized_debit_transaction = TransactionSerializer(debit_transaction)

    return {
        "loan": serialized_loan.data,
        "credit_transaction": serialized_credit_transaction.data,
        "debit_transaction": serialized_debit_transaction.data,
    }
