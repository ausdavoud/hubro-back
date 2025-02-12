# Create your views here.
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from people.models import CustomUser
from people.serializers import (
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    UserRegisterSerializer,
)
from people.views import exceptions as people_exceptions


def custom_validation(data):
    email = data["email"].strip()
    password = data["password"].strip()
    if not email or CustomUser.objects.filter(email=email).exists():
        raise people_exceptions.EmailExists(email)
    if not password or len(password) < 8:
        raise people_exceptions.ShortPassword()

    return data


@extend_schema_view(post=extend_schema(tags=["Auth"]))
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


@extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        },
    )
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@extend_schema_view(
    post=extend_schema(
        tags=["Auth"],
        responses={
            status.HTTP_200_OK: TokenRefreshResponseSerializer,
        },
    )
)
class DecoratedTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
