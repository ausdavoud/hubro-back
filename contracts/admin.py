from django.contrib import admin

from contracts.models import Contract, ContractAssignment, ContractPriority


class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "simulation_class",
        "closure_quarter",
        "payment_quarter",
        "quantity",
        "unit_price",
        "total_price",
        "deliverable_product",
        "minimum_esg_index",
        "priority",
    ]


class ContractPriorityAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "contract", "quarter", "priority"]


class ContractAssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "contract", "status"]


admin.site.register(Contract, ContractAdmin)
admin.site.register(ContractPriority, ContractPriorityAdmin)
admin.site.register(ContractAssignment, ContractAssignmentAdmin)
