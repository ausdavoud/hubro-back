import sys


MATERIALS = {
    "standard": {"price": 100.00, "emissions": 0.40},
    "eco": {"price": 115.00, "emissions": 0.26},
    "gaia": {"price": 130.00, "emissions": 0.16},
}


def calculate_esg_index(production, material: str) -> float:
    max_emissions = 0
    current_emissions = 0

    for prod in production:

        max_production_emissions = prod["amount"] * 0.5
        max_material_emissions = prod["amount"] * MATERIALS["standard"].get("emissions")
        max_emissions += max_production_emissions + max_material_emissions

        current_production_emissions = prod["amount"] * prod["emission_per_unit"]
        current_material_emissions = prod["amount"] * MATERIALS[material].get(
            "emissions"
        )
        current_emissions += current_production_emissions + current_material_emissions

    emission_reduction = max_emissions - current_emissions
    return round((emission_reduction / max_emissions) * 100, 2)


production = [
    {"amount": 1000, "emission_per_unit": 0.5},
    {"amount": 1000, "emission_per_unit": 0.4},
    {"amount": 1000, "emission_per_unit": 0.4},
]

mat = sys.argv[1] if len(sys.argv) > 1 else "standard"
res = calculate_esg_index(production, mat)
print(res)
