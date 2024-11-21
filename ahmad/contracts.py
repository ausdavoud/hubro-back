import random
from enum import Enum
from typing import TypedDict

from contracts.models import Contract
from rd.models import DynamicRD


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
    product: DynamicRD,
) -> list[ContractType]:
    contracts: list[ContractType] = []
    amounts = distribute_unevenly(demand, contracts_number)
    esg_indexes = create_esg_range_list(required_esg, contracts_number)
    unit_prices = create_price_range_list(start_unit_price_range, end_unit_price_range, contracts_number)
    payment_delays = generate_payment_delays(date, contracts_number)
    for i in range(contracts_number):
        contracts.append(
            {
                "closure_quarter": date,
                "payment_quarter": payment_delays[i],
                "quantity": amounts[i],
                "unit_price": unit_prices[i],
                "total_price": amounts[i] * unit_prices[i],
                "minimum_esg_index": esg_indexes[0],
                "deliverable_product": product,
                "status": Contract.ContractStatuses.NOTASSIGNED,
            }
        )

    contracts = calculate_priorities(contracts)
    contracts = sorted(contracts, key=lambda x: x["priority"], reverse=True)
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


def calculate_priorities(contracts: list[ContractType]):
    priorities = []
    for contract in contracts:
        priority = calculate_priority(
            contract.get("unit_price"),
            contract.get("quantity"),
            contract.get("minimum_esg_index"),
            contract.get("payment_quarter"),
        )
        priorities.append(priority)

    for contract, priority in zip(contracts, priorities):
        contract["priority"] = priority

    return contracts


def distribute_unevenly(
    total_amount: int,
    num_parts: int,
) -> list[int]:
    MIN_CONTRACT_AMOUNT = 1000
    SEGMENT_SIZE = 100

    if num_parts <= 0:
        raise ValueError("Number of parts must be greater than 0")
    # Possible BUG. <= or <?
    if total_amount < num_parts * MIN_CONTRACT_AMOUNT:
        raise ValueError(f"Total amount must be greater than {num_parts * MIN_CONTRACT_AMOUNT}")

    parts = [MIN_CONTRACT_AMOUNT] * num_parts
    remaining = total_amount - sum(parts)
    number_of_parts_with_segment = remaining // SEGMENT_SIZE

    while number_of_parts_with_segment > 0:
        i = random.randint(0, len(parts) - 1)
        parts[i] += SEGMENT_SIZE
        number_of_parts_with_segment -= 1
    return parts


def generate_payment_delays(quarter: int, contract_count: int):
    delayed_contract_count = 0
    QUARTER_4 = 4
    QUARTER_7 = 7
    MAX_DELAY_QUARTERS_Q1_Q3 = 0
    MAX_DELAY_QUARTERS_Q4_Q6 = 3
    MAX_DELAY_QUARTERS_Q7_PLUS = 4
    MAX_DELAYED_CONTRACTS_Q1_Q6 = 2
    MAX_DELAYED_CONTRACTS_Q7_PLUS = 2

    max_delay_quarters = (
        MAX_DELAY_QUARTERS_Q1_Q3
        if quarter < QUARTER_4
        else (MAX_DELAY_QUARTERS_Q4_Q6 if quarter < QUARTER_7 else MAX_DELAY_QUARTERS_Q7_PLUS)
    )
    payment_delays = [0] * contract_count

    if quarter < QUARTER_4:
        return payment_delays

    if quarter < QUARTER_7:
        delayed_contract_count = random.randint(1, MAX_DELAYED_CONTRACTS_Q1_Q6)
    elif quarter >= QUARTER_7:
        delayed_contract_count = random.randint(1, MAX_DELAYED_CONTRACTS_Q7_PLUS)

    for i in range(delayed_contract_count):
        payment_delays[i] = random.randint(1, max_delay_quarters)

    return payment_delays


def create_price_range_list(min_price: int, max_price: int, num_contracts: int) -> list[int]:
    if min_price > max_price:
        raise ValueError("Start value must be less than or equal to end value")
    return [random.randint(min_price, max_price) for _ in range(num_contracts)]


def create_esg_range_list(max_esg: int, num_contracts: int) -> list[int]:
    ESG_RANGE = 6
    min_esg = max_esg - ESG_RANGE
    return [random.randint(min_esg, max_esg) for _ in range(num_contracts)]


if __name__ == "__main__":
    # how to use :

    # generate_contracts data
    contracts: list[ContractType] = generate_contract_data(
        4,
        5900,
        5,
        228,
        266,
        5,
        ProductType.BASIC,  # this is a row of the market forecast report
    )

    for contract in contracts:
        print(contract)
