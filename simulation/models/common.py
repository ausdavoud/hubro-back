from django.db import models

from .people import Player
from .rd import DynamicRD


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

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="ripple_tasks")
    run_at_quarter = models.IntegerField()
    type = models.CharField(max_length=50, choices=TaskTypes.choices)
    dynamic_rd_object = models.ForeignKey(
        DynamicRD, on_delete=models.CASCADE, related_name="ripple_tasks", null=True, blank=True
    )

    def __str__(self):
        return f"{self.dynamic_rd_object} - {self.type}"
