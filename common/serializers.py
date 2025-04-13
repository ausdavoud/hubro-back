from decimal import Decimal

from rest_framework import serializers

from common.models import DecisionPool, RippleTask, StateVariable


class DecisionPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionPool
        fields = "__all__"


class RippleTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RippleTask
        fields = "__all__"


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateVariable
        fields = [
            "company_name",
            "company_slogan",
            "company_icon",
            "company_icon_bg",
            "company_icon_color",
            "company_icon_font",
        ]

    def validate_company_icon_bg(self, value):
        if not 0 <= value <= 5:
            raise serializers.ValidationError(
                "Icon background must be between 0 and 5."
            )
        return value

    def validate_company_icon(self, value):
        if not 0 <= value <= 5:
            raise serializers.ValidationError(
                "Icon icon must be between 0 and 5."
            )
        return value

    def validate_company_icon_color(self, value):
        if not 0 <= value <= 5:
            raise serializers.ValidationError(
                "Icon color must be between 0 and 5."
            )
        return value

    def validate_company_icon_font(self, value):
        if not 0 <= value <= 5:
            raise serializers.ValidationError(
                "Icon font must be between 0 and 5."
            )
        return value


class StateVariableSerializer(serializers.ModelSerializer):
    simulation_name = serializers.SerializerMethodField()
    beginning_cash = serializers.SerializerMethodField()

    class Meta:
        model = StateVariable
        fields = "__all__"

    def get_simulation_name(self, obj: StateVariable) -> str:
        return obj.team.simulation_class.name

    def get_beginning_cash(self, obj: StateVariable) -> Decimal:
        from finance.views.views import _get_cash_income_outcome

        return _get_cash_income_outcome(
            obj.team, obj.team.simulation_class.current_quarter
        )[obj.team.simulation_class.current_quarter]


class SimulationCodeSerializer(serializers.Serializer):
    simulation_code = serializers.CharField()
