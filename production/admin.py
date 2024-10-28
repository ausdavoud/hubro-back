from django.contrib import admin

from production.models import Factory, Production


class FactoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "ownership",
        "name",
        "output_per_quarter",
        "outsourcing_fee_per_unit",
        "labor_cost_per_unit",
    ]


class ProductionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "product",
        "factory",
        "quarter",
        "activity_level",
        "activity_factor",
        "produced_quantity",
        "labor_cost",
    ]


admin.site.register(Factory, FactoryAdmin)
admin.site.register(Production, ProductionAdmin)
