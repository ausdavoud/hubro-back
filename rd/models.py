from django.db import models

from people.models import Team
from rd.apps import RdConfig


# Has to be here to avoid circular import
class RDCategories(models.TextChoices):
    BASIC = "basic", "Basic jetpack"
    SPORTY = "sporty", "Sporty jetpack"
    SAFE = "safe", "Safe jetpack"
    GREEN = "green", "Green jetpack"
    PRODUCTION = "production", "Production"


class DynamicRD(models.Model):
    class RDTypes(models.TextChoices):
        PRODUCT = "PR", "Product"
        UPGRADE = "UP", "UPGRADE"

    class RDStates(models.TextChoices):
        LOCKED = "locked"
        AVAILABLE = "available"
        RESEARCHING = "researching"
        COMPLETED = "completed"

    class Engines(models.IntegerChoices):
        ENGINE_1 = 0, "Engine 1"
        ENGINE_2 = 1, "Engine 2"
        ENGINE_3 = 2, "Engine 3"

    class Chassis(models.IntegerChoices):
        CHASSIS_1 = 0, "Chassis 1"
        CHASSIS_2 = 1, "Chassis 2"
        CHASSIS_3 = 2, "Chassis 3"

    class Straps(models.IntegerChoices):
        STRAP_1 = 0, "Strap 1"
        STRAP_2 = 1, "Strap 2"
        STRAP_3 = 2, "Strap 3"

    class Colors(models.IntegerChoices):
        COLOR_1 = 0, "rgb(141, 110, 99)"
        COLOR_2 = 1, "rgb(236, 64, 122)"
        COLOR_3 = 2, "rgb(126, 87, 194)"
        COLOR_4 = 3, "rgb(186, 104, 200)"
        COLOR_5 = 4, "rgb(102, 187, 106)"
        COLOR_6 = 5, "rgb(205, 220, 57)"
        COLOR_7 = 6, "rgb(66, 165, 245)"
        COLOR_8 = 7, "rgb(255, 202, 40)"
        COLOR_9 = 8, "rgb(239, 83, 80)"
        COLOR_10 = 9, "rgb(38, 166, 154)"
        COLOR_11 = 10, "rgb(255, 171, 64)"
        COLOR_12 = 11, "rgb(238, 238, 238)"
        COLOR_13 = 12, "rgb(189, 189, 189)"
        COLOR_14 = 13, "rgb(102, 102, 102)"
        COLOR_15 = 14, "rgb(55, 71, 79)"

    from suppliers.models import Supplier

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="rd")

    category = models.CharField(max_length=30, choices=RDCategories.choices)
    order = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=2, choices=RDTypes.choices)

    title = models.CharField(max_length=50)
    description = models.TextField()

    depreciation_time = models.IntegerField(null=True, blank=True)
    development_cost = models.DecimalField(max_digits=15, decimal_places=0)
    development_duration = models.IntegerField()
    available_from_quarter = models.IntegerField(null=True, blank=True)
    started_at = models.IntegerField(default=0)
    time_spent_developing = models.IntegerField(default=0)

    # 2 out of 3 are always null based on being 1. Product 2. Upgrade 3. Production
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    # below is for upgrade type only
    unit_mat_cost_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # below is for production type only
    emission_reduction = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # below is for product type only, namely the sum of all reductions for a product
    unit_mat_cost_effect = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    emission_effect = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    alias = models.CharField(max_length=100, blank=True)
    icon_link = models.CharField(max_length=300, blank=True)
    engine = models.IntegerField(choices=Engines.choices, null=True, blank=True)
    chassis = models.IntegerField(choices=Chassis, null=True, blank=True)
    strap = models.IntegerField(choices=Straps, null=True, blank=True)
    engine_color = models.IntegerField(choices=Colors, null=True, blank=True)
    chassis_color = models.IntegerField(choices=Colors, null=True, blank=True)
    strap_color = models.IntegerField(choices=Colors, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "order"]
        unique_together = ["team", "category", "order"]
        verbose_name = "Dynamic R&D"
        db_table = f"{RdConfig.name}_dynamic_rd"

    @property
    def final_cost(self):
        return self.original_unit_mat_cost * (1 - self.unit_mat_cost_effect)

    @property
    def is_completed(self):
        return self.time_spent_developing == self.development_duration and self.started_at > 0

    @property
    def is_researching(self):
        return self.time_spent_developing < self.development_duration and self.started_at > 0

    def get_state(self, current_quarter: int, previous_rd_items):
        """
        Determines the current state of an R&D item based on its progress, availability, and dependencies.
        To check if user has started the research process for this R&D item, check if started_at > 0.
        Because the start_at must be a valid quarter (a positive integer), and if it's not,
        it means the user has not started the research process.

        Args:
            current_quarter (int): The current quarter of the simulation.
            prefetched_rd_table (dict): A prefetched database query result containing R&D items.

        Returns:
            RDStates: The current state of the R&D item, which can be one of the following:
                - RDStates.COMPLETED: The R&D item has been fully developed.
                - RDStates.RESEARCHING: The R&D item is currently being developed.
                - RDStates.AVAILABLE: The R&D item is available for research.
                - RDStates.LOCKED: The R&D item is not yet available for research.
        """
        # user has started the research process for this R&D item
        if self.started_at > 0:
            return (
                DynamicRD.RDStates.COMPLETED
                if self.time_spent_developing == self.development_duration
                else DynamicRD.RDStates.RESEARCHING
            )

        # time-based availability
        if self.available_from_quarter:
            return (
                DynamicRD.RDStates.AVAILABLE
                if self.available_from_quarter <= current_quarter
                else DynamicRD.RDStates.LOCKED
            )

        # dependency-based availability
        previous_item = previous_rd_items.get((self.category, self.order))
        if not previous_item:
            return DynamicRD.RDStates.LOCKED
        return (
            DynamicRD.RDStates.AVAILABLE
            if previous_item.time_spent_developing >= previous_item.development_duration
            else DynamicRD.RDStates.LOCKED
        )

    def __str__(self):
        return self.title
