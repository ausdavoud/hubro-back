from rest_framework import serializers

from suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "rd_category", "name", "price", "emission")


class SetSupplierSerializer(serializers.ModelSerializer):
    supplier_id = serializers.IntegerField()

    class Meta:
        model = Supplier
        fields = ("rd_category", "supplier_id")
