from rest_framework import serializers

from ..models.rd import DynamicRD, StaticRD


class DynamicRDSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    class Meta:
        model = DynamicRD
        fields = [
            "category",
            "order",
            "type",
            "title",
            "description",
            "development_cost",
            "development_duration",
            "started_at",
            "time_spent_developing",
            "available_from_quarter",
            "original_unit_mat_cost",
            "unit_mat_cost_effect",
            "production_emission_effect",
            "alias",
            "icon_link",
            "state",
        ]

    def get_state(self, obj: DynamicRD):
        current_quarter = self.context.get("current_quarter")
        previous_rd_items = self.context.get("previous_rd_items")
        return obj.get_state(current_quarter, previous_rd_items=previous_rd_items)

    fields_to_be_removed = [
        "available_from_quarter",
        "original_unit_mat_cost",
        "unit_mat_cost_effect",
        "production_emission_effect",
        "alias",
        "icon_link",
    ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in self.fields_to_be_removed:
            try:
                if rep[field] is None or rep[field] == "":
                    rep.pop(field)
            except KeyError:
                pass
        return rep


class BaseCreateRDSerializer(serializers.Serializer):
    category = serializers.ChoiceField(StaticRD.Categories.choices)
    order = serializers.IntegerField(default=1)


class CreateRDUpgradeSerializer(BaseCreateRDSerializer):
    pass


class CreateRDProductSerializer(BaseCreateRDSerializer):
    alias = serializers.CharField(max_length=100)
    icon_link = serializers.CharField(max_length=300)
