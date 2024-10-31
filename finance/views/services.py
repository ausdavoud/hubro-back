from decimal import Decimal

from django.db import IntegrityError, transaction
from rest_framework.response import Response
from ahmad.financials import (
    calculate_interest,
    calculate_payback_per_quarter,
)

from finance.models import FinancialAccount, Loan, Transaction
from finance.serializer import LoanSerializer, TransactionSerializer
from people.models import Player
from common.views import exceptions as common_exceptions


def new_loan(player: Player, json_body: dict) -> Response:
    """Create a new loan for the player."""

    current_quarter = player.state_variables.quarter
    fixed_interest = player.state_variables.fixed_interest
    simulation_duration = player.state_variables.simulation_duration
    esg_index = player.state_variables.esg_index

    amount_str = json_body["amount"]
    amount_decimal = Decimal(amount_str)
    payback_period = json_body["payback_period"]

    try:
        long_term_notes_payable = FinancialAccount.objects.get(
            name=FinancialAccount.AccountNames.LONG_TERM_NOTES_PAYABLE, type=FinancialAccount.AccountTypes.CREDIT
        )
    except FinancialAccount.DoesNotExist:
        raise common_exceptions.DatabaseRecordNotFound(FinancialAccount, {"Account Name": "Long term notes payable"})
    try:
        cash = FinancialAccount.objects.get(
            name=FinancialAccount.AccountNames.CASH, type=FinancialAccount.AccountTypes.DEBIT
        )
    except FinancialAccount.DoesNotExist:
        raise common_exceptions.DatabaseRecordNotFound(FinancialAccount, {"Account Name": "Cash"})

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
                player=player,
                amount=amount_decimal,
                issued_quarter=current_quarter,
                interest=interest,
                payback_period=payback_period,
                total_payback=total_payback,
                payback_per_quarter=payback_per_quarter,
            )
            credit_transaction = Transaction.objects.create(
                player=player,
                category=Transaction.Categories.NEW_LOANS,
                quarter=current_quarter,
                debit_amount=0,
                credit_amount=amount_decimal,
                financial_account=long_term_notes_payable,
            )
            debit_transaction = Transaction.objects.create(
                player=player,
                category=Transaction.Categories.NEW_LOANS,
                quarter=current_quarter,
                debit_amount=amount_decimal,
                credit_amount=0,
                financial_account=cash,
            )
    except IntegrityError:
        raise common_exceptions.AtomicTransactionError({"state": "new loan was not created"})

    serialized_loan = LoanSerializer(loan)
    serialized_credit_transaction = TransactionSerializer(credit_transaction)
    serialized_debit_transaction = TransactionSerializer(debit_transaction)

    return {
        "loan": serialized_loan.data,
        "credit_transaction": serialized_credit_transaction.data,
        "debit_transaction": serialized_debit_transaction.data,
    }
