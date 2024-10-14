from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models.people import CustomUser
from ..serializers.people import UserRegisterSerializer
from .exceptions import people as people_exceptions


def custom_validation(data):
    email = data["email"].strip()
    password = data["password"].strip()
    if not email or CustomUser.objects.filter(email=email).exists():
        raise people_exceptions.EmailExistsException(email)
    if not password or len(password) < 8:
        raise people_exceptions.ShortPasswordException()

    return data


@extend_schema_view(post=extend_schema(tags=["Register & Login"]))
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
                            "error": "error messages",
                            "data": "generated user",
                        },
                    )
                ],
            ),
        },
    )
    def post(self, request: Request):
        clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=clean_data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(clean_data)
            if user:
                # Return access and refresh token instead of authentication
                # Return a json without password
                refresh = RefreshToken.for_user(user)
                response = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
                return Response(response, status=status.HTTP_201_CREATED)

        raise people_exceptions.UserNotCreated(response)


# Create your views here.
def index(request):
    return render(request, "chat/index.html", {})


def room(request, room_name: str):
    return render(request, "chat/room.html", {"room_name": room_name})
