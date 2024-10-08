from django.db import models
from .people import Player


class StateVariable(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    esg_index = models.IntegerField(default=0)
    fixed_interest = models.DecimalField(max_digits=5, decimal_places=2, default=2)
    current_quarter = models.IntegerField(default=1)
    simulation_duration = models.IntegerField(default=20)
    max_loan_repayment_duration = models.IntegerField(default=16)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_player_quarter(player: Player):
        state_variables = StateVariable.objects.filter(player=player).first()
        if not state_variables:
            return 0
        return state_variables.current_quarter

    def __str__(self):
        return f"{self.player.user.email}'s state variables"


class RippleTask(models.Model):
    class RippleTaskTypes(models.TextChoices):
        INCREMENT_RD_DEV_TIME = "inc_rd_dev_time", "Increment R&D Project Development Time"

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    run_at_quarter = models.IntegerField()
    type = models.CharField(max_length=50, choices=RippleTaskTypes.choices)

    def __str__(self):
        return self.type
