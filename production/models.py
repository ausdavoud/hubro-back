from django.db import models

from people.models import Player
from rd.models import DynamicRD


class Factory(models.Model):
    class OwnershipTypes(models.TextChoices):
        OWNED = "OW", "Owned"
        RENTED = "RN", "Rented"

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    ownership = models.CharField(max_length=2, choices=OwnershipTypes.choices)
    quarterly_output = models.IntegerField()
    outsourcing_fee_per_unit = models.DecimalField(max_digits=15, decimal_places=0)
    labor_cost_per_unit = models.DecimalField(max_digits=15, decimal_places=0)
    maintenance_cost = models.DecimalField(max_digits=15, decimal_places=0)
    fixed_cost = models.DecimalField(max_digits=15, decimal_places=0)
    resale_value_percent = models.DecimalField(max_digits=5, decimal_places=2)
    build_cost = models.DecimalField(max_digits=15, decimal_places=0)
    workers = models.IntegerField()
    hours = models.DecimalField(max_digits=15, decimal_places=0)
    wage = models.DecimalField(max_digits=5, decimal_places=2)
    emission_t_unit = models.DecimalField(max_digits=5, decimal_places=2)
    depreciation_time = models.IntegerField()
    build_time = models.IntegerField()
    base = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - {self.ownership}"


class Production(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    product = models.ForeignKey(DynamicRD, on_delete=models.CASCADE)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    quarter = models.IntegerField()
    activity_level = models.DecimalField(max_digits=5, decimal_places=2)
    activity_factor = models.DecimalField(max_digits=5, decimal_places=2)
    produced_quantity = models.IntegerField()
    labor_cost = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - {self.product.alias}"
