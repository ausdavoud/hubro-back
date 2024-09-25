from django.db import models

from .people import Player


class Factory(models.Model):
    class OwnershipType(models.TextChoices):
        OWNED = "OW", "Owned"
        RENTED = "RN", "Rented"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    ownership = models.CharField(max_length=2, choices=OwnershipType.choices)
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
        return f"{self.ownership} by {self.player_id.user.username}"


class RnD(models.Model):
    class RnDTypes(models.TextChoices):
        PRODUCT = "PR", "Product"
        UPGRADE = "UP", "UPGRADE"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=RnDTypes.choices)
    unit_mat_cost_effect = models.DecimalField(max_digits=5, decimal_places=2)
    title = models.CharField(max_length=50)
    updated_product = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    depreciation_time = models.IntegerField()
    is_available = models.BooleanField()
    origin_unit_mat_cost = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.player_id.user.username}"


class Product(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    research_project_id = models.ForeignKey(RnD, on_delete=models.CASCADE)
    original_unit_mat_cost = models.DecimalField(max_digits=15, decimal_places=0)
    calculated_unit_mat_cost = models.DecimalField(max_digits=15, decimal_places=0)
    alias = models.CharField(max_length=50)
    icon = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.alias} by {self.player_id.user.username}"


class Production(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    factory_id = models.ForeignKey(Factory, on_delete=models.CASCADE)
    quarter = models.IntegerField()
    activity_level = models.DecimalField(max_digits=5, decimal_places=2)
    activity_factor = models.DecimalField(max_digits=5, decimal_places=2)
    produced_quantity = models.IntegerField()
    labor_cost = models.DecimalField(max_digits=15, decimal_places=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_id.alias} by {self.player_id.user.username} "


class Contract(models.Model):
    class ContractStatus(models.TextChoices):
        FULFILLED = "FF", "Fulfilled"
        WAITING = "WT", "Waiting"
        EXPIRED = "EX", "Expired"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    closure_quarter = models.IntegerField()
    payment_quarter = models.IntegerField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=0)
    deliverable_product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=ContractStatus.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.total_price} at {self.closure_quarter} by {self.player_id.user.username}"


class Storage(models.Model):
    class TransactionType(models.TextChoices):
        PAID = "PD", "Paid"
        RECEIVED = "RC", "Received"

    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()
    transaction_type = models.CharField(max_length=2, choices=TransactionType.choices)
    quarter = models.IntegerField()
    finished_good_inventory = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.count} {self.product_id.alias} by {self.player_id.user.username}"
