from django.contrib.auth import authenticate
from django.forms import ValidationError
from rest_framework import serializers

from .models.people import CustomUser
from .models.simulation import Factory, RnDProduct, RnDStatic, RnDUpgrade


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

    def create(self, clean_data):
        user = CustomUser.objects.create_user(email=clean_data["email"], password=clean_data["password"])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(username=clean_data["email"], password=clean_data["password"])
        if not user:
            raise ValidationError("User not found")
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name"]


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = "__all__"


class RnDStaticSerializer(serializers.ModelSerializer):
    static = serializers.SerializerMethodField()

    class Meta:
        model = RnDStatic
        fields = "__all__"

    def get_state():
        pass


class RnDProductSerializer(serializers.ModelSerializer):
    static = RnDStaticSerializer(source="static", read_only=True)
    state = serializers.SerializerMethodField()

    class Meta:
        model = RnDUpgrade
        fields = [
            "static",
            "state",
            "time_spent_developing",
            "alias",
            "icon_link",
        ]

    def get_state(self, obj: RnDProduct):
        if obj.time_spent_developing == obj.static.development_duration:
            return "completed"
        elif obj.time_spent_developing < obj.static.development_duration:
            return "researching"


class RnDUpgradeSerializer(serializers.ModelSerializer):
    static = RnDStaticSerializer(source="static", read_only=True)
    state = serializers.SerializerMethodField()

    class Meta:
        model = RnDUpgrade
        fields = [
            "static",
            "state",
            "time_spent_developing",
            "unit_mat_cost_effect",
            "production_emission_effect",
        ]

    def get_state(self, obj: RnDUpgrade):
        if obj.time_spent_developing == obj.static.development_duration:
            return "completed"
        elif obj.time_spent_developing < obj.static.development_duration:
            return "researching"
