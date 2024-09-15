from django.db import models

from hubro_back.simulation.models.users import Player


class Overdraft(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_overdraft = models.DecimalField(max_digits=15, decimal_places=2)
    ending_overdraft = models.DecimalField(max_digits=15, decimal_places=2)
    quarter = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CashChange(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    beginning_cash = models.DecimalField(max_digits=15, decimal_places=2)
    ending_cash = models.DecimalField(max_digits=15, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Loan(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    issued_quarter = models.IntegerField()
    interest = models.DecimalField(max_digits=5, decimal_places=2)
    payback_period = models.IntegerField()
    total_payback = models.DecimalField(max_digits=15, decimal_places=2)
    payback_per_quarter = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Repayment(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    loan_id = models.ForeignKey(Loan, on_delete=models.CASCADE)
    interest_amount = models.DecimalField(max_digits=15, decimal_places=2)
    left = models.DecimalField(max_digits=15, decimal_places=2)
    quarter = models.IntegerField()


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
    
    pass

class RippleTask(models.Model):
    quarter = models.IntegerField()
    type = models.CharField(max_length=100)

    pass
