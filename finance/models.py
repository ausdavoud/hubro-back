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
        LOSS_ON_SALE_OF_ASSETS = 5520, "Loss on sale of assets"

    class AccountTypes(models.TextChoices):
        DEBIT = "DE", "Debit"
        CREDIT = "CR", "Credit"

    name = models.IntegerField(choices=AccountNames.choices)
    type = models.CharField(max_length=2, choices=AccountTypes.choices)

    def __str__(self):
        return self.get_name_display()


class Transaction(models.Model):
    class Categories(models.TextChoices):
        DEPRECIATION_OF_FACTORIES = "Depreciation of factories"
        AMORTIZATION_OF_PROJECTS = "Amortization of projects"
        MATERIALS_USED_IN_PRODUCTION = "Materials used in production"
        COST_OF_SOLD_PRODUCTS = "Cost of sold products"
        WAGES_FOR_PRODUCTION = "Wages for production workers"
        CURRENT_PORTION_OF_LOANS = "Current portion of loans to be paid this year"
        NEW_LOANS = "New loans"
        LOAN_REPAYMENT = "Loan Repayment"
        OVERDRAFT = "Overdraft"
        SALES = "Sales"
        STORAGE = "Storage"
        PROMOTION = "Promotion"
        MAINTENANCE = "Maintenance"
        INTEREST_ON_OVERDRAFT = "Interest on overdraft"
        LOAN_INTEREST = "Loan interest"
        SOLD_FACTORIES = "Sold factories"
        LOSS_ON_SALE_OF_ASSETS = "Loss on sale of assets"
        EXTRAORDINARY_PR_EXPENSES = "Extraordinary PR expenses"

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    category = models.CharField(max_length=80, choices=Categories.choices)
    quarter = models.IntegerField()
    debit_amount = models.DecimalField(max_digits=15, decimal_places=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=0)
    financial_account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE)

    def __str__(self):
        return self.category


class Overdraft(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_overdraft = models.DecimalField(max_digits=15, decimal_places=0)
    ending_overdraft = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.beginning_overdraft}"


class CashChange(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=15, decimal_places=0)
    ending_cash = models.DecimalField(max_digits=15, decimal_places=0)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.beginning_cash}"


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
        return f"{self.amount}"


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
        # Wrap decimal value into string,
        # otherwise django raises error in admin panel
        return f"{self.repayment_amount}"
