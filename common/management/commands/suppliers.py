from typing import Any

from django.core.management.base import BaseCommand

from common.management.data_fixtures import SUPPLIERS
from suppliers.models import Supplier


class Command(BaseCommand):
    help = "Create suppliers"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Creating Suppliers")
        self._create_suppliers(suppliers=SUPPLIERS)

    def _create_suppliers(self, suppliers: dict):
        for rd_category in suppliers.keys():
            for supplier_name in suppliers[rd_category]:
                price = suppliers[rd_category][supplier_name]["price"]
                emission = suppliers[rd_category][supplier_name]["emission"]
                supplier_dict = {
                    "rd_category": rd_category,
                    "name": supplier_name,
                    "price": price,
                    "emission": emission,
                }
                try:
                    supplier_obj, created = Supplier.objects.get_or_create(
                        **supplier_dict
                    )
                except Supplier.MultipleObjectsReturned:
                    continue
                if created:
                    self.stdout.write(
                        f"Created supplier {supplier_obj.name} for {supplier_obj.rd_category}"
                    )
                    continue
                self.stderr.write(
                    f"Found previously added supplier with name: {supplier_obj.name}"
                )
