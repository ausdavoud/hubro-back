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
    try:
        ripple_task: RippleTask = player.ripple_tasks.get(rd_object=dynamic_rd_object)
        delete_response = ripple_task.delete()
    except RippleTask.DoesNotExist:
        context = {"dynamic_rd_object": str(dynamic_rd_object)}
        raise common_exceptions.DatabaseRecordNotFound(RippleTask, context)

    response = {"data": {"deleted_count": delete_response}}
    return response
