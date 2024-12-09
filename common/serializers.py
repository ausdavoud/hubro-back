from rest_framework import serializers

from common.models import DecisionPool, RippleTask


class DecisionPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionPool
        fields = "__all__"


class RippleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RippleTask
        fields = "__all__"
