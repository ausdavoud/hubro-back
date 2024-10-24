import uuid

from django.db import models

from people.models import Player


class FinancialAccount(models.Model):
    class AccountNames(models.IntegerChoices):
        DEPRECIATION_OF_FACTORIES = 6030, "Depreciation of factories"
        FACTORIES = 1121, "Factories"
        AMORTIZATION = 6040, "Amortization"
        RESEARCHED_TECHNOLOGY = 1130, "Researched technology"
        DIRECT_LABOR = 5120, "Direct labor"
        DIRECT_RAW_MATERIALS = 5110, "Direct raw materials"
        FINISHED_GOODS_INVENTORY = 1720, "Finished goods inventory"
        STORAGE = 5340, "Storage"
        CASH = 1910, "Cash"
        CURRENT_PORTION_OF_LOANS_PAYABLE = (
            3310,
            "Current portion of loans payable",
        )
        INTEREST_EXPENSES = 7210, "Interest expenses"
        MAINTENANCE = 5420, "Maintenance"
        PROMOTION = 5360, "Promotion"
        SALES = 4110, "Sales"
        OVERDRAFT = 3360, "Overdraft"
        LONG_TERM_NOTES_PAYABLE = 3210, "Long term notes payable"
        RAW_MATERIAL_INVENTORY = 1710, "Raw material inventory"

    class AccountTypes(models.TextChoices):
        DEBIT = "DE", "Debit"
        CREDIT = "CR", "Credit"

    name = models.IntegerField(choices=AccountNames.choices)
    type = models.CharField(max_length=2, choices=AccountTypes.choices)

    def __str__(self):
        return f"({self.type}) ({self.name}) {self.get_name_display()}"


class Transaction(models.Model):
    class TransactionTypes(models.TextChoices):
        PAID = "PD", "Paid"
        RECEIVED = "RC", "Received"

    document = models.UUIDField(default=uuid.uuid4, unique=False)
    quarter = models.IntegerField()
    debit_amount = models.DecimalField(max_digits=15, decimal_places=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=0)
    financial_account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f"Credit: {self.credit_amount}, Debit: {self.debit_amount} - {self.financial_account.name}"


class Overdraft(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_overdraft = models.DecimalField(max_digits=15, decimal_places=0)
    ending_overdraft = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - Quarter {self.quarter}"


class CashChange(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=15, decimal_places=0)
    ending_cash = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - Quarter {self.quarter}"


class Loan(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    issued_quarter = models.IntegerField()
    interest = models.DecimalField(max_digits=5, decimal_places=2)
    payback_period = models.IntegerField()
    total_payback = models.DecimalField(max_digits=15, decimal_places=0)
    payback_per_quarter = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - ${self.amount}"


class Repayment(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    interest_amount = models.DecimalField(max_digits=15, decimal_places=0)
    repayment_amount = models.DecimalField(max_digits=15, decimal_places=0)
    left = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - ${self.loan.payback_per_quarter}"
