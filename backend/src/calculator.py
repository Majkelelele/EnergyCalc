import pandas as pd
from battery_handler.battery_handler import Battery
import matplotlib.pyplot as plt
from algoritms import best_algos_ever
import numpy as np
from battery_handler.krzysiek_alg.krzysieg_alg import KAlg
from typing import List
import glob


# possible_cycles = 1500
# battery_price = 20000
# installation_cost = 0
# current_month = "November"
# # PGE
# trade_fee_per_month = 49.90
# trade_fee_per_day = trade_fee_per_month/30
# additional_shit_idont_know = 0
# expected_energy_usage_yearly_kWH = 3000
# expected_daily_energy_usage = expected_energy_usage_yearly_kWH / 365
# number_of_segments_daily = 24

# import daily distribution of power use per hour
# solar_power_monthly = pd.read_csv("../data/SolarPower.csv")

# # calculate daily usage of power in kWH per hour
# energy_usage_day_kWH = pd.read_csv("../data/energy_usage.csv").values
# # fetching daily dynamic prices per hour per mWh
# prices = pd.read_csv("../data/prices.csv")
# # prices are in zl per MWh, we want them in zl per kWh
# prices = prices.values / 1000
# hours_cost_day_kWH = prices

# # calculating K from cost equation - see backend/docs/Zalacznik-nr-2-Algorytm-wyznaczania-ceny.pdf
# K_pge_kWH = 0.0812
# K_month = energy_usage_day_kWH.sum() * K_pge_kWH
# K_day = K_month/30

# # calculating A from cost equation
# A_mWH = 5
# A_kwH = 5 / 1000
# A_month = A_kwH * energy_usage_day_kWH.sum()
# A_day = A_month/30

# def calc_energy_price_daily(solar_deduction):
#     cost_energy_alone = ((energy_usage_day_kWH - solar_deduction/number_of_segments_daily) * hours_cost_day_kWH).sum()
#     return cost_energy_alone + K_day + A_day

# def calc_brutto_price_daily(solar_deduction):
#     return calc_energy_price_daily(solar_deduction) + trade_fee_per_day + additional_shit_idont_know

# format of list [(index of period - 0:00 = 0, 0:15 = 1 ..., amount to be loaded in 15 minutes period in kwH)]
# note indexes only if loading amount greater than 0
# total arguments means total energy needed in a given period
def benchmark(battery_loading, grid_loading, prices, total, battery_cost_per_kwh):
    usage_list = battery_loading + grid_loading
    sum_of_js = sum(j for _, j in usage_list)
    tolerance = 0.1
    if sum_of_js - total < -tolerance:
        print("not fulffiled entire need")
    if sum_of_js - total > tolerance:
        print(f"loading too much energy: energy needed {total}, energy loaded = {sum_of_js}")
    total_cost = 0
    for start, amount in grid_loading:
        cost = prices[start]
        total_cost += cost * amount   
    for start, amount in battery_loading:
        cost = prices[start]
        total_cost += (cost + battery_cost_per_kwh) * amount

    return float(total_cost[0])

def michal_alg():
    battery = Battery(
        price=16000, 
        capacity=10, 
        DoD=0.95, 
        efficiency=0.9, 
        life_cycles=6000
        )
    
    all_energy_needed = []
    all_from_alg_cost = []
    all_from_grid_cost = []

    for i in range(1, 8):
        price_file_name = "prices" + str(i) + ".csv"
        prices = pd.read_csv("../data/" + price_file_name)
        prices["price"] = prices["price"] / 1000
        prices = prices.values

        usage_file_name = "energy_usage" + str(i) + ".csv"
        energy_usage = pd.read_csv("../data/" + usage_file_name).values

        battery_cost_per_kwh = battery.one_kwh_cost()
        battery_time, grid_time = best_algos_ever(prices,energy_usage,battery_cost_per_kwh, 0.6)

        bat = np.array(battery_time)
        grid = np.array(grid_time)

        energy_needed = energy_usage.sum()
        print(f"energy needed = {round(energy_needed, 3)}")
        all_energy_needed.append(energy_needed)

        alg_cost = benchmark(battery_time, 
                             grid_time, 
                             prices, 
                             energy_needed, 
                             battery_cost_per_kwh)
        all_from_alg_cost.append(alg_cost)
        # print(f"benchmark cost dla korzystania z algosa Michal {benchmark(battery_time, grid_time, prices, energy_needed, battery_cost_per_kwh)}")

        basic = [(i, float(usage)) for i, usage in 
                    enumerate(energy_usage.flatten())]
        grid_cost = benchmark([], 
                              basic, 
                              prices, 
                              energy_needed, 
                              battery_cost_per_kwh)
        all_from_grid_cost.append(grid_cost)
        # print(f"benchmark dla korzystania bezposrednio z grida = {benchmark([], basic, prices, energy_needed,battery_cost_per_kwh)}")
    
    print(f"sum of cost only from grid = {sum(all_from_grid_cost)}, sum of cost from alg = {sum(all_from_alg_cost)}")
    return all_energy_needed, all_from_grid_cost, all_from_alg_cost

