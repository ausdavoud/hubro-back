from django.db import models

from .people import Player
from .common import StateVariable


class RDStatic(models.Model):
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
    type = models.CharField(max_length=2, choices=RDTypes.choices)
    order = models.PositiveIntegerField()

    title = models.CharField(max_length=50)
    description = models.TextField()

    development_cost = models.DecimalField(max_digits=15, decimal_places=0)
    depreciation_time = models.IntegerField(null=True, blank=True)
    development_duration = models.IntegerField()
    available_from_quarter = models.IntegerField(null=True, blank=True)

    # 2 out of 3 are always null based on being 1. Product 2. Upgrade 3. Production
    original_unit_mat_cost = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)
    unit_mat_cost_effect = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    production_emission_effect = models.DecimalField(max_digits=15, decimal_places=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "order"]
        unique_together = ["category", "order"]
        verbose_name = "R&D Static"
        db_table = "rd_static"

    @property
    def previous_item(self):
        return RDStatic.objects.filter(category=self.category, order=self.order - 1).first()

    def has_dynamic_obj(self, player: Player):
        return self.products.filter(player=player).exists() or self.upgrades.filter(player=player).exists()

    def get_product(self, player: Player):
        return self.products.filter(player=player).first()

    def get_upgrade(self, player: Player):
        return self.upgrades.filter(player=player).first()

    def get_state(self, player: Player):
        current_quarter = StateVariable.get_player_quarter(player)
        # time-based availability
        if self.available_from_quarter:
            return "available" if self.available_from_quarter <= current_quarter else "locked"

        # dependency-based availability
        previous_static_item = self.previous_item
        if previous_static_item:
            has_dynamic_item = previous_static_item.has_dynamic_obj(player=player)
            return "available" if has_dynamic_item else "locked"

        raise Exception(f"{self.title} has no previous item")

    def __str__(self):
        return f"{self.category} - {self.title}"


class RDProduct(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    static = models.ForeignKey(RDStatic, on_delete=models.CASCADE, related_name="products")
    started_at = models.IntegerField()
    time_spent_developing = models.IntegerField()
    alias = models.CharField(max_length=100)
    icon_link = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "R&D Product"
        db_table = "rd_product"

    def get_state(self):
        if self.time_spent_developing == self.static.development_duration:
            return "completed"
        elif self.time_spent_developing < self.static.development_duration:
            return "researching"

    def __str__(self):
        return f"{self.static.title} by {self.player.user.email}"


class RDUpgrade(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    static = models.ForeignKey(RDStatic, on_delete=models.CASCADE, related_name="upgrades")
    started_at = models.IntegerField()
    time_spent_developing = models.IntegerField()
    updated_product = models.ForeignKey(RDProduct, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "R&D Upgrade"
        db_table = "rd_upgrade"

    def get_state(self):
        if self.time_spent_developing == self.static.development_duration:
            return "completed"
        elif self.time_spent_developing < self.static.development_duration:
            return "researching"

    def __str__(self):
        return f"{self.static.title} by {self.player.user.email}"
