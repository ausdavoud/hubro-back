from common.models import DecisionPool, RippleTask
from common.views import exceptions as common_exceptions
from common.views.services import delete_dynamic_rd_ripple_task_or_404
from people.models import Player
from rd.models import DynamicRD, RDStates, StaticRD
from rd.serializers import DynamicRDSerializer
from rd.views import exceptions as rd_exceptions


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
    json_body = {"dynamic_rd_id": dynamic_rd_object.pk}
    ripple_task = RippleTask.objects.create(
        player=player,
        run_at_quarter=current_quarter + 1,
        type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
        json_body=json_body,
    )

    serialized_model = DynamicRDSerializer(dynamic_rd_object)
    return serialized_model


def start_rd(player: Player, decision: DecisionPool):
    json_body = decision.json_body
    current_quarter = decision.made_at_quarter

    # Validating category and order
    category = json_body.get("category")
    order = json_body.get("order")

    # Finding the static object for which the request has been sent
    dynamic_rd_object = get_dynamic_rd_or_404(player, category=category, order=order)

    # Validating alias and icon_link only if the request is for a product
    if dynamic_rd_object.type == StaticRD.RDTypes.PRODUCT:
        alias = json_body.get("alias")
        icon_link = json_body.get("icon_link")
        engine = json_body.get("engine")
        chassis = json_body.get("chassis")
        strap = json_body.get("strap")
        engine_color = json_body.get("engine_color")
        chassis_color = json_body.get("chassis_color")
        strap_color = json_body.get("strap_color")
        dynamic_rd_object.alias = alias
        dynamic_rd_object.icon_link = icon_link
        dynamic_rd_object.engine = engine
        dynamic_rd_object.chassis = chassis
        dynamic_rd_object.strap = strap
        dynamic_rd_object.engine_color = engine_color
        dynamic_rd_object.chassis_color = chassis_color
        dynamic_rd_object.strap_color = strap_color

    # Check if the dynamic object is available for development,
    # since only available R&D items can be developed
    dynamic_rd_objects: list[DynamicRD] | None = player.rd.all()
    previous_rd_items = get_previous_rd_items(dynamic_rd_objects)
    state = dynamic_rd_object.get_state(current_quarter, previous_rd_items)
    if state != RDStates.AVAILABLE:
        raise rd_exceptions.RDStateError(state)

    serialized_dynamic_rd_object = start_rd_development(player, dynamic_rd_object=dynamic_rd_object)

    return serialized_dynamic_rd_object


def pause_rd(player: Player, decision: DecisionPool):
    json_body = decision.json_body
    category = json_body.get("category")
    order = json_body.get("order")

    # Finding the static object for which the request has been sent
    dynamic_rd_object = get_dynamic_rd_or_404(player, category=category, order=order)
    if not dynamic_rd_object.is_researching:
        raise rd_exceptions.RDPauseError("R&D item is not being researched, so it cannot be paused")

    delete_response = delete_dynamic_rd_ripple_task_or_404(player, dynamic_rd_object)
    return delete_response


def resume_rd(player: Player, decision: DecisionPool):
    json_body = decision.json_body
    category = json_body.get("category")
    order = json_body.get("order")
    current_quarter = decision.made_at_quarter

    # Finding the static object for which the request has been sent
    dynamic_rd_object = get_dynamic_rd_or_404(player, category=category, order=order)
    if not dynamic_rd_object.is_researching:
        raise rd_exceptions.RDResumeError("The R&D item is not being researched at all, so it cannot be resumed")
    json_body = {"dynamic_rd_id": dynamic_rd_object.pk}
    try:
        ripple_task: RippleTask = player.ripple_tasks.get(json_body=json_body)
        raise rd_exceptions.RDResumeError("The R&D item is already being researched")
    except RippleTask.DoesNotExist:
        ripple_task = RippleTask.objects.create(
            player,
            run_at_quarter=current_quarter,
            type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
            json_body=json_body,
        )
        response = {"description": "Auto increment ripple task was created successfully"}
        return response
