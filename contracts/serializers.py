from rest_framework import serializers

from contracts.models import Contract


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class ContractIDSerializer(serializers.Serializer):
    contract_id = serializers.IntegerField()


class ContractsOrderSerializer(serializers.Serializer):
    marketing_budget = serializers.DecimalField(max_digits=15, decimal_places=0)
    contract_ids = serializers.ListField(child=serializers.IntegerField(), default=list)
