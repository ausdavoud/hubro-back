from django.db import models

from rd.apps import RdConfig


class RDStates:
    LOCKED = "locked"
    AVAILABLE = "available"
    RESEARCHING = "researching"
    COMPLETED = "completed"


class StaticRD(models.Model):
    class RDTypes(models.TextChoices):
        PRODUCT = "PR", "Product"
        UPGRADE = "UP", "UPGRADE"

    class Categories(models.TextChoices):
        BASIC = "basic", "Basic jetpack"
        SPORTY = "sporty", "Sporty jetpack"
        SAFE = "safe", "Safe jetpack"
        GREEN = "green", "Green jetpack"
        PRODUCTION = "production", "Production"

    category = models.CharField(max_length=30, choices=Categories.choices)
    order = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=2, choices=RDTypes.choices)

    title = models.CharField(max_length=50)
    description = models.TextField()

    development_cost = models.DecimalField(max_digits=15, decimal_places=0)
    development_duration = models.IntegerField()
    available_from_quarter = models.IntegerField(null=True, blank=True)
    depreciation_time = models.IntegerField(null=True, blank=True)

    # 2 out of 3 are always null based on being 1. Product 2. Upgrade 3. Production
    original_unit_mat_cost = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    unit_mat_cost_effect = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    production_emission_effect = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["category", "order"]
        ordering = ["-id"]
        verbose_name = "Static R&D"
        db_table = f"{RdConfig.name}_static_rd"

    def __str__(self):
        return f"{self.category} - {self.title}"


class DynamicRD(models.Model):
    # Cannot inherit from StaticRD because bulk_create is not supported
    # on child models
    from people.models import Player

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="rd")

    category = models.CharField(max_length=30, choices=StaticRD.Categories.choices)
    order = models.PositiveSmallIntegerField()
    type = models.CharField(max_length=2, choices=StaticRD.RDTypes.choices)

    title = models.CharField(max_length=50)
    description = models.TextField()

    depreciation_time = models.IntegerField(null=True, blank=True)
    development_cost = models.DecimalField(max_digits=15, decimal_places=0)
    development_duration = models.IntegerField()
    available_from_quarter = models.IntegerField(null=True, blank=True)
    started_at = models.IntegerField(default=0)
    time_spent_developing = models.IntegerField(default=0)

    # 2 out of 3 are always null based on being 1. Product 2. Upgrade 3. Production
    original_unit_mat_cost = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    unit_mat_cost_effect = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    production_emission_effect = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)

    alias = models.CharField(max_length=100, blank=True)
    icon_link = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["player", "-id"]
        verbose_name = "Dynamic R&D"
        db_table = f"{RdConfig.name}_dynamic_rd"

    @property
    def is_completed(self):
        return (
            self.time_spent_developing == self.development_duration
            and self.started_at > 0
            and self.time_spent_developing != 0
        )

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
                RDStates.COMPLETED if self.time_spent_developing == self.development_duration else RDStates.RESEARCHING
            )

        # time-based availability
        if self.available_from_quarter:
            return RDStates.AVAILABLE if self.available_from_quarter <= current_quarter else RDStates.LOCKED

        # dependency-based availability
        previous_item = previous_rd_items.get((self.category, self.order))
        if not previous_item:
            return RDStates.LOCKED
        return (
            RDStates.AVAILABLE
            if previous_item.time_spent_developing >= previous_item.development_duration
            else RDStates.LOCKED
        )

    def __str__(self):
        return f"{self.player} - {self.category} - {self.title}"
