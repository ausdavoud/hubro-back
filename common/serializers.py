from rest_framework import serializers

from common.models import DecisionPool


class DecisionPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionPool
        fields = "__all__"
