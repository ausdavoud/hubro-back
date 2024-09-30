from django.db import models

from .people import Player
import uuid


class FinancialAccount(models.Model):
    class AccountNames(models.TextChoices):
        DEPRECIATION_OF_FACTORIES = "6030", "Depreciation of factories"
        FACTORIES = "1121", "Factories"
        AMORTIZATION = "6040", "Amortization"
        RESEARCHED_TECHNOLOGY = "1130", "Researched technology"
        DIRECT_LABOR = "5120", "Direct labor"
        DIRECT_RAW_MATERIALS = "5110", "Direct raw materials"
        FINISHED_GOODS_INVENTORY = "1720", "Finished goods inventory"
        STORAGE = "storage", "Storage"
        CASH = "1910", "Cash"
        CURRENT_PORTION_OF_LOANS_PAYABLE = (
            "current_portion_of_loans_payable",
            "Current portion of loans payable",
        )
        INTEREST_EXPENSES = "interest_expenses", "Interest expenses"
        MAINTENANCE = "5420", "Maintenance"
        PROMOTION = "5360", "Promotion"
        SALES = "4110", "Sales"
        OVERDRAFT = "overdraft", "Overdraft"
        LONG_TERM_NOTES_PAYABLE = "long_term_notes_payable", "Long term notes payable"
        RAW_MATERIAL_INVENTORY = "1710", "Raw material inventory"

    class AccountTypes(models.TextChoices):
        DEBIT = "DE", "Debit"
        CREDIT = "CR", "Credit"

    name = models.CharField(max_length=50, choices=AccountNames.choices)
    type = models.CharField(max_length=2, choices=AccountTypes.choices)


class Transaction(models.Model):
    class TransactionTypes(models.TextChoices):
        PAID = "PD", "Paid"
        RECEIVED = "RC", "Received"

    document_id = models.UUIDField(default=uuid.uuid4, unique=False)
    quarter = models.IntegerField()
    debit_amount = models.DecimalField(max_digits=15, decimal_places=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=0)
    financial_account_id = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE)


class Overdraft(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_overdraft = models.DecimalField(max_digits=15, decimal_places=0)
    ending_overdraft = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.player_id} Quarter {self.quarter}"


class CashChange(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=15, decimal_places=0)
    ending_cash = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.player_id.user_id.username} Quarter {self.quarter}"


class Loan(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    issued_quarter = models.IntegerField()
    interest = models.DecimalField(max_digits=5, decimal_places=2)
    payback_period = models.IntegerField()
    total_payback = models.DecimalField(max_digits=15, decimal_places=0)
    payback_per_quarter = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"${self.amount} by {self.player_id}"


class Repayment(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE)
    interest_amount = models.DecimalField(max_digits=15, decimal_places=0)
    repayment_amount = models.DecimalField(max_digits=15, decimal_places=0)
    left = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"${self.loan_id.payback_per_quarter} by {self.player_id.user_id.username}"
        )


class StateVariable(models.Model):
    esg_index = models.IntegerField()
    fixed_interest = models.DecimalField()
    current_quarter = models.IntegerField()
    simulation_duration = models.IntegerField()
    max_loan_repayment = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RecurringAction(models.Model):
    quarter = models.IntegerField()
    type = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type


class RippleTask(models.Model):
    quarter = models.IntegerField()
    type = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type
