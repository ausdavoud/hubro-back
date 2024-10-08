from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.people import CustomUser
from ..serializers.people import UserRegisterSerializer


class EmailExistsException(Exception):
    pass


class ShortPasswordException(Exception):
    pass


def custom_validation(data):
    email = data["email"].strip()
    password = data["password"].strip()
    if not email or CustomUser.objects.filter(email=email).exists():
        raise EmailExistsException("choose another email")
    if not password or len(password) < 8:
        raise ShortPasswordException("choose another password, min 8 characters")

    return data


class UserRegister(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = UserRegisterSerializer

    @extend_schema(
        responses={
            200: UserRegisterSerializer,
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        name="Bad Request",
                        value={
                            "type": "error",
                            "data": "email is not valid or already exists",
                        },
                    )
                ],
            ),
        },
    )
    def post(self, request: Request):
        try:
            clean_data = custom_validation(request.data)
        except EmailExistsException:
            return Response(
                {"type": "error", "data": "email is not valid or already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ShortPasswordException:
            return Response({"type": "error", "data": "password is too short"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                # Return access and refresh token instead of authentication
                # Return a json without password
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


# Create your views here.
def index(request):
    return render(request, "chat/index.html", {})


def room(request, room_name: str):
    return render(request, "chat/room.html", {"room_name": room_name})
