from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models.people import CustomUser
from .serializers import UserRegisterSerializer


def custom_validation(data):
    print(data)
    email = data["email"].strip()
    password = data["password"].strip()
    if not email or CustomUser.objects.filter(email=email).exists():
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
                user = authenticate(email=clean_data["email"], password=clean_data["password"])
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
def index(request):
    return render(request, "chat/index.html", {})


def room(request, room_name: str):
    return render(request, "chat/room.html", {"room_name": room_name})


class RnDAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def get(self, request: Request):
        pass
        # static objects

        # product objects

        # upgrade objects

    def post(self, request: Request):
        pass
        # is it product or upgrade

        # product creation

        # upgrade creation: has updated_product or not?

        # create ripple task to increment development time by 1
