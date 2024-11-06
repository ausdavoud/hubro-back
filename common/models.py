from django.db import models

from people.models import Player


class DecisionPool(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="decision_pool")
    made_at_quarter = models.IntegerField()
    endpoint = models.CharField(max_length=100)
    json_body = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.endpoint


class StateVariable(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name="state_variables")
    esg_index = models.IntegerField(default=0)
    fixed_interest = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    quarter = models.IntegerField(default=1)
    simulation_duration = models.IntegerField(default=20)
    max_loan_repayment_duration = models.IntegerField(default=16)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player}'s state variables"


class RippleTask(models.Model):
    class TaskTypes(models.TextChoices):
        INCREMENT_RD_DEV_TIME = "inc_rd_dev_time", "Increment R&D Project Development Time"
        PRODUCTION = "production", "Production"

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="ripple_tasks")
    run_at_quarter = models.IntegerField()
    type = models.CharField(max_length=50, choices=TaskTypes.choices)
    json_body = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type
