from django.db import models


class Supplier(models.Model):
    from rd.models import RDCategories

    class Names(models.TextChoices):
        STANDARD = "standard"
        ECO = "eco"
        GAIA = "gaia"

    rd_category = models.CharField(max_length=10, choices=RDCategories.choices)
    name = models.CharField(max_length=10, choices=Names.choices)
    price = models.IntegerField()
    emission = models.FloatField()

    def __str__(self):
        return f"{self.name} {self.rd_category}"
