from rest_framework import serializers

from common.models import DecisionPool
from common.views import exceptions as common_exceptions
from rd.models import DynamicRD, RDCategories
from suppliers.serializers import SupplierSerializer


class DynamicRDSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()
    supplier = SupplierSerializer()

    class Meta:
        model = DynamicRD
        fields = [
            "id",
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
            "base_material_cost",
            "supplier",
            "unit_mat_cost_reduction",
            "emission_reduction",
            "emission_effect",
            "unit_mat_cost_effect",
            "alias",
            "icon_link",
            "state",
        ]

    def get_state(self, obj: DynamicRD):
        team = obj.team
        json_body = {"category": obj.category, "order": obj.order}
        current_quarter = self.context.get("current_quarter")
        previous_rd_items = self.context.get("previous_rd_items")
        if not current_quarter and not previous_rd_items:
            return None
        if DecisionPool.objects.filter(
            team=team,
            json_body__contains=json_body,
            made_at_quarter=current_quarter,
        ).exists():
            return DynamicRD.RDStates.RESEARCHING
        return obj.get_state(
            current_quarter, previous_rd_items=previous_rd_items
        )

    fields_to_be_removed = [
        "available_from_quarter",
        "unit_mat_cost_reduction",
        "unit_mat_cost_effect",
        "emission_reduction",
        "emission_effect",
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


class CreateBaseRDSerializer(serializers.Serializer):
    category = serializers.ChoiceField(RDCategories.choices)
    order = serializers.IntegerField(default=1)


class CreateRDProductSerializer(CreateBaseRDSerializer):
    alias = serializers.CharField(max_length=100)
    icon_link = serializers.CharField(max_length=300)
    engine = serializers.IntegerField()
    chassis = serializers.IntegerField()
    strap = serializers.IntegerField()
    engine_color = serializers.IntegerField()
    chassis_color = serializers.IntegerField()
    strap_color = serializers.IntegerField()

    def validate_engine(self, value):
        if not 0 <= value <= 2:
            raise common_exceptions.ValidationError(
                "Invalid engine index. Must be from 0 to 2."
            )
        return value

    def validate_chassis(self, value):
        if not 0 <= value <= 2:
            raise common_exceptions.ValidationError(
                "Invalid chassis index. Must be from 0 to 2."
            )
        return value

    def validate_strap(self, value):
        if not 0 <= value <= 2:
            raise common_exceptions.ValidationError(
                "Invalid strap index. Must be from 0 to 2."
            )
        return value

    def validate_engine_color(self, value):
        if not 0 <= value <= 14:
            raise common_exceptions.ValidationError(
                "Invalid color index. Must be from 0 to 14."
            )
        return value

    def validate_chassis_color(self, value):
        if not 0 <= value <= 14:
            raise common_exceptions.ValidationError(
                "Invalid color index. Must be from 0 to 14."
            )
        return value

    def validate_strap_color(self, value):
        if not 0 <= value <= 14:
            raise common_exceptions.ValidationError(
                "Invalid color index. Must be from 0 to 14."
            )
        return value
