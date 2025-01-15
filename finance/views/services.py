from decimal import Decimal

from django.db import DatabaseError, transaction
from rest_framework.response import Response

from ahmad.financials import (
    calculate_interest,
    calculate_payback_per_quarter,
)
from common.models import DecisionPool, RippleTask
from common.views import exceptions as common_exceptions
from common.views.services import get_db_record_select_prefetch_or_404
from finance.models import FinancialAccount, Loan, Transaction
from finance.serializer import LoanSerializer, TransactionSerializer
from people.models import Team


def create_transaction(
    team: Team,
    quarter: int,
    amount: Decimal,
    category: str,
    debit_account: FinancialAccount,
    credit_account: FinancialAccount,
):
    try:
        with transaction.atomic():
            debit_transaction = Transaction.objects.create(
                team=team,
                category=category,
                quarter=quarter,
                debit_amount=amount,
                credit_amount=0,
                financial_account=debit_account,
            )
            credit_transaction = Transaction.objects.create(
                team=team,
                category=category,
                quarter=quarter,
                debit_amount=0,
                credit_amount=amount,
                financial_account=credit_account,
            )
            return debit_transaction, credit_transaction
    except DatabaseError:
        raise common_exceptions.AtomicTransactionError(state="Error at making a financial transaction.")


def new_loan(team: Team, decision: DecisionPool) -> Response:
    """Create a new loan for the team."""

    json_body = decision.json_body
    current_quarter = decision.made_at_quarter
    fixed_interest = team.state_variables.fixed_interest
    simulation_duration = team.state_variables.simulation_duration
    esg_index = team.state_variables.esg_index

    amount_str = json_body["amount"]
    amount_decimal = Decimal(amount_str)
    payback_period = int(json_body["payback_period"])

    long_term_notes_payable_account = get_db_record_select_prefetch_or_404(FinancialAccount,
        code=FinancialAccount.AccountNames.LONG_TERM_NOTES_PAYABLE
    )
    cash_account = get_db_record_select_prefetch_or_404(FinancialAccount, code=FinancialAccount.AccountNames.CASH)

    try:
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
        with transaction.atomic():
            loan = Loan.objects.create(
                team=team,
                amount=amount_decimal,
                issued_quarter=current_quarter,
                interest=interest,
                payback_period=payback_period,
                total_payback=total_payback,
                payback_per_quarter=payback_per_quarter,
            )
            credit_transaction, debit_transaction = create_transaction(
                team=team,
                quarter=current_quarter,
                category=Transaction.Categories.NEW_LOANS,
                amount=amount_decimal,
                debit_account=long_term_notes_payable_account,
                credit_account=cash_account,
            )
            repayment_ripple_task = RippleTask.objects.create(
                team=team,
                run_at_quarter=current_quarter,
                type=RippleTask.TaskTypes.LOAN_REPAYMENT,
                json_body={
                    "amount": str(payback_per_quarter),
                    "quarters_to_pay": payback_period,
                    "quarters_paid": 0,
                },
            )
            interest_ripple_task = RippleTask.objects.create(
                team=team,
                run_at_quarter=current_quarter,
                type=RippleTask.TaskTypes.LOAN_INTEREST,
                json_body={
                    "amount": str(interest),
                    "quarters_to_pay": payback_period,
                    "quarters_paid": 0,
                },
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
