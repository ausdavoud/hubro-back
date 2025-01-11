from django.db.models import F

from common.management.data_fixtures import STATIC_RD
from common.models import DecisionPool, RippleTask
from common.serializers import RippleTaskSerializer
from common.views import exceptions as common_exceptions
from common.views.services import delete_dynamic_rd_ripple_task_or_404
from people.models import Team
from rd.models import DynamicRD
from rd.serializers import DynamicRDSerializer
from rd.views import exceptions as rd_exceptions
from suppliers.models import Supplier


def create_dynamic_rd_items(team: Team):
    dynamic_rd_items = []

    for static in STATIC_RD:
        supplier_tuple = static.get("supplier")
        if supplier_tuple:
            supplier_rd_category = supplier_tuple[0]
            supplier_name = supplier_tuple[1]

        supplier = Supplier.objects.get(rd_category=supplier_rd_category, name=supplier_name)
        dynamic_rd_item = DynamicRD(
            team=team,
            category=static["category"],
            order=static["order"],
            type=static["type"],
            title=static["title"],
            description=static["description"],
            development_cost=static["development_cost"],
            development_duration=static["development_duration"],
            available_from_quarter=static.get("available_from_quarter", None),
            depreciation_time=static["depreciation_time"],
            supplier=supplier if supplier else None,
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


def get_dynamic_rd_or_404(team: Team, category: str, order: int):
    try:
        # Finding the dynamic object for which the request has been sent
        dynamic_rd_object: DynamicRD = team.rd.get(category=category, order=order)
        return dynamic_rd_object
    except DynamicRD.DoesNotExist:
        context = {"category": category, "order": order}
        raise common_exceptions.DatabaseRecordNotFound("DynamicRD", context)


def start_rd_development(team: Team, dynamic_rd_object: DynamicRD) -> DynamicRDSerializer:
    # Check if the dynamic object is available for development,
    # since only available R&D items can be developed
    dynamic_rd_objects: list[DynamicRD] | None = team.rd.all()
    current_quarter = team.state_variables.quarter
    previous_rd_items = get_previous_rd_items(dynamic_rd_objects)
    state = dynamic_rd_object.get_state(current_quarter, previous_rd_items)
    if state != DynamicRD.RDStates.AVAILABLE:
        raise rd_exceptions.RDStateError(state)

    dynamic_rd_object.started_at = current_quarter
    dynamic_rd_object.save()

    # Create ripple task to increase dev time at the end of the quarter
    json_body = {"dynamic_rd_id": dynamic_rd_object.pk}
    ripple_task = RippleTask.objects.create(
        team=team,
        run_at_quarter=current_quarter,
        type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
        json_body=json_body,
    )

    serialized_model = DynamicRDSerializer(dynamic_rd_object)
    return serialized_model


def start_rd(team: Team, decision: DecisionPool):
    json_body = decision.json_body
    current_quarter = decision.made_at_quarter

    # Validating category and order
    category = json_body.get("category")
    order = json_body.get("order")

    # Finding the static object for which the request has been sent
    dynamic_rd_object = get_dynamic_rd_or_404(team=team, category=category, order=order)

    # Validating alias and icon_link only if the request is for a product
    if dynamic_rd_object.type == DynamicRD.RDTypes.PRODUCT:
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
    dynamic_rd_objects: list[DynamicRD] | None = team.rd.all()
    previous_rd_items = get_previous_rd_items(dynamic_rd_objects)
    state = dynamic_rd_object.get_state(current_quarter, previous_rd_items)
    if state != DynamicRD.RDStates.AVAILABLE:
        raise rd_exceptions.RDStateError(state)

    serialized_dynamic_rd_object = start_rd_development(team, dynamic_rd_object=dynamic_rd_object)

    return serialized_dynamic_rd_object


def pause_rd(team: Team, decision: DecisionPool):
    json_body = decision.json_body
    category = json_body.get("category")
    order = json_body.get("order")

    # Finding the static object for which the request has been sent
    dynamic_rd_object = get_dynamic_rd_or_404(team, category=category, order=order)
    if not dynamic_rd_object.is_researching:
        raise rd_exceptions.RDPauseError("R&D item is not being researched, so it cannot be paused")

    delete_response = delete_dynamic_rd_ripple_task_or_404(team, dynamic_rd_object)
    return delete_response


def resume_rd(team: Team, decision: DecisionPool):
    json_body = decision.json_body
    category = json_body.get("category")
    order = json_body.get("order")
    current_quarter = decision.made_at_quarter

    # Finding the static object for which the request has been sent
    dynamic_rd_object = get_dynamic_rd_or_404(team, category=category, order=order)
    if not dynamic_rd_object.is_researching:
        raise rd_exceptions.RDResumeError("The R&D item is not being researched at all, so it cannot be resumed")
    json_body = {"dynamic_rd_id": dynamic_rd_object.pk}
    try:
        ripple_task: RippleTask = team.ripple_tasks.get(json_body=json_body)
        raise rd_exceptions.RDResumeError("The R&D item is already being researched")
    except RippleTask.DoesNotExist:
        ripple_task = RippleTask.objects.create(
            team=team,
            run_at_quarter=current_quarter,
            type=RippleTask.TaskTypes.INCREMENT_RD_DEV_TIME,
            json_body=json_body,
        )
        response = RippleTaskSerializer(ripple_task).data
        return response


def get_available_rd_dynamics_at_next_quarter(team: Team, current_quarter: int):
    from rd.views.views import RDView

    # development_duration - time_spent_developing <= 1 and started_at is not zero
    dynamic_rd_objects = DynamicRD.objects.filter(
        team=team,
        type=DynamicRD.RDTypes.PRODUCT,
        development_duration__lte=F("time_spent_developing") + 1,
        started_at__gte=1,
    )

    # start decision was made for a product that has a development time of 1
    current_quarter_rd_decisions = DecisionPool.objects.filter(
        team=team,
        made_at_quarter=current_quarter,
        endpoint=RDView.ENDPOINTS.START_RD,
    )
    for rd_decision in current_quarter_rd_decisions:
        category = rd_decision.json_body["category"]
        order = rd_decision.json_body["order"]
        dynamic_rd_objects |= DynamicRD.objects.filter(
            team=team,
            type=DynamicRD.RDTypes.PRODUCT,
            category=category,
            order=order,
            development_duration=1,
        )

    return dynamic_rd_objects
