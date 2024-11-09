import pandas as pd
from battery_handler.battery_handler import Battery

possible_cycles = 1500
battery_price = 20000
installation_cost = 0
# PGE
trade_fee_per_month = 49.90
trade_fee_per_day = trade_fee_per_month/30
additional_shit_idont_know = 0
expected_energy_usage_yearly_kWH = 3000
expected_daily_energy_usage = expected_energy_usage_yearly_kWH / 365

# import daily distribution of power use per hour
expected_daily_energy_distribution = pd.read_csv("../data/distribution.csv").values

# calculate daily usage of power in kWH per hour
hours_usage_day_kWH = expected_daily_energy_distribution * expected_daily_energy_usage
# fetching daily dynamic prices per hour per mWh
prices = pd.read_csv("../data/prices.csv")
# prices are in zl per MWh, we want them in zl per kWh
prices = prices.values / 1000
hours_cost_day_kWH = prices

# calculating K from cost equation - see backend/docs/Zalacznik-nr-2-Algorytm-wyznaczania-ceny.pdf
K_pge_kWH = 0.0812
K_month = hours_usage_day_kWH.sum() * K_pge_kWH
K_day = K_month/30

# calculating A from cost equation
A_mWH = 5
A_kwH = 5 / 1000
A_month = A_kwH * hours_usage_day_kWH.sum()
A_day = A_month/30

# battery
# battery = Battery(capacity=1000, voltage=20, power_output=230, efficiency=0.9)
# print(battery.calc_deposit_profit(prices, 2) * 30)


def calc_energy_price_daily():
    cost_energy_alone = (hours_usage_day_kWH * hours_cost_day_kWH).sum()
    return cost_energy_alone + K_day + A_day


def calc_brutto_price_daily():
    return calc_energy_price_daily() + trade_fee_per_day + additional_shit_idont_know

print(f"energy cost per day = {calc_brutto_price_daily()}")