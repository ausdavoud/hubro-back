from typing import TypedDict
from enum import Enum
import random


class ProductType(Enum):
    BASIC = "basicJetPack"
    SPORTY = "sportyJetPack"
    GREEN = "greenJetPack"
    SAFE = "safeJetPack"


class ContractType(TypedDict):

    contract_value: int
    product_count: int
    product_type: ProductType
    minimum_esg_score: int
    unit_price: int
    payment_due_date: int


def generate_contract_data(
    date: int,
    demand: int,
    contracts_number: int,
    start_unit_price_range: int,
    end_unit_price_range: int,
    required_esg: int,
    product: ProductType,
) -> list[ContractType]:
    contracts: list[ContractType] = []
    amounts = distribute_unevenly(demand, 5)
    esg_indexes = create_esg_range_list(required_esg, contracts_number)
    unit_prices = create_price_range_list(
        start_unit_price_range, end_unit_price_range, contracts_number
    )
    payment_delays = generate_payment_delays(date, contracts_number)
    for i in range(contracts_number):
        contracts.append(
            {
                "contract_value": amounts[i] * unit_prices[i],
                "product_count": amounts[i],
                "product_type": product,
                "minimum_esg_score": esg_indexes[0],
                "unit_price": unit_prices[i],
                "payment_due_date": payment_delays[i],
            }
        )
    return contracts


def calculate_priority(
    unit_price: int,
    product_count: int,
    minimum_esg_score: int,
    payment_due_date: int,
):
    FACTOR_UNIT_PRICE = 0.1
    FACTOR_PRODUCT_COUNT = 0.1
    FACTOR_MINIMUM_ESG = -0.1
    FACTOR_PAYMENT_DUO_DATE = -0.7

    priority = (
        unit_price * FACTOR_UNIT_PRICE
        + product_count * FACTOR_PRODUCT_COUNT
        + minimum_esg_score * FACTOR_MINIMUM_ESG
        + payment_due_date * FACTOR_PAYMENT_DUO_DATE
    )
    return priority


def distribute_unevenly(
    total_amount: int,
    num_parts: int,
) -> list[int]:
    if num_parts <= 0:
        raise ValueError("Number of parts must be greater than 0")
    if total_amount <= num_parts * 1000:
        raise ValueError(f"Total amount must be greater than {num_parts * 1000}")

    parts = [1000] * num_parts
    remaining = total_amount - sum(parts)
    number_of_parts_with_100 = remaining // 100

    while number_of_parts_with_100 > 0:
        i = random.randint(0, len(parts) - 1)
        parts[i] += 100
        number_of_parts_with_100 -= 1
    return parts


def generate_payment_delays(quarter: int, contract_count: int):
    delayed_contract_count = 0
    max_delay_days = 0 if quarter < 4 else 3 if quarter < 7 else 4
    payment_delays = [0] * contract_count

    if quarter < 4:
        return payment_delays

    if quarter < 7:
        delayed_contract_count = random.randint(1, 2)
    elif quarter >= 7:
        delayed_contract_count = random.randint(1, 4)

    for i in range(delayed_contract_count):
        payment_delays[i] = random.randint(1, max_delay_days)

    return payment_delays


def create_price_range_list(
    min_price: int, max_price: int, num_contracts: int
) -> list[int]:
    if min_price > max_price:
        raise ValueError("Start value must be less than or equal to end value")
    return [random.randint(min_price, max_price) for _ in range(num_contracts)]


def create_esg_range_list(max_esg: int, num_contracts: int) -> list[int]:
    ESG_RANGE = 6
    min_esg = max_esg - ESG_RANGE
    return [random.randint(min_esg, max_esg) for _ in range(num_contracts)]


contracts: list[ContractType] = generate_contract_data(
    4, 5900, 5, 228, 266, 5, ProductType.BASIC
)

priorities = []
for contract in contracts:
    priority = calculate_priority(
        contract.get("unit_price"),
        contract.get("product_count"),
        contract.get("minimum_esg_score"),
        contract.get("payment_due_date"),
    )
    priorities.append(priority)


for contract, priority in zip(contracts, priorities):
    contract["priority"] = priority

for contract in contracts:
    print(contract)
