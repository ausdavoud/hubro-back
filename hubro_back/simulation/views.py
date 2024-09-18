from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth import authenticate

from .serializers import UserLoginSerializer, UserRegisterSerializer, UserSerializer

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
                user = authenticate(email=clean_data['email'], password=clean_data['password'])
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)
