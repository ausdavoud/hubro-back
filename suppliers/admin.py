from django.contrib import admin

from suppliers.models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "rd_category", "price", "emission")
    list_filter = ("name", "rd_category")
