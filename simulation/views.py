from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from rest_framework.request import Request
from django.shortcuts import render
from .serializers import UserSerializer, UserRegisterSerializer
from django.contrib.auth import authenticate

UserModel = get_user_model()


def custom_validation(data):
    print(data)
    email = data["email"].strip()
    password = data["password"].strip()
    if not email or UserModel.objects.filter(email=email).exists():
        raise ValidationError("choose another email")
    if not password or len(password) < 8:
        raise ValidationError("choose another password, min 8 characters")

    return data


class UserRegister(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request: Request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                user = authenticate(
                    email=clean_data["email"], password=clean_data["password"]
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
def index(request):
    return render(request, "chat/index.html", {})


def room(request, room_name: str):
    return render(request, "chat/room.html", {"room_name": room_name})
