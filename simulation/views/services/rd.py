from simulation.views.services.ripple_tasks import create_dynamic_rd_ripple_task

from ...models.common import RippleTask
from ...models.people import Player
from ...models.rd import DynamicRD, RDStates, StaticRD
from ...serializers.rd import DynamicRDSerializer
from ...views.services.common import get_serializer_or_400
from ..exceptions import common as common_exceptions
from ..exceptions import rd as rd_exceptions


def create_dynamic_rd_items(player):
    static_rd_items = StaticRD.objects.all()
    dynamic_rd_items = []

    for static in static_rd_items:
        dynamic_rd_item = DynamicRD(
            player=player,
            category=static.category,
            order=static.order,
            type=static.type,
            title=static.title,
            description=static.description,
            development_cost=static.development_cost,
            development_duration=static.development_duration,
            available_from_quarter=static.available_from_quarter,
            depreciation_time=static.depreciation_time,
            original_unit_mat_cost=static.original_unit_mat_cost,
            unit_mat_cost_effect=static.unit_mat_cost_effect,
            production_emission_effect=static.production_emission_effect,
        )
        dynamic_rd_items.append(dynamic_rd_item)

    DynamicRD.objects.bulk_create(dynamic_rd_items)


def get_previous_rd_items(dynamic_rd_objects: list[DynamicRD]):
    previous_rd_items = dict()
    for i in range(len(dynamic_rd_objects)):
        if dynamic_rd_objects[i].order == 1:
            continue
        previous_rd_items.update(
            {(dynamic_rd_objects[i].category, dynamic_rd_objects[i].order): dynamic_rd_objects[i - 1]}
        )

    return previous_rd_items


def get_dynamic_rd_or_404(player: Player, category: str, order: int):
    try:
        # Finding the dynamic object for which the request has been sent
        dynamic_rd_object: DynamicRD = player.rd.get(category=category, order=order)
        return dynamic_rd_object
    except DynamicRD.DoesNotExist:
        context = {"category": category, "order": order}
        raise common_exceptions.DatabaseRecordNotFound("DynamicRD", context)


def start_rd_development(player: Player, dynamic_rd_object: DynamicRD) -> DynamicRDSerializer:
    # Check if the dynamic object is available for development,
    # since only available R&D items can be developed
    dynamic_rd_objects: list[DynamicRD] | None = player.rd.all()
    current_quarter = player.state_variables.quarter
    previous_rd_items = get_previous_rd_items(dynamic_rd_objects)
    state = dynamic_rd_object.get_state(current_quarter, previous_rd_items)
    if state != RDStates.AVAILABLE:
        raise rd_exceptions.RDStateError(state)

    dynamic_rd_object.started_at = current_quarter
    dynamic_rd_object.save()

    # Create ripple task to increase dev time at the end of the quarter
    ripple_task = create_dynamic_rd_ripple_task(
        player=player,
        run_at_quarter=current_quarter + 1,
        type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
        dynamic_rd_object=dynamic_rd_object,
    )

    serialized_data = get_serializer_or_400(DynamicRDSerializer, dynamic_rd_object)
    return serialized_data
