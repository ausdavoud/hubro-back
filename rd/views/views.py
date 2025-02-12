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
from common.views import exceptions as common_exceptions
from common.views.services import (
    get_db_record_select_prefetch_or_404,
    get_serializer_or_400,
)
from people.models import CustomUser, Player, Team
from rd.models import DynamicRD, RDCategories
from rd.serializers import (
    CreateBaseRDSerializer,
    CreateRDProductSerializer,
    DynamicRDSerializer,
)
from rd.views import exceptions as rd_exceptions
from rd.views.services import get_previous_rd_items


@extend_schema_view(
    get_rds=extend_schema(tags=["R&D"]),
    start=extend_schema(tags=["R&D"], request=CreateRDProductSerializer),
    pause=extend_schema(tags=["R&D"], request=CreateBaseRDSerializer),
    resume=extend_schema(tags=["R&D"], request=CreateBaseRDSerializer),
)
class RDView(ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = None

    class ENDPOINTS:
        START_RD = "rd/start"
        PAUSE_RD = "rd/pause"
        RESUME_RD = "rd/resume"

    @action(methods=["get"], detail=False)
    def get_rds(self, request: Request) -> Response:
        user: CustomUser = request.user
        player: Player = get_db_record_select_prefetch_or_404(
            Player, user=user
        )
        team: Team = get_db_record_select_prefetch_or_404(
            Team, prefetch_related_tables=["rd"], id=player.team_id
        )
        current_quarter: int = team.state_variables.quarter
        dynamic_rd_objects: list[DynamicRD] | None = team.rd.all()

        previous_rd_items = get_previous_rd_items(dynamic_rd_objects)

        serialized_rd = DynamicRDSerializer(
            dynamic_rd_objects,
            many=True,
            context={
                "current_quarter": current_quarter,
                "previous_rd_items": previous_rd_items,
            },
        )
        # Data for decisions can easily be accessed via checking the state of the whole data
        response = {
            "data": serialized_rd.data,
        }
        return Response(
            response,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _is_product_rd(category: str, order: int) -> bool:
        """Check if the R&D item is of type product"""
        return category != RDCategories.PRODUCTION and order == 1

    def _get_json_body(self, data, is_start_rd: bool = False) -> dict:
        """Return a dictionary as the JSON body for the request.\n
        Since /rd/start also requires alias and icon_link,
        we need to check if the request is for starting R&D or pausing/resuming.
        Return example:
        ```
        {
            "category": "production",
            "order": 1,
            "alias": "My Fancy Production Item!",
            "icon_link": "https://example.com/icon.png",
            "engine": 0 | 1 | 2,
            "chassis": 0 | 1 | 2,
            "strap": 0 | 1 | 2,
            "engine_color: 0 | 1 | 2 | ... | 14,
            "chassis_color": 0 | 1 | 2 | ... | 14,
            "strap_color": 0 | 1 | 2 | ... | 14,
        }
        ```
        """
        base_rd_serializer = get_serializer_or_400(
            CreateBaseRDSerializer, data
        )
        category = base_rd_serializer.validated_data.get("category", None)
        order = base_rd_serializer.validated_data.get("order", None)

        if not is_start_rd:
            return {
                "category": category,
                "order": order,
            }

        # initiate the variables with none as value
        alias = None
        icon_link = None
        engine = None
        chassis = None
        strap = None
        engine_color = None
        chassis_color = None
        strap_color = None

        # simple check for being product or upgrade
        if self._is_product_rd(category, order):
            product_rd_serializer = get_serializer_or_400(
                CreateRDProductSerializer, data
            )
            alias = product_rd_serializer.validated_data.get("alias", None)
            icon_link = product_rd_serializer.validated_data.get(
                "icon_link", None
            )
            engine = product_rd_serializer.validated_data.get("engine", None)
            chassis = product_rd_serializer.validated_data.get("chassis", None)
            strap = product_rd_serializer.validated_data.get("strap", None)
            engine_color = product_rd_serializer.validated_data.get(
                "engine_color", None
            )
            chassis_color = product_rd_serializer.validated_data.get(
                "chassis_color", None
            )
            strap_color = product_rd_serializer.validated_data.get(
                "strap_color", None
            )

        json_body = {
            key: value
            for key, value in {
                "category": category,
                "order": order,
                "alias": alias,
                "icon_link": icon_link,
                "engine": engine,
                "chassis": chassis,
                "strap": strap,
                "engine_color": engine_color,
                "chassis_color": chassis_color,
                "strap_color": strap_color,
            }.items()
            if value is not None
        }

        return json_body

    def _get_decision(
        self,
        team: Team,
        current_quarter: int,
        endpoint: str,
        json_body: dict,
        contains,
    ):
        """Return a decision object from the decision pool.\n
        It uses __contained_by JSON operator. Why?\n
        At /rd/start/, json body also has alias and icon_link, but at /rd/pause/ and /rd/resume/,
        json body only has category and order.
        Therefore, this method is sometimes called with json_body that has alias and icon_link,
        and sometimes it's called with json_body that has only category and order.
        That's why sometimes we need to check if the decision inside the decision pool
        is a subset of the json_body, and other times check if the json_body is a subset of the decision.
        """
        kwargs = {
            "team": team,
            "made_at_quarter": current_quarter,
            "endpoint": endpoint,
        }
        if contains:
            kwargs["json_body__contains"] = json_body
        else:
            kwargs["json_body__contained_by"] = json_body

        return DecisionPool.objects.filter(**kwargs)

    def _create_decision(
        self,
        player: Player,
        team: Team,
        current_quarter: int,
        endpoint: str,
        json_body,
    ) -> DecisionPool:
        """Create a new decision in the DecisionPool."""
        decision, created = DecisionPool.objects.get_or_create(
            team=team,
            made_at_quarter=current_quarter,
            endpoint=endpoint,
            json_body=json_body,
            defaults={"player": player},
        )

        serialized_decision = DecisionPoolSerializer(decision)
        if not created:
            raise common_exceptions.DuplicateDecisionError(
                context={"decision": serialized_decision.data}
            )

        return decision

    @action(methods=["post"], detail=False)
    def start(self, request: Request) -> Response:
        """
        Start development of R&D
        """
        """
        Format:
        `Previous Decision` -> `Start`:
            `Action`

        `Start` -> `Start`:
            Raise error: Already started.

        `Pause` -> `Start`:
            Raise error: Can't start while paused. Because if it was paused,
            it was under development in the previous quarter.
            So it's already been started back in time.

        `Resume` -> `Start`:
            Raise error: Can't start. It's been resumed.

        `None of Above` -> `Start`:
            Create Decision object
        """

        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter: int = team.state_variables.quarter
        json_body = self._get_json_body(request.data, is_start_rd=True)

        # Pause -> Start
        if self._get_decision(
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.PAUSE_RD,
            json_body=json_body,
            contains=False,
        ).exists():
            raise rd_exceptions.RDStartError(
                "You've paused this R&D item at this quarter, so you can't start it. Maybe you want to resume it?"
            )

        # Resume -> Start
        if self._get_decision(
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.RESUME_RD,
            json_body=json_body,
            contains=False,
        ).exists():
            raise rd_exceptions.RDStartError(
                "You've resumed this R&D item at this quarter, so you can't start it. Maybe you want to pause it?"
            )

        # Start -> Start | None -> Start
        decision = self._create_decision(
            player=player,
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.START_RD,
            json_body=json_body,
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": serialized_decision.data}
        return Response(data=response, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def pause(self, request: Request) -> Response:
        """
        Pause development of R&D
        """
        """
        Format:
        `Previous Decision` -> `Start`:
            `Action`

        `Start` -> `Pause`:
            Remove start decision

        `Resume` -> `Pause`:
            Remove resume decision

        `Pause` -> `Pause`:
            Raise error: Already paused.

        `None of Above` -> `Pause`:
            Create Decision object
        """
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        json_body = self._get_json_body(request.data)

        # Start -> Pause
        start_decision = self._get_decision(
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.START_RD,
            json_body=json_body,
            contains=True,
        )
        if start_decision.exists():
            start_decision.delete()
            response = {"data": {"R&D item paused successfully"}}
            return Response(response, status=status.HTTP_200_OK)

        resume_decision = self._get_decision(
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.RESUME_RD,
            json_body=json_body,
            contains=True,
        )
        if resume_decision.exists():
            resume_decision.delete()
            response = {"data": {"R&D item paused successfully"}}
            return Response(response, status=status.HTTP_200_OK)

        # Pause -> Pause | None -> Pause
        decision = self._create_decision(
            player=player,
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.PAUSE_RD,
            json_body=json_body,
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": serialized_decision.data}
        return Response(data=response, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def resume(self, request: Request):
        """
        Resume development of R&D
        """
        """
        Format:
        `Previous Decision` -> `Resume`:
            `Action`

        `Start` -> `Resume`:
            Raise error: Can't resume. It's been started.

        `Pause` -> `Resume`:
            Remove pause decision

        `Resume` -> `Resume`:
            Raise error: Already resumed.

        `None of Above` -> `Resume`:
            Create Decision object
        """
        user: CustomUser = request.user
        player = get_db_record_select_prefetch_or_404(Player, user=user)
        team = player.team
        current_quarter = team.state_variables.quarter
        json_body = self._get_json_body(request.data)

        # Start -> Resume
        if self._get_decision(
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.START_RD,
            json_body=json_body,
            contains=True,
        ).exists():
            raise rd_exceptions.RDResumeError(
                "R&D item has not been paused (you've started development at this quarter), so you can't resume it."
            )

        # Pause -> Resume
        pause_rd_decision = self._get_decision(
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.PAUSE_RD,
            json_body=json_body,
            contains=True,
        )
        if pause_rd_decision.exists():
            pause_rd_decision.delete()
            response = {"data": {"R&D item resumed successfully"}}
            return Response(response, status=status.HTTP_200_OK)

        # Resume -> Resume | None -> Resume
        decision = self._create_decision(
            player=player,
            team=team,
            current_quarter=current_quarter,
            endpoint=self.ENDPOINTS.RESUME_RD,
            json_body=json_body,
        )
        serialized_decision = DecisionPoolSerializer(decision)
        response = {"data": serialized_decision.data}
        return Response(data=response, status=status.HTTP_200_OK)
