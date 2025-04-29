from math import ceil
from battery_handler.battery_handler import Battery

# --- PLN-based coefficients ---
FIXED_COST_PLN         = 1_260          # zł  (inverter, BMS, install)
VARIABLE_COST_PLN_PKWH = 1_270          # zł/kWh  (cells + casing)
DOD_BASE               = 0.93
EFF_BASE               = 0.96
CYCLES_BASE            = 6_000

def make_battery(capacity_kwh: float) -> Battery:
    price = FIXED_COST_PLN + VARIABLE_COST_PLN_PKWH * capacity_kwh
    dod   = DOD_BASE + (0.02 if capacity_kwh < 3 else 0)
    eff   = EFF_BASE - 0.005 * max(0, capacity_kwh - 8) / 8
    cycles = CYCLES_BASE + ceil(max(0, 4 - capacity_kwh) * 500)

    return Battery(
        price=round(price, 0),
        capacity=capacity_kwh,
        DoD=round(dod, 2),
        efficiency=round(eff, 3),
        life_cycles=cycles,
        is_grant_reduction=True,
    )