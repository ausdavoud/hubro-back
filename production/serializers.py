from rest_framework import serializers


from production.models import Factory, Production


class FactorySerializer(serializers.ModelSerializer):
    is_finished = serializers.BooleanField(default=True)

    class Meta:
        model = Factory
        fields = "__all__"


class NewFactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = ["ownership"]


class SellFactorySerializer(serializers.Serializer):
    factory_id = serializers.IntegerField()


class SelectProductSerializer(serializers.Serializer):
    factory_id = serializers.IntegerField()
    product_id = serializers.IntegerField()


class SetActivityLevelSerializer(serializers.ModelSerializer):
    factory_id = serializers.IntegerField()

    class Meta:
        model = Production
        fields = ["factory_id", "activity_level"]


class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = "__all__"
