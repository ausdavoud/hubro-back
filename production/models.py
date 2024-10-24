import random

from django.db import models

from common.management.data_fixtures import FACTORY_NAMES
from people.models import Player
from rd.models import DynamicRD


class Factory(models.Model):
    class OwnershipTypes(models.TextChoices):
        OWNED = "OW", "Owned"
        RENTED = "RN", "Rented"

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
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

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.generate_unique_name()
        super().save(*args, **kwargs)

    def generate_unique_name(self):
        existing_names = set(Factory.objects.filter(player=self.player).values_list("name", flat=True))
        available_names = [name for name in FACTORY_NAMES if f"Factory {name}" not in existing_names]

        if not available_names:
            base_name = random.choice(FACTORY_NAMES)
            i = 1
            while f"Factory {base_name} {i}" in existing_names:
                i += 1
            return f"Factory {base_name} {i}"

        chosen_name = random.choice(available_names)
        return f"Factory {chosen_name}"

    class Meta:
        verbose_name_plural = "Factories"
        constraints = [models.UniqueConstraint(fields=["player", "name"], name="unique_factory_name_per_player")]


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