def krzysieg_alg():
    
    all_energy_needed = []
    all_from_alg_cost = []
    all_from_grid_cost = []
    charge_level = 0

    for i in range(1, 8):
        battery = Battery(
            price=16000, 
            capacity=10, 
            DoD=0.95, 
            efficiency=0.9, 
            life_cycles=6000,
            charge_level=charge_level
            )

        battery_cost_per_kwh = battery.one_kwh_cost()

        k_alg = KAlg(charging_time=battery.charging_time, 
                    charging_per_hour=battery.charging_per_hour, 
                    charge_level=battery.charge_level,
                    battery_cost_per_kWh=battery_cost_per_kwh,
                    b_max_capacity=battery.capacity)

        price_file_name = "prices" + str(i) + ".csv"
        prices = pd.read_csv("../data/" + price_file_name)
        prices["price"] = prices["price"] / 1000
        prices = prices.values

        usage_file_name = "energy_usage" + str(i) + ".csv"
        energy_usage = pd.read_csv("../data/" + usage_file_name).values

        battery_time, grid_time, alg_cost = k_alg.krzysiek_algorithm(prices, energy_usage)

        energy_needed = energy_usage.sum()
        all_energy_needed.append(energy_needed)

        all_from_alg_cost.append(alg_cost)

        basic = [(i, float(usage)) for i, usage in 
                    enumerate(energy_usage.flatten())]
        grid_cost = benchmark([], 
                              basic, 
                              prices, 
                              energy_needed, 
                              battery_cost_per_kwh)
        all_from_grid_cost.append(grid_cost)

        charge_level = k_alg.charge_level

    print(f"sum of cost only from grid = {sum(all_from_grid_cost)}, sum of cost from alg = {sum(all_from_alg_cost)}")

    return all_energy_needed, all_from_grid_cost, all_from_alg_cost


    
def plot_results(all_energy_needed: List, 
                 all_from_grid_cost: List, 
                 all_from_alg_cost: List):
    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(all_from_grid_cost, label='Grid Cost', marker='o', color='blue')
    plt.plot(all_from_alg_cost, label='Algorithm Cost', marker='x', color='orange')

    # Formatting the plot
    plt.xlabel('day')
    plt.ylabel('Cost [zl]')
    plt.title('Comparison of Grid Cost and Algorithm Cost')
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    plt.savefig('krzysiek_alg.png')


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
    usage_files = glob.glob(usage_pattern)

    prices_pattern = "../data_months/day_*.csv"
    prices_files = glob.glob(prices_pattern)

    # expected amount to be loaded in entire 15 min period
    loading_per_segment = battery.charging_per_segment()

    results_only_grid = []
    results_krzysiek = []
    results_michal = []

    for i, (f_price, f_usage) in enumerate(zip(prices_files, usage_files)):
        print(f"DAY {i}")
        # converting to prices per kWh
        prices = pd.read_csv(f_price).values / 1000 
        usage = pd.read_csv(f_usage).values
        total = usage.sum()
        
        basic_grid_time = [(i, float(usage)) for i, usage in 
                    enumerate(usage.flatten())]
        
        res = round(benchmark([],basic_grid_time,prices,total,battery_cost_per_kwh),3)
        results_only_grid.append(res)
        print(f"total cost of stupid using only grid = {res}")

        battery_time, grid_time = best_algos_ever(prices,usage,battery_cost_per_kwh,loading_per_segment)
        res = round(benchmark(battery_time,grid_time,prices,total,battery_cost_per_kwh),3)
        results_michal.append(res)
        print(f"total cost of best algos ever = {res}")

        k_alg = KAlg(charging_time=battery.charging_time, 
                    charging_per_hour=battery.charging_per_hour, 
                    charge_level=battery.charge_level,
                    battery_cost_per_kWh=battery_cost_per_kwh,
                    b_max_capacity=battery.capacity)

        battery_time, grid_time, alg_cost = k_alg.krzysiek_algorithm(prices, usage)
        res = round(alg_cost,3)
        results_krzysiek.append(res)
        print(f"total cost of krzysiek's algos = {res}")

        
    # all_energy_needed_m, all_from_grid_cost_m, all_from_alg_cost_m = michal_alg()
    # all_energy_needed_k, all_from_grid_cost_k, all_from_alg_cost_k = krzysieg_alg()

    # plot_results(all_energy_needed, all_from_grid_cost, all_from_alg_cost)

    # battery = Battery(
    #     price=16000, 
    #     capacity=10, 
    #     DoD=0.95, 
    #     efficiency=0.9, 
    #     life_cycles=6000
    #     )
   
    # battery_cost_per_kwh = battery.one_kwh_cost()
    # battery_time, grid_time = best_algos_ever(prices,energy_usage_day_kWH,battery_cost_per_kwh,0.6)
    # bat = np.array(battery_time)
    # grid = np.array(grid_time)

    # energy_needed = energy_usage_day_kWH.sum()
    # print(f"energy needed = {energy_needed}")


    # print(f"benchmark cost dla korzystania z algosa mojego {benchmark(battery_time, grid_time, prices, energy_needed,battery_cost_per_kwh)}")

    # basic = [(i, float(usage)) for i, usage in enumerate(energy_usage_day_kWH.flatten())]
    # print(f"benchmark dla korzystania bezposrednio z grida = {benchmark([], basic, prices, energy_needed,battery_cost_per_kwh)}")

    # ## drugi algos 
    # k_alg = KAlg(charging_time=battery.charging_time, 
    #              charging_per_hour=battery.charging_per_hour, 
    #              charge_level=0,
    #              battery_cost_per_kWh=battery_cost_per_kwh,
    #              b_max_capacity=battery.capacity)
    
    # charging_times, grid_times = k_alg.krzysiek_algorithm(prices, energy_usage_day_kWH)
    
    # charge_sum = sum(j for _, j in charging_times)
    # print(f"charge sum = {charge_sum}")

    # bat2 = np.array(charging_times)
    # grid2 = np.array(grid_times)
    
    # print(f"benchmark cost dla korzystania z algosa krzyska {benchmark(charging_times, grid_times, prices, energy_needed, battery_cost_per_kwh)}")

