from django.db import models

from .people import Player
from .rd import DynamicRD


class Contract(models.Model):
    class ContractStatuses(models.TextChoices):
        FULFILLED = "FF", "Fulfilled"
        WAITING = "WG", "Waiting"
        EXPIRED = "EX", "Expired"

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    closure_quarter = models.IntegerField()
    payment_quarter = models.IntegerField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=0)
    deliverable_product = models.ForeignKey(DynamicRD, on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=ContractStatuses.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - {self.total_price} at {self.closure_quarter}"


class Storage(models.Model):
    class TransactionTypes(models.TextChoices):
        PAID = "PD", "Paid"
        RECEIVED = "RC", "Received"

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    product = models.ForeignKey(DynamicRD, on_delete=models.CASCADE)
    count = models.IntegerField()
    transaction_type = models.CharField(max_length=2, choices=TransactionTypes.choices)
    quarter = models.IntegerField()
    finished_good_inventory = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} - {self.count} {self.product.alias}"
