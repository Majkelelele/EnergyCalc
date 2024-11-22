import pandas as pd
from battery_handler.battery_handler import Battery
import matplotlib.pyplot as plt
from algoritms import best_algos_ever
import numpy as np
from battery_handler.krzysiek_alg.krzysieg_alg import KAlg

possible_cycles = 1500
battery_price = 20000
installation_cost = 0
current_month = "November"
# PGE
trade_fee_per_month = 49.90
trade_fee_per_day = trade_fee_per_month/30
additional_shit_idont_know = 0
expected_energy_usage_yearly_kWH = 3000
expected_daily_energy_usage = expected_energy_usage_yearly_kWH / 365
number_of_segments_daily = 24

# import daily distribution of power use per hour
solar_power_monthly = pd.read_csv("../data/SolarPower.csv")

# calculate daily usage of power in kWH per hour
energy_usage_day_kWH = pd.read_csv("../data/energy_usage.csv").values
# fetching daily dynamic prices per hour per mWh
prices = pd.read_csv("../data/prices.csv")
# prices are in zl per MWh, we want them in zl per kWh
prices = prices.values / 1000
hours_cost_day_kWH = prices

# calculating K from cost equation - see backend/docs/Zalacznik-nr-2-Algorytm-wyznaczania-ceny.pdf
K_pge_kWH = 0.0812
K_month = energy_usage_day_kWH.sum() * K_pge_kWH
K_day = K_month/30

# calculating A from cost equation
A_mWH = 5
A_kwH = 5 / 1000
A_month = A_kwH * energy_usage_day_kWH.sum()
A_day = A_month/30

def calc_energy_price_daily(solar_deduction):
    cost_energy_alone = ((energy_usage_day_kWH - solar_deduction/number_of_segments_daily) * hours_cost_day_kWH).sum()
    return cost_energy_alone + K_day + A_day

def calc_brutto_price_daily(solar_deduction):
    return calc_energy_price_daily(solar_deduction) + trade_fee_per_day + additional_shit_idont_know

# format of list [(index of period - 0:00 = 0, 0:15 = 1 ..., amount to be loaded in 15 minutes period in kwH)]
def benchmark(battery_loading, grid_loading, prices, total, battery_cost_per_kwh):
    usage_list = battery_loading + grid_loading
    sum_of_js = sum(j for _, j in usage_list)
    tolerance = 0.1
    if abs(sum_of_js - total) > tolerance:
        print("not fulffiled entire need")
    total_cost = 0
    for start, amount in usage_list:
        cost = prices[start]
        total_cost += cost * amount   
    total_cost += sum(j for _,j in battery_loading)*battery_cost_per_kwh
    return total_cost

if __name__ == "__main__":

    battery = Battery(
        price=16000, 
        capacity=10, 
        DoD=0.95, 
        efficiency=0.9, 
        life_cycles=6000
        )
   
    battery_cost_per_kwh = battery.one_kwh_cost()
    battery_time, grid_time = best_algos_ever(prices,energy_usage_day_kWH,battery_cost_per_kwh,0.6)
    bat = np.array(battery_time)
    grid = np.array(grid_time)

    energy_needed = energy_usage_day_kWH.sum()
    print(f"energy needed = {energy_needed}")


    print(f"benchmark cost dla korzystania z algosa mojego {benchmark(battery_time, grid_time, prices, energy_needed,battery_cost_per_kwh)}")

    basic = [(i, float(usage)) for i, usage in enumerate(energy_usage_day_kWH.flatten())]
    print(f"benchmark dla korzystania bezposrednio z grida = {benchmark([], basic, prices, energy_needed,battery_cost_per_kwh)}")

    ## drugi algos 
    k_alg = KAlg(charging_time=battery.charging_time, 
                 charging_per_hour=battery.charging_per_hour, 
                 charge_level=0,
                 battery_cost_per_kWh=battery_cost_per_kwh,
                 b_max_capacity=battery.capacity)
    
    charging_times, grid_times = k_alg.krzysiek_algorithm(prices, energy_usage_day_kWH)
    
    charge_sum = sum(j for _, j in charging_times)
    print(f"charge sum = {charge_sum}")

    bat2 = np.array(charging_times)
    grid2 = np.array(grid_times)
    
    print(f"benchmark cost dla korzystania z algosa krzyska {benchmark(charging_times, grid_times, prices, energy_needed, battery_cost_per_kwh)}")

