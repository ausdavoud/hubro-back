from django.contrib import admin

from production.models import Factory, Production, Storage


class FactoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "team",
        "ownership",
        "name",
        "output_per_quarter",
        "outsourcing_fee_per_unit",
        "labor_cost_per_unit",
    ]


class ProductionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "team",
        "product",
        "factory",
        "quarter",
        "activity_level",
        "produced_quantity",
        "labor_cost",
    ]


class StorageAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "product", "quantity"]


admin.site.register(Storage, StorageAdmin)
admin.site.register(Factory, FactoryAdmin)
admin.site.register(Production, ProductionAdmin)
