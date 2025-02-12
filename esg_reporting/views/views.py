from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.models import DecisionPool
from common.serializers import DecisionPoolSerializer
from common.views.exceptions import DatabaseRecordNotFound, DuplicateDecisionError, ValidationError
from common.views.services import get_db_record_select_prefetch_or_404
from people.models import Player, Team


@extend_schema_view(
    enable_esg_reporting=extend_schema(tags=["ESG Reporting"], request=None, responses={200: DecisionPoolSerializer}),
    disable_esg_reporting=extend_schema(tags=["ESG Reporting"], request=None),
)
class ESGReportingView(ViewSet):
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [
        JWTAuthentication,
    ]
    serializer_class = None

    class ENDPOINTS:
        ENABLE_ESG_REPORTING = "esg_reporting/enable"
        DISABLE_ESG_REPORTING = "esg_reporting/disable"

    @action(methods=["post"], detail=False)
    def enable_esg_reporting(self, request: Request) -> Response:
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        serialized_decision = self._create_esg_reporting_decision(
            player=player, team=team, current_quarter=current_quarter
        )
        response = {"decision": serialized_decision}
        return Response(response, status=status.HTTP_200_OK)

    def _create_esg_reporting_decision(self, player: Player, team: Team, current_quarter) -> None:
        if current_quarter != 3:
            raise ValidationError("You can only enable ESG reporting at quarter 3.")

        decision, created = DecisionPool.objects.get_or_create(
            team=team,
            made_at_quarter=current_quarter,
            endpoint=ESGReportingView.ENDPOINTS.ENABLE_ESG_REPORTING,
            json_body={},
            defaults={"player": player},
        )
        if not created:
            raise DuplicateDecisionError(context={"duplication at": "esg_reporting"})

        serialized_decision = DecisionPoolSerializer(decision).data
        return serialized_decision

    @action(methods=["post"], detail=False)
    def disable_esg_reporting(self, request: Request) -> Response:
        user = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        serialized_deleted_decision = self._delete_esg_reporting_decision(team, current_quarter=current_quarter)
        response = {"deleted_decision": serialized_deleted_decision}
        return Response(response, status=status.HTTP_200_OK)

    def _delete_esg_reporting_decision(self, team: Team, current_quarter) -> None:
        if current_quarter != 3:
            raise ValidationError("You can only disable ESG reporting at quarter 3.")
        decision = DecisionPool.objects.filter(
            team=team,
            made_at_quarter=current_quarter,
            endpoint=ESGReportingView.ENDPOINTS.ENABLE_ESG_REPORTING,
        ).first()
        serialized_decision = DecisionPoolSerializer(decision).data
        if decision:
            decision.delete()
            return serialized_decision
        raise DatabaseRecordNotFound(DecisionPool, {"msg": "Have you started esg reporting at all?"})
