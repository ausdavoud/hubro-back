from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models.people import CustomUser, Player
from .models.simulation import RnDProduct, RnDStatic, RnDUpgrade
from .serializers import RnDProductSerializer, RnDStaticSerializer, RnDUpgradeSerializer, UserRegisterSerializer


class EmailExistsException(Exception):
    pass


class ShortPasswordException(Exception):
    pass


def custom_validation(data):
    print(data)
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


class RnDAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]

    def get(self, request: Request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        all_rnd_data = []

        # static objects
        static_rnd_objects = RnDStatic.objects.all()
        for static_obj in static_rnd_objects:
            rnd_product_obj = RnDProduct.objects.filter(static=static_obj, player=player).first()
            rnd_upgrade_obj = RnDUpgrade.objects.filter(static=static_obj, player=player).first()

            if not rnd_product_obj and not rnd_upgrade_obj:
                print("Nothing found")
                rnd_static_data = RnDStaticSerializer(static_obj).data
                all_rnd_data.append(rnd_static_data)
                continue
            print("found")
            if static_obj.type == RnDStatic.RnDTypes.PRODUCT:
                rnd_product_data = RnDProductSerializer(rnd_product_obj).data
                all_rnd_data.append(rnd_product_data)
                continue

            elif static_obj.type == RnDStatic.RnDTypes.UPGRADE:
                rnd_upgrade_data = RnDUpgradeSerializer(rnd_upgrade_obj).data
                all_rnd_data.append(rnd_upgrade_data)
                continue

        return Response(all_rnd_data, status=status.HTTP_200_OK)

    def post(self, request: Request):
        pass
        # is it product or upgrade

        # product creation

        # upgrade creation: has updated_product or not?

        # create ripple task to increment development time by 1
