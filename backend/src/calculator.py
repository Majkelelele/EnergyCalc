import numpy as np
import pandas as pd
from battery_handler.battery_handler import Battery
from some_module.some_file import some_fun

possible_cycles = 1500
max_price_MWh = 1000
min_price_MWh = 100
battery_price = 20000
installation_cost = 0
# PGE
trade_fee_per_month = 49.90
additional_shit_idont_know = 0
hours_in_month = 30 * 24
hours_in_year = 12 * hours_in_month
expected_avg_cost_hour_kwh = 0.75
expected_energy_usage_yearly_kWH = 3000
expected_average_hour_usage_kWH = expected_energy_usage_yearly_kWH / hours_in_year
hours_usage_month_kWH = np.full(hours_in_month, expected_average_hour_usage_kWH)
prices = pd.read_csv("../data/prices.csv")
prices = prices.values/1000
hours_cost_month_kWH = np.tile(prices, (1, 30))
K_pge_kWH = 0.0812
K_month = hours_usage_month_kWH.sum() * K_pge_kWH
A_mWH = 5
A_kwH = 5/1000
A_month = A_kwH * hours_usage_month_kWH.sum()

# battery
battery = Battery(1000, 20, 230, 0.9)
print(battery.calc_deposit_profit(prices, 2) * 30)




def calc_energy_price_monthly():
    cost_energy_alone = (hours_usage_month_kWH * hours_cost_month_kWH.flatten()).sum()
    return cost_energy_alone + K_month + A_month


def calc_brutto_price_monthly():
    return calc_energy_price_monthly() + trade_fee_per_month + additional_shit_idont_know


print(f"energy cost per month = {calc_brutto_price_monthly()}")
some_fun()






