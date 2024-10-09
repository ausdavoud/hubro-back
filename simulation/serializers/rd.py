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
    category = serializers.CharField(source="static.category")
    type = serializers.CharField(source="static.type")
    order = serializers.IntegerField(source="static.order")
    title = serializers.CharField(source="static.title")
    description = serializers.CharField(source="static.description")
    development_cost = serializers.DecimalField(max_digits=15, decimal_places=0, source="static.development_cost")
    development_duration = serializers.IntegerField(source="static.development_duration")
    available_from_quarter = serializers.IntegerField(source="static.available_from_quarter")
    state = serializers.SerializerMethodField()
    original_unit_mat_cost = serializers.DecimalField(
        max_digits=15, decimal_places=0, source="static.original_unit_mat_cost"
    )

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

    def get_state(self, obj: RDUpgrade):
        return obj.get_state()

    # It must have `available_from_quarter` and `original_mat_cost_effect`
    # So, there's no need to consider them nullable and rewrite to_representation


class RDUpgradeSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="static.category")
    type = serializers.CharField(source="static.type")
    order = serializers.IntegerField(source="static.order")
    title = serializers.CharField(source="static.title")
    description = serializers.CharField(source="static.description")
    development_cost = serializers.DecimalField(max_digits=15, decimal_places=0, source="static.development_cost")
    development_duration = serializers.IntegerField(source="static.development_duration")
    available_from_quarter = serializers.IntegerField(source="static.available_from_quarter")
    state = serializers.SerializerMethodField()
    unit_mat_cost_effect = serializers.DecimalField(
        max_digits=5, decimal_places=2, source="static.unit_mat_cost_effect"
    )
    production_emission_effect = serializers.DecimalField(
        max_digits=15, decimal_places=0, source="static.production_emission_effect"
    )

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

    def get_state(self, obj: RDUpgrade):
        return obj.get_state()

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


class CreateRDUpgradeSerializer(serializers.Serializer):
    category = serializers.ChoiceField(RDStatic.Categories.choices)
    order = serializers.IntegerField(default=1)


class CreateRDProductSerializer(CreateRDUpgradeSerializer):
    alias = serializers.CharField(max_length=100)
    icon_link = serializers.CharField(max_length=300)
