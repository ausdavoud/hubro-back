from ...models.common import RippleTask
from ...models.people import Player
from ...models.rd import DynamicRD
from ..exceptions import common as common_exceptions


def create_dynamic_rd_ripple_task(player: Player, run_at_quarter: int, type: str, dynamic_rd_object: DynamicRD):
    return RippleTask.objects.create(
        player=player,
        run_at_quarter=run_at_quarter,
        type=type,
        rd_object=dynamic_rd_object,
    )


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
    delete_response = player.ripple_tasks.filter(rd_object=dynamic_rd_object).delete()
    delete_count, delete_details = delete_response
    if delete_count == 0:
        context = {"dynamic_rd_object": str(dynamic_rd_object)}
        raise common_exceptions.DatabaseRecordNotFound(RippleTask, context)

    response = {"deletion_response": delete_response}
    return response
