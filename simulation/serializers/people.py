from django.contrib.auth import authenticate
from django.forms import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from ..models.people import CustomUser


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


@extend_schema_view(
    post=extend_schema(
        tags=["Register & Login"],
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        },
    )
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


@extend_schema_view(
    post=extend_schema(
        tags=["Register & Login"],
        responses={
            status.HTTP_200_OK: TokenRefreshResponseSerializer,
        },
    )
)
class DecoratedTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, clean_data):
        user = CustomUser.objects.create_user(
            email=clean_data["email"], password=clean_data["password"], role=clean_data["role"]
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name"]
