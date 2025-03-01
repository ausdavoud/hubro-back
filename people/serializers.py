from rest_framework import serializers

from people.models import (
    CustomUser,
    Instructor,
    SimulationClass,
    SimulationClassQueue,
    Team,
)


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "password", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, clean_data):
        user = CustomUser.objects.create_user(
            email=clean_data["email"],
            password=clean_data["password"],
            role=clean_data["role"],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "simulation_class", "team_type")


class UserGeneralInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name"]


class InstructorSerializer(serializers.ModelSerializer):
    user = UserGeneralInfoSerializer()

    class Meta:
        model = Instructor
        fields = ("user",)


class SimulationClassSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True)
    instructor = InstructorSerializer()

    class Meta:
        model = SimulationClass
        fields = ("code", "name", "instructor", "mode", "teams")


class SimulationClassQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationClassQueue
        fields = ("simulation_class", "team")
