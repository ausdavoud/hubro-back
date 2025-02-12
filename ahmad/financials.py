from decimal import Decimal


def calculate_interest(
    payback_period: float,
    esg_index: float,
    simulation_duration: float,
    current_quarter: float,
) -> float:
    ESG_INDEX_FACTOR = 3
    MATURITY_FACTOR = 2
    PAYBACK_FACTOR = 1
    FIXED_INTEREST = 2
    MAX_LOAN_REPAYMENT = 16

    esg_component = ESG_INDEX_FACTOR * (1 - (esg_index / 100))
    maturity_component = (
        MATURITY_FACTOR * (1 - current_quarter)
    ) / simulation_duration
    payback_component = PAYBACK_FACTOR * (payback_period / MAX_LOAN_REPAYMENT)

    return (
        esg_component + maturity_component + payback_component + FIXED_INTEREST
    )


def calculate_payback_per_quarter(
    payback_period: float, interest: float, amount: Decimal
) -> float:
    interest_rate_base = (interest / 100) + 1
    power_component = sum(
        1 / (interest_rate_base ** (i + 1)) for i in range(payback_period)
    )
    decimal_power_component = Decimal(power_component)
    return amount / decimal_power_component


if __name__ == "__main__":
    esg_index = 30
    current_quarter = 4
    simulation_duration = 20

    interest = calculate_interest(
        16, esg_index, simulation_duration, current_quarter
    )
    payback_per_quarter = calculate_payback_per_quarter(16, interest, 1000000)

    print({"interest": interest, "payback_per_quarter": payback_per_quarter})
