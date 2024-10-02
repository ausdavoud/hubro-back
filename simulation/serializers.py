from django.contrib.auth import authenticate, get_user_model
from django.forms import ValidationError
from rest_framework import serializers

from .models.simulation import Factory, RnDProduct, RnDStatic, RnDUpgrade

UserModel = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"

    def create(self, clean_data):
        user = UserModel.objects.create_user(
            email=clean_data["email"], password=clean_data["password"]
        )
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(
            username=clean_data["email"], password=clean_data["password"]
        )
        if not user:
            raise ValidationError("User not found")
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["email", "first_name"]


class FactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Factory
        fields = "__all__"


class RnDStaticSerializer(serializers.ModelSerializer):
    class Meta:
        model = RnDStatic
        fields = "__all__"


class RnDProductSerializer(serializers.ModelSerializer):
    static_id = RnDStaticSerializer(source="static", read_only=True)
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = RnDUpgrade
        fields = [
            "static_id",
            "time_spent_developing",
            "alias",
            "icon_link",
            "is_unlocked",
        ]

    def get_is_unlocked(self, obj: RnDProduct):
        return obj.is_unlocked()


class RnDUpgradeSerializer(serializers.ModelSerializer):
    static_id = RnDStaticSerializer(source="static", read_only=True)
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = RnDUpgrade
        fields = [
            "static_id",
            "time_spent_developing",
            "unit_mat_cost_effect",
            "production_emission_effect",
            "is_unlocked",
        ]

    def get_is_unlocked(self, obj: RnDUpgrade):
        return obj.is_unlocked()
