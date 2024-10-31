import math


def calculate_mat_COSTS(base_cost):
    MID_QUALITY_FACTOR = 1.15
    HIGH_QUALITY_FACTOR = 1.3
    return {
        "low": math.ceil(base_cost),
        "mid": math.ceil(base_cost * MID_QUALITY_FACTOR),
        "high": math.ceil(base_cost * HIGH_QUALITY_FACTOR),
    }


if __name__ == "__main__":
    JET_PACK_BASIC_MAT_COST = 100
    JET_PACK_SPORTY_MAT_COST = 160
    JET_PACK_GREEN_MAT_COST = 120
    JET_PACK_SAFE_MAT_COST = 140

    res = calculate_mat_COSTS(JET_PACK_GREEN_MAT_COST)
    print(res)
