from django.db import models

from people.models import SimulationClass, Team


class Contract(models.Model):
    # simulation_class = models.ForeignKey(SimulationClass, on_delete=models.CASCADE)
    # define a textcoice for status for the following statuses:
    # 1. when a contract is yet to be assigned to a company
    # 2. when a contract is assigned to a company
    # now write it

    class Statuses(models.TextChoices):
        PENDING = "P", "Pending"
        ASSIGNED = "A", "Assigned"

    simulation_class = models.ForeignKey(
        SimulationClass, on_delete=models.CASCADE, related_name="contracts"
    )
    closure_quarter = models.IntegerField()
    payment_quarter = models.IntegerField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=0)
    deliverable_product = models.CharField(max_length=100)
    minimum_esg_index = models.IntegerField()
    priority = models.IntegerField()
    status = models.CharField(
        max_length=1, choices=Statuses.choices, default=Statuses.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.deliverable_product}"


class ContractPriority(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    quarter = models.IntegerField()
    priority = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team} - {self.contract} - {self.priority}"


class ContractAssignment(models.Model):
    """
    Why one to one field for contract assignment?
    because a contract can only be assigned to one company at a time
    """

    class Statuses(models.TextChoices):
        WAITING = "WG", "Waiting"
        FULFILLED = "FF", "Fulfilled"
        EXPIRED = "EX", "Expired"

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="contracts"
    )
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=Statuses.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team} - {self.contract}"
