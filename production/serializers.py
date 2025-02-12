from rest_framework import serializers

from production.models import Factory, Production
from rd.models import DynamicRD
from rd.serializers import DynamicRDSerializer


class FactorySerializer(serializers.ModelSerializer):
    # is_new shows if the factory is a decision (true)
    # or has been created successfully (false)
    is_new = serializers.BooleanField(default=False)
    activity_level = serializers.SerializerMethodField()
    selected_product = serializers.SerializerMethodField()

    class Meta:
        model = Factory
        fields = "__all__"

    def get_activity_level(self, obj: Factory):
        # get it from the decision at current quarter
        team = self.context["team"]
        decision = (
            team.decision_pool.filter(
                endpoint="production/set_activity_level",
                json_body__factory_id=obj.pk,
            )
            .order_by("-made_at_quarter")
            .first()
        )
        if not decision:
            return 100
        return decision.json_body["activity_level"]

    def get_selected_product(self, obj: Factory):
        #  get it from the decision at current quarter
        team = self.context["team"]
        decision = (
            team.decision_pool.filter(
                endpoint="production/select_product",
                json_body__factory_id=obj.pk,
            )
            .order_by("-made_at_quarter")
            .first()
        )
        if not decision:
            return None
        product_id = decision.json_body["product_id"]
        dynamic_rd = DynamicRD.objects.get(pk=product_id)
        serialized_dynamic_rd = DynamicRDSerializer(dynamic_rd)
        return serialized_dynamic_rd.data


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
