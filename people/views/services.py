from django.db.models import Prefetch

from common.views import exceptions as common_exceptions
from people.models import CustomUser, Player, Team


def get_player_or_404(
    user: CustomUser, prefetch_related_tables: list[str | Prefetch] = [], select_related_tables: list[str] = []
) -> Player:
    try:
        return (
            Player.objects.prefetch_related(*prefetch_related_tables)
            .select_related(*select_related_tables)
            .get(user=user)
        )
    except Player.DoesNotExist:
        context = {"user_email": user.email}
        raise common_exceptions.DatabaseRecordNotFound(Player, context)


def get_simulation_teams(team: Team) -> list[Team]:
    """
    Returns a list of teams that are in the same simulation as the given team.
    """
    return Team.objects.filter(simulation_class=team.simulation_class).exclude(pk=team.pk)
