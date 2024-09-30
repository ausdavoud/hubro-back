from django.db import models

from .people import Player


class Factory(models.Model):
    class OwnershipTypes(models.TextChoices):
        OWNED = "OW", "Owned"
        RENTED = "RN", "Rented"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
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
        return f"{self.ownership} by {self.player_id.user_id.username}"


class RnDStatic(models.Model):
    class RnDTypes(models.TextChoices):
        PRODUCT = "PR", "Product"
        UPGRADE = "UP", "UPGRADE"

    class ProductKeys(models.TextChoices):
        BASIC = "basic", "Basic jetpack"
        SPORTY = "sporty", "Sporty jetpack"
        SAFE = "safe", "Safe jetpack"
        GREEN = "green", "Green jetpack"
        PRODUCTION = 'production', 'Production'

    type = models.CharField(max_length=2, choices=RnDTypes.choices)
    title = models.CharField(max_length=50)
    product_key = models.CharField(max_length=20, choices=ProductKeys.choices, blank=True, null=True)
    development_cost = models.DecimalField(max_digits=15, decimal_places=0)
    depreciation_time = models.IntegerField(null=True, blank=True)
    origin_unit_mat_cost = models.DecimalField(
        max_digits=15, decimal_places=0, null=True, blank=True
    )
    development_duration = models.IntegerField()
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class RnDProduct(models.Model):
    static_id = models.ForeignKey(RnDStatic, on_delete=models.CASCADE)
    started_at = models.IntegerField()
    time_spent_developing = models.IntegerField()
    alias = models.CharField(max_length=100)
    icon_link = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_unlocked(self):
        return self.time_spent_developing == self.static_id.development_duration


class RnDUpgrade(models.Model):
    static_id = models.ForeignKey(
        RnDStatic, on_delete=models.CASCADE, related_name="static"
    )
    started_at = models.IntegerField()
    time_spent_developing = models.IntegerField()
    updated_product_id = models.ForeignKey(RnDProduct, on_delete=models.CASCADE)
    unit_mat_cost_effect = models.DecimalField(max_digits=5, decimal_places=2)
    production_emission_effect = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_unlocked(self):
        return self.time_spent_developing == self.static_id.development_duration


class Production(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    product_id = models.ForeignKey(RnDProduct, on_delete=models.CASCADE)
    factory_id = models.ForeignKey(Factory, on_delete=models.CASCADE)
    quarter = models.IntegerField()
    activity_level = models.DecimalField(max_digits=5, decimal_places=2)
    activity_factor = models.DecimalField(max_digits=5, decimal_places=2)
    produced_quantity = models.IntegerField()
    labor_cost = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_id.alias} by {self.player_id.user_id.username} "


class Contract(models.Model):
    class ContractStatuses(models.TextChoices):
        FULFILLED = "FF", "Fulfilled"
        WAITING = "WG", "Waiting"
        EXPIRED = "EX", "Expired"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    closure_quarter = models.IntegerField()
    payment_quarter = models.IntegerField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=0)
    deliverable_product_id = models.ForeignKey(RnDProduct, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=ContractStatuses.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.total_price} at {self.closure_quarter} by {self.player_id.user_id.username}"


class Storage(models.Model):
    class TransactionTypes(models.TextChoices):
        PAID = "PD", "Paid"
        RECEIVED = "RC", "Received"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    product_id = models.ForeignKey(RnDProduct, on_delete=models.CASCADE)
    count = models.IntegerField()
    transaction_type = models.CharField(max_length=2, choices=TransactionTypes.choices)
    quarter = models.IntegerField()
    finished_good_inventory = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.count} {self.product_id.alias} by {self.player_id.user_id.username}"
        )
