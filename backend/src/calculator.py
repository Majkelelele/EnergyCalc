import pandas as pd
from battery_handler.battery_handler import Battery
import matplotlib.pyplot as plt
from algoritms import best_algos_ever
import numpy as np
from battery_handler.krzysiek_alg.krzysieg_alg import KAlg
from typing import List
import glob
import os



# def krzysieg_alg():
    
#     all_energy_needed = []
#     all_from_alg_cost = []
#     all_from_grid_cost = []
#     charge_level = 0

#     for i in range(1, 8):
#         battery = Battery(
#             price=16000, 
#             capacity=10, 
#             DoD=0.95, 
#             efficiency=0.9, 
#             life_cycles=6000,
#             charge_level=charge_level
#             )

#         battery_cost_per_kwh = battery.one_kwh_cost()

#         # k_alg = KAlg(charging_time=battery.charging_time, 
#         #             charging_per_hour=battery.charging_per_hour, 
#         #             charge_level=battery.charge_level,
#         #             battery_cost_per_kWh=battery_cost_per_kwh,
#         #             b_max_capacity=battery.capacity)

#         price_file_name = "prices" + str(i) + ".csv"
#         prices = pd.read_csv("../data/" + price_file_name)
#         prices["price"] = prices["price"] / 1000
#         prices = prices.values

#         usage_file_name = "energy_usage" + str(i) + ".csv"
#         energy_usage = pd.read_csv("../data/" + usage_file_name).values

#         # battery_time, grid_time, alg_cost = k_alg.krzysiek_algorithm(prices, energy_usage)

#         energy_needed = energy_usage.sum()
#         all_energy_needed.append(energy_needed)

#         all_from_alg_cost.append(alg_cost)

#         basic = [(i, float(usage)) for i, usage in 
#                     enumerate(energy_usage.flatten())]
#         grid_cost = benchmark([], 
#                               basic, 
#                               prices, 
#                               energy_needed, 
#                               battery_cost_per_kwh)
#         all_from_grid_cost.append(grid_cost)

#         charge_level = k_alg.charge_level

#     print(f"sum of cost only from grid = {sum(all_from_grid_cost)}, sum of cost from alg = {sum(all_from_alg_cost)}")

#     return all_energy_needed, all_from_grid_cost, all_from_alg_cost

# benchmark accepts two lists, each list contains pairs - (index of 15min period in 24h - starting from 00:00, ending 23:45 -> 96 indices posibles):
# 1) - battery_loading - at given index, how much power to load battery -> price at loading time, not using time;
# 2) - grid_loading - the same but when using energy directly from grid
# 3) prices is a list of prices at given 15min period (96indices)

def benchmark(battery_loading, grid_loading, prices, max_load_15min, total, battery_cost_per_kwh):
    usage_list = battery_loading + grid_loading
    sum_of_js = sum(j for _, j in usage_list)
    tol = 0.01
    # ensuring correct input
    assert not (total - sum_of_js  > tol), "Not fulfilled entire need"
    assert not (sum_of_js - total > tol), f"loading too much energy: energy needed {total}, energy loaded = {sum_of_js}"
    load_per_index = {}
    for start, amount in usage_list:
        load_per_index[start] = load_per_index.get(start, 0) + amount
        # assert load_per_index[start] <= max_load_15min + tol, f"Exceeded max load of {max_load_15min} at index {start}, with value = {load_per_index[start]}" 
        # if load_per_index[start] > max_load_15min + tol:
        #     print(f"Exceeded max load of {max_load_15min} at index {start}, with value = {load_per_index[start]}" )


    total_cost = 0
    for start, amount in grid_loading:
        cost = prices[start]
        total_cost += cost * amount   
    for start, amount in battery_loading:
        cost = prices[start]
        total_cost += (cost + battery_cost_per_kwh) * amount

    return total_cost

if __name__ == "__main__":
    
    grants = []

    battery = Battery(
        price=16000, 
        capacity=10, 
        DoD=0.95, 
        efficiency=0.9, 
        life_cycles=6000,
        grant_reduction=8000
        )
   
    battery_cost_per_kwh = battery.one_kwh_cost()

    usage_pattern = "../data/energy_usage*.csv"
    usage_files = sorted(glob.glob(usage_pattern))
    #ensuring that files are starting from day 0, and ascending
    prices_pattern = "../data_months/day_*.csv"
    prices_files = sorted(glob.glob(prices_pattern))



    # expected amount to be loaded in entire 15 min period
    max_load_15min = battery.charging_per_segment()

    results_only_grid = []
    # results_krzysiek = []
    results_michal = []

    for i, (f_price, f_usage) in enumerate(zip(prices_files, usage_files)):
        print(f"DAY {i}")
        # converting to prices per kWh
        prices = ((pd.read_csv(f_price).values / 1000).flatten()).tolist() 
        print(f"prices file = {f_price}")
        # usage already in kWh
        usage = (pd.read_csv(f_usage).values).flatten().tolist()
        total = sum(usage)
        
        basic_grid_time = [(i, float(usage)) for i, usage in 
                    enumerate(usage)]
        
        res = round(benchmark([],basic_grid_time,prices,max_load_15min,total,battery_cost_per_kwh),3)
        results_only_grid.append(res)
        print(f"total cost of stupid using only grid = {res}")

        battery_time, grid_time = best_algos_ever(prices,usage,battery_cost_per_kwh,max_load_15min)
        res = round(benchmark(battery_time,grid_time,prices,max_load_15min,total,battery_cost_per_kwh),3)
        results_michal.append(res)
        print(f"total cost of best algos ever = {res}")

        # k_alg = KAlg(charging_time=battery.charging_time, 
        #             charging_per_hour=battery.charging_per_hour, 
        #             charge_level=battery.charge_level,
        #             battery_cost_per_kWh=battery_cost_per_kwh,
        #             b_max_capacity=battery.capacity)

        # battery_time, grid_time, alg_cost = k_alg.krzysiek_algorithm(prices, usage)
        # res = round(alg_cost,3)
        # results_krzysiek.append(res)
        # print(f"total cost of krzysiek's algos = {res}")
