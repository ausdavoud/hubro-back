from simulation.models.rd import DynamicRD, StaticRD


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
