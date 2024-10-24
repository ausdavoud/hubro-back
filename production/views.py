from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication


@extend_schema_view(get_factories=extend_schema(tags=["Factory"], request=...))
class ProductionView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(["GET"], detail=False)
    def get_factories(self, request: Request) -> Response:
        return Response({"factories": []})
