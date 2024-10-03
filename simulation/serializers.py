from django.contrib.auth import authenticate
from django.forms import ValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .models.people import CustomUser
from .models.simulation import Factory, RnDProduct, RnDStatic, RnDUpgrade


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenRefreshView(TokenRefreshView):
    @extend_schema(
        responses={
            status.HTTP_200_OK: TokenRefreshResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "password", "role"]

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
    state = serializers.SerializerMethodField()

    class Meta:
        model = RnDStatic
        fields = "__all__"

    def get_state(self, obj):
        pass


class RnDProductSerializer(serializers.ModelSerializer):
    static = RnDStaticSerializer(read_only=True)
    state = serializers.SerializerMethodField()

    class Meta:
        model = RnDProduct
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
    # static = RnDStaticSerializer(read_only=True)
    title = serializers.SerializerMethodField()
    development_cost = serializers.SerializerMethodField()
    development_duration = serializers.SerializerMethodField()
    time_spent_developing = serializers.SerializerMethodField()
    unit_mat_cost_effect = serializers.SerializerMethodField()
    production_emission_effect = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = RnDUpgrade
        fields = [
            "title",
            "development_cost",
            "development_duration",
            "time_spent_developing",
            "unit_mat_cost_effect",
            "production_emission_effect",
            "key",
            "state",
        ]

    def get_title(self, obj: RnDUpgrade):
        return obj.static.title

    def get_development_cost(self, obj: RnDUpgrade):
        return obj.static.development_cost

    def get_development_duration(self, obj: RnDUpgrade):
        return obj.static.development_duration

    def get_time_spent_developing(self, obj: RnDUpgrade):
        return obj.time_spent_developing

    def get_unit_mat_cost_effect(self, obj: RnDUpgrade):
        return obj.static.unit_mat_cost_effect

    def get_production_emission_effect(self, obj: RnDUpgrade):
        return obj.static.production_emission_effect

    def get_key(self, obj: RnDUpgrade):
        return obj.static.product_key

    def get_state(self, obj: RnDUpgrade):
        if obj.time_spent_developing == obj.static.development_duration:
            return "completed"
        elif obj.time_spent_developing < obj.static.development_duration:
            return "researching"
