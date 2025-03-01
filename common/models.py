from django.db import models

from people.models import Player, Team


class DecisionPool(models.Model):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="decision_pool"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="decision_pool"
    )
    made_at_quarter = models.IntegerField()
    endpoint = models.CharField(max_length=100)
    json_body = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.endpoint


class StateVariable(models.Model):
    team = models.OneToOneField(
        Team, on_delete=models.CASCADE, related_name="state_variables"
    )

    esg_index = models.IntegerField(default=0)
    esg_reporting_enabled = models.BooleanField(default=False)
    marketing_budget = models.DecimalField(
        max_digits=15, decimal_places=0, default=0
    )

    fixed_interest = models.DecimalField(
        max_digits=5, decimal_places=2, default=2
    )
    max_loan_repayment_duration = models.IntegerField(default=16)

    company_name = models.CharField(max_length=20, null=True)
    company_slogan = models.CharField(max_length=40, null=True)
    company_icon = models.IntegerField(default=0)
    company_icon_bg = models.IntegerField(default=0)
    company_icon_color = models.IntegerField(default=0)
    company_icon_font = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team}'s state variables"


class RippleTask(models.Model):
    class TaskTypes(models.TextChoices):
        INCREMENT_RD_DEV_TIME = (
            "inc_rd_dev_time",
            "Increment R&D Project Development Time",
        )
        PRODUCTION = "production", "Production"
        ESG_REPORTING = "esg_reporting", "ESG Reporting"
        LOAN_REPAYMENT = "loan_repayment", "Loan Repayment"
        LOAN_INTEREST = "loan_interest", "Loan Interest"
        FACTORY_DEPRECIATION = "factory_depreciation", "Factory Depreciation"
        FACTORY_MAINTENANCE = "factory_maintenance", "Factory Maintenance"
        PAY_RD_COST = "pay_rd_cost", "Pay R&D Project Cost"
        AMORTIZATION_OF_PROJECTS = (
            "amortization_of_projects",
            "Amortization of Projects",
        )

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="ripple_tasks"
    )
    run_at_quarter = models.IntegerField()
    type = models.CharField(max_length=50, choices=TaskTypes.choices)
    json_body = models.JSONField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type
