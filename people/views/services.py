from django.db.models import Prefetch

from common.views import exceptions as common_exceptions
from people.models import CustomUser, Player


def get_player_or_404(user: CustomUser, prefetch_related_tables: list[str | Prefetch] = []):
    try:
        return Player.objects.prefetch_related(*prefetch_related_tables).get(user=user)
    except Player.DoesNotExist:
        context = {"user_email": user.email}
        raise common_exceptions.DatabaseRecordNotFound(Player, context)
