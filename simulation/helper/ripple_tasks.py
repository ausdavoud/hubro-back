from ..models.people import Player
from ..models.rd import DynamicRD


def increment_rd_dev_time(player: Player, dynamic_rd_object: DynamicRD):
    dynamic_rd_object.time_spent_developing += 1
    dynamic_rd_object.save()

    return dynamic_rd_object
