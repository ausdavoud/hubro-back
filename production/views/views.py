from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

# import GenericAPIView
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool
from common.serializers import DecisionPoolSerializer
from common.views import exceptions as common_exceptions
from common.views.services import get_serializer_or_400
from people.models import CustomUser, Player
from people.views.services import get_player_or_404
from production.models import Factory
from production.serializers import (
    FactorySerializer,
    NewFactorySerializer,
    SelectProductSerializer,
    SellFactorySerializer,
    SetActivityLevelSerializer,
)


@extend_schema_view(
    get_factories=extend_schema(tags=["Production"]),
    new_factory=extend_schema(tags=["Production"], request=NewFactorySerializer),
    cancel_new_factory=extend_schema(tags=["Production"]),
    sell_factory=extend_schema(tags=["Production"], request=SellFactorySerializer),
    cancel_sell_factory=extend_schema(tags=["Production"], request=SellFactorySerializer),
    select_product=extend_schema(tags=["Production"], request=SelectProductSerializer),
    set_activity_level=extend_schema(tags=["Production"], request=SetActivityLevelSerializer),
)
class ProductionView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    class ENDPOINTS:
        GET_FACTORY = "production/get_factories"
        NEW_FACTORY = "production/new_factory"
        SELL_FACTORY = "production/sell_factory"
        SELECT_PRODUCT = "production/select_product"
        SET_ACTIVITY_LEVEL = "production/set_activity_level"

    @action(["GET"], detail=False)
    def get_factories(self, request: Request) -> Response:
        user = request.user
        player = get_player_or_404(user)
        factories = Factory.objects.filter(player=player)
        serialized_factories = FactorySerializer(factories, many=True)
        response = {"data": serialized_factories.data}
        return Response(response, status=status.HTTP_200_OK)

    @action(["POST"], detail=False)
    def new_factory(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter: int = player.state_variables.quarter
        json_body = self._get_new_factory_json_body(request.data)

        decision = self._create_new_factory_decision(
            player=player, current_quarter=current_quarter, endpoint=self.ENDPOINTS.NEW_FACTORY, json_body=json_body
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_201_CREATED)

    def _get_new_factory_json_body(self, data):
        serialized_data = get_serializer_or_400(NewFactorySerializer, data)
        ownership = serialized_data.validated_data["ownership"]

        json_body = {"ownership": ownership}
        return json_body

    def _create_new_factory_decision(self, player: Player, current_quarter: int, endpoint: str, json_body: dict):
        """Why not get_or_create? See finance.views.views._create_decision docs"""
        try:
            previous_decision = DecisionPool.objects.get(
                player=player, made_at_quarter=current_quarter, endpoint=endpoint
            )
            serialized_decision = DecisionPoolSerializer(previous_decision)
            raise common_exceptions.DuplicateDecision(context={"decision": serialized_decision.data})
        except DecisionPool.DoesNotExist:
            decision = DecisionPool.objects.create(
                player=player, made_at_quarter=current_quarter, endpoint=endpoint, json_body=json_body
            )
            return decision

    @action(["POST"], detail=False)
    def cancel_new_factory(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter: int = player.state_variables.quarter

        serialized_deleted_decision = self._delete_new_factory_decision(player=player, current_quarter=current_quarter)
        response = {
            "data": {
                "message": "Building new factory cancelled successfully",
                "canceled_factory": serialized_deleted_decision,
            }
        }
        return Response(response, status=status.HTTP_200_OK)

    def _delete_new_factory_decision(self, player: Player, current_quarter: int) -> dict:
        """Cancel the factory that was gonna be built at this quarter"""

        try:
            decision = DecisionPool.objects.get(
                player=player, made_at_quarter=current_quarter, endpoint=self.ENDPOINTS.NEW_FACTORY
            )
            serialized_decision = DecisionPoolSerializer(decision)
            serialized_decision_data = serialized_decision.data
            decision.delete()
            return serialized_decision_data
        except DecisionPool.DoesNotExist:
            raise common_exceptions.DatabaseRecordNotFound(
                DecisionPool, context={"endpoint": self.ENDPOINTS.NEW_FACTORY}
            )

    # Sell Factory

    @action(["POST"], detail=False)
    def sell_factory(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter

        json_body = self._get_sell_factory_json_body(request.data)

        decision = self._create_sell_factory_decision(
            player=player, current_quarter=current_quarter, endpoint=self.ENDPOINTS.SELL_FACTORY, json_body=json_body
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_201_CREATED)

    def _get_sell_factory_json_body(self, data):
        serialized_data = get_serializer_or_400(SellFactorySerializer, data)
        factory_id = serialized_data.validated_data["factory_id"]
        json_body = {"factory_id": factory_id}
        return json_body

    def _create_sell_factory_decision(self, player: Player, current_quarter: int, endpoint: str, json_body: dict):
        decision, created = DecisionPool.objects.get_or_create(
            player=player, made_at_quarter=current_quarter, endpoint=endpoint, json_body=json_body
        )
        if not created:
            serialized_decision = DecisionPoolSerializer(decision)
            raise common_exceptions.DuplicateDecision(context={"decision": serialized_decision.data})

        return decision

    @action(["POST"], detail=False)
    def cancel_sell_factory(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter

        json_body = self._get_sell_factory_json_body(request.data)

        serialized_decision_data = self._delete_sell_factory_decision(
            player=player, current_quarter=current_quarter, json_body=json_body
        )

        response = {
            "data": {
                "message": "Selling factory was canceled successfully",
                "deleted_decision": serialized_decision_data,
            }
        }
        return Response(response, status=status.HTTP_200_OK)

    def _delete_sell_factory_decision(self, player: Player, current_quarter: int, json_body: dict):
        """Cancel the factory that was going be sold at this quarter
        Serialize the decision before deletion to keep the id for the response
        """

        try:
            decision = DecisionPool.objects.get(
                player=player, made_at_quarter=current_quarter, endpoint=self.ENDPOINTS.SELL_FACTORY
            )
            serialized_decision = DecisionPoolSerializer(decision)
            serialized_decision_data = serialized_decision.data
            decision.delete()
            return serialized_decision_data
        except DecisionPool.DoesNotExist:
            raise common_exceptions.DatabaseRecordNotFound(
                DecisionPool, context={"endpoint": self.ENDPOINTS.SELL_FACTORY}
            )

    @action(["POST"], detail=False)
    def select_product(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter

        json_body = self._get_select_product_json_body(request.data)

        decision = self._create_select_product_decision(
            player=player, current_quarter=current_quarter, endpoint=self.ENDPOINTS.SELECT_PRODUCT, json_body=json_body
        )

        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_201_CREATED)

    def _get_select_product_json_body(self, data) -> dict:
        serialized_data = get_serializer_or_400(SelectProductSerializer, data)
        factory_id = serialized_data.validated_data["factory_id"]
        product_id = serialized_data.validated_data["product_id"]
        json_body = {"factory_id": factory_id, "product_id": product_id}
        return json_body

    def _create_select_product_decision(self, player: Player, current_quarter: int, endpoint: str, json_body: dict):
        try:
            decision = DecisionPool.objects.get(
                player=player,
                made_at_quarter=current_quarter,
                endpoint=endpoint,
                json_body__factory_id=json_body["factory_id"],
            )

            if decision.json_body["product_id"] == json_body["product_id"]:
                serialized_decision = DecisionPoolSerializer(decision)
                raise common_exceptions.DuplicateDecision(context={"decision": serialized_decision.data})

            decision.json_body["product_id"] = json_body["product_id"]
            decision.save()
            return decision

        except DecisionPool.DoesNotExist:
            decision = DecisionPool.objects.create(
                player=player, made_at_quarter=current_quarter, endpoint=endpoint, json_body=json_body
            )
            return decision

    @action(["POST"], detail=False)
    def set_activity_level(self, request: Request) -> Response:
        user: CustomUser = request.user
        player = get_player_or_404(user)
        current_quarter = player.state_variables.quarter

        json_body = self._get_activity_level_json_body(request.data)

        decision = self._create_set_activity_level_decision(
            player=player,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.SET_ACTIVITY_LEVEL,
            json_body=json_body,
        )

        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": {"decision": serialized_decision.data}}
        return Response(response, status=status.HTTP_201_CREATED)

    def _get_activity_level_json_body(self, data) -> dict:
        """POSSIBLE BUG
        Here we needed to convert decimal to str to avoid encoding errors.
        But what about other endpoints that receive and store decimal?
        """
        serialized_data = get_serializer_or_400(SetActivityLevelSerializer, data)
        factory_id = serialized_data.validated_data["factory_id"]
        activity_level = serialized_data.validated_data["activity_level"]
        json_body = {"factory_id": factory_id, "activity_level": str(activity_level)}
        return json_body

    def _create_set_activity_level_decision(self, player: Player, current_quarter: int, endpoint: str, json_body: dict):
        """If the decision is already made, update it; Otherwise create a new one"""
        try:
            decision = DecisionPool.objects.get(
                player=player,
                made_at_quarter=current_quarter,
                endpoint=endpoint,
                json_body__factory_id=json_body["factory_id"],
            )

            if decision.json_body["activity_level"] == json_body["activity_level"]:
                serialized_decision = DecisionPoolSerializer(decision)
                raise common_exceptions.DuplicateDecision(context={"decision": serialized_decision.data})

            decision.json_body["activity_level"] = json_body["activity_level"]
            decision.save()
            return decision

        except DecisionPool.DoesNotExist:
            decision = DecisionPool.objects.create(
                player=player, made_at_quarter=current_quarter, endpoint=endpoint, json_body=json_body
            )
            return decision
