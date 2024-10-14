from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ...models.people import CustomUser, Player
from ..exceptions import common as common_exceptions


def get_player_or_404(user: CustomUser, prefetch_related_tables: list[str] = ["rd", "state_variables"]):
    try:
        return Player.objects.prefetch_related(*prefetch_related_tables).get(user=user)
    except Player.DoesNotExist:
        context = {"user_email": user.email}
        raise common_exceptions.DatabaseRecordNotFound(Player, context)


def get_serializer_or_400(serializer_class: serializers.BaseSerializer, data):
    payload_serializer: serializers.BaseSerializer = serializer_class(data=data)
    try:
        payload_serializer.is_valid(raise_exception=True)
        return payload_serializer
    except ValidationError:
        raise common_exceptions.SerializerError(payload_serializer.errors)
