import random

from django.db import models

from common.management.data_fixtures import FACTORY_NAMES
from people.models import Team
from rd.models import DynamicRD

# factory_string_en = 'Factory'
# unused for now
factory_string_fa = "کارخانه"


class Factory(models.Model):
    class OwnershipTypes(models.TextChoices):
        OWNED = "OW", "Owned"
        RENTED = "RN", "Rented"

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    built_at_quarter = models.IntegerField()
    name = models.CharField(max_length=20, blank=True)
    ownership = models.CharField(max_length=2, choices=OwnershipTypes.choices)
    output_per_quarter = models.IntegerField()
    build_cost = models.DecimalField(max_digits=15, decimal_places=0)
    setup_time = models.IntegerField()
    outsourcing_fee_per_unit = models.DecimalField(
        max_digits=15, decimal_places=0
    )
    labor_cost_per_unit = models.DecimalField(max_digits=15, decimal_places=0)
    maintenance_cost_per_quarter = models.DecimalField(
        max_digits=15, decimal_places=0
    )
    resale_value_percent = models.DecimalField(max_digits=5, decimal_places=2)
    emissions_per_unit = models.DecimalField(max_digits=5, decimal_places=2)
    depreciation_time = models.IntegerField()

    fixed_cost = models.DecimalField(max_digits=15, decimal_places=0)
    workers = models.IntegerField()
    hours = models.DecimalField(max_digits=15, decimal_places=0)
    wage = models.DecimalField(max_digits=5, decimal_places=2)
    base = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name or 'Untitled'}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = generate_unique_factory_name(team=self.team)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Factories"
        constraints = [
            models.UniqueConstraint(
                fields=["team", "name"], name="unique_factory_name_per_team"
            )
        ]


def generate_unique_factory_name(team: Team = None):
    existing_names = set(
        Factory.objects.filter(team=team).values_list("name", flat=True)
    )
    available_names = [
        name
        for name in FACTORY_NAMES
        if f"{factory_string_fa} {name}" not in existing_names
    ]

    if not available_names:
        base_name = random.choice(FACTORY_NAMES)
        i = 1
        while f"{factory_string_fa} {base_name} {i}" in existing_names:
            i += 1
        return f"{factory_string_fa} {base_name} {i}"

    chosen_name = random.choice(available_names)
    return f"{factory_string_fa} {chosen_name}"


class Production(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="productions"
    )
    product = models.ForeignKey(DynamicRD, on_delete=models.CASCADE)
    factory = models.ForeignKey(Factory, on_delete=models.CASCADE)
    quarter = models.IntegerField()
    activity_level = models.DecimalField(
        max_digits=5, decimal_places=2, default=100
    )
    produced_quantity = models.IntegerField()
    labor_cost = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.alias


class Storage(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="storages"
    )
    product = models.ForeignKey(DynamicRD, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.team} - {self.quantity} {self.product.alias}"
