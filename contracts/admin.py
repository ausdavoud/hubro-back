from django.contrib import admin

from contracts.models import Contract, Storage


class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "closure_quarter",
        "payment_quarter",
        "quantity",
        "unit_price",
        "total_price",
        "deliverable_product",
        "status",
    ]


class StorageAdmin(admin.ModelAdmin):
    list_display = ["id", "player", "product", "count", "transaction_type", "quarter", "finished_good_inventory"]


admin.site.register(Contract, ContractAdmin)
admin.site.register(Storage, StorageAdmin)
