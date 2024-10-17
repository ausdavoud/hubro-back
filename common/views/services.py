from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.models import RippleTask
from common.views import exceptions as common_exceptions
from people.models import Player
from rd.models import DynamicRD


def get_serializer_or_400(serializer_class: serializers.BaseSerializer, data):
    payload_serializer: serializers.BaseSerializer = serializer_class(data=data)
    try:
        payload_serializer.is_valid(raise_exception=True)
        return payload_serializer
    except ValidationError:
        raise common_exceptions.SerializerError(payload_serializer.errors)


def increment_rd_dev_time(dynamic_rd_object: DynamicRD):
    dynamic_rd_object.time_spent_developing += 1
    dynamic_rd_object.save()

    return dynamic_rd_object


def delete_dynamic_rd_ripple_task_or_404(player: Player, dynamic_rd_object: DynamicRD):
    """
    if the player has cancelled research at the same quarter it was started,
    (meaning time_spent_developing == 0) we should set back the start_at field
    to 0, to act like it's never been started at the first place. So that
    the player can again, start the project with a possibly new alias and icon.
    """
    if dynamic_rd_object.time_spent_developing == 0:
        dynamic_rd_object.started_at = 0
        dynamic_rd_object.save()
    delete_response = player.ripple_tasks.filter(dynamic_rd_object=dynamic_rd_object).delete()
    delete_count, delete_details = delete_response
    if delete_count == 0:
        context = {"dynamic_rd_object": str(dynamic_rd_object)}
        raise common_exceptions.DatabaseRecordNotFound(RippleTask, context)

    response = {"deletion_response": delete_response}
    return response
