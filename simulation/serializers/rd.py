from rest_framework import serializers

from ..models.rd import RDProduct, RDStatic, RDUpgrade


class RDStaticSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    class Meta:
        model = RDStatic
        fields = [
            "category",
            "order",
            "type",
            "title",
            "description",
            "development_cost",
            "development_duration",
            "available_from_quarter",
            "state",
            "original_unit_mat_cost",
            "unit_mat_cost_effect",
            "production_emission_effect",
        ]

    def get_state(self, obj: RDStatic):
        player = self.context.get("player")
        return obj.get_state(player)

    fields_to_be_removed = [
        "available_from_quarter",
        "original_unit_mat_cost",
        "unit_mat_cost_effect",
        "production_emission_effect",
    ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in self.fields_to_be_removed:
            try:
                if rep[field] is None:
                    rep.pop(field)
            except KeyError:
                pass
        return rep


class RDProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    development_cost = serializers.SerializerMethodField()
    development_duration = serializers.SerializerMethodField()
    available_from_quarter = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    original_unit_mat_cost = serializers.SerializerMethodField()

    class Meta:
        model = RDProduct
        fields = [
            # Static
            "category",
            "order",
            "type",
            "title",
            "description",
            "development_cost",
            "development_duration",
            "available_from_quarter",
            # product
            "time_spent_developing",
            "state",
            "original_unit_mat_cost",
            "alias",
            "icon_link",
        ]

    def get_category(self, obj: RDUpgrade):
        return obj.static.category

    def get_type(self, obj: RDUpgrade):
        return obj.static.type

    def get_order(self, obj: RDUpgrade):
        return obj.static.order

    def get_title(self, obj: RDUpgrade):
        return obj.static.title

    def get_description(self, obj: RDUpgrade):
        return obj.static.description

    def get_development_cost(self, obj: RDUpgrade):
        return obj.static.development_cost

    def get_development_duration(self, obj: RDUpgrade):
        return obj.static.development_duration

    def get_available_from_quarter(self, obj: RDUpgrade):
        return obj.static.available_from_quarter

    def get_state(self, obj: RDUpgrade):
        return obj.get_state()

    def get_original_unit_mat_cost(self, obj: RDUpgrade):
        return obj.static.original_unit_mat_cost

    # It must have `available_from_quarter` and `original_mat_cost_effect`
    # So, there's no need to consider them nullable and rewrite to_representation


class RDUpgradeSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    development_cost = serializers.SerializerMethodField()
    development_duration = serializers.SerializerMethodField()
    available_from_quarter = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    unit_mat_cost_effect = serializers.SerializerMethodField()
    production_emission_effect = serializers.SerializerMethodField()

    class Meta:
        model = RDUpgrade
        fields = [
            # Static
            "category",
            "order",
            "type",
            "title",
            "description",
            "development_cost",
            "development_duration",
            "time_spent_developing",
            "available_from_quarter",
            # Upgrade
            "state",
            "unit_mat_cost_effect",
            "production_emission_effect",
        ]

    def get_category(self, obj: RDUpgrade):
        return obj.static.category

    def get_type(self, obj: RDUpgrade):
        return obj.static.type

    def get_order(self, obj: RDUpgrade):
        return obj.static.order

    def get_title(self, obj: RDUpgrade):
        return obj.static.title

    def get_description(self, obj: RDUpgrade):
        return obj.static.description

    def get_development_cost(self, obj: RDUpgrade):
        return obj.static.development_cost

    def get_development_duration(self, obj: RDUpgrade):
        return obj.static.development_duration

    def get_available_from_quarter(self, obj: RDUpgrade):
        return obj.static.available_from_quarter

    def get_state(self, obj: RDUpgrade):
        return obj.get_state()

    def get_unit_mat_cost_effect(self, obj: RDUpgrade):
        return obj.static.unit_mat_cost_effect

    def get_production_emission_effect(self, obj: RDUpgrade):
        return obj.static.production_emission_effect

    fields_to_be_removed = ["available_from_quarter", "unit_mat_cost_effect", "production_emission_effect"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in self.fields_to_be_removed:
            try:
                if rep[field] is None:
                    rep.pop(field)
            except KeyError:
                pass
        return rep
