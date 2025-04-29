import pandas as pd
from battery_handler.battery_handler import Battery
from algoritms import best_algos_ever
import glob
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray  # Available in NumPy 1.20 and later
from backend.scripts.making_data_script import generate_energy_usage_days
from backend.const import TOL, SIZE, BATTERIES, WITHDRAWABLE_RATE
from providers import calculate_enea_prices, calculate_energa_prices, calculate_pge_prices, calculate_tauron_prices
import os
import datetime


ARR = NDArray[np.float32]


def is_overloaded(battery_loading:ARR, usage:ARR, grid_loading:ARR, buy:ARR, sell:ARR, total_capacity:float, tol = TOL):
    battery = 0  # Initial battery level
    
    # Simulate battery level over time
    for i in range(SIZE):
        battery += battery_loading[i]
        battery -= usage[i]
        battery += grid_loading[i]
        battery += buy[i]
        battery -= sell[i]

        if battery > total_capacity + tol:
            return True 
            
    return False 

# benchmark accepts two lists, each list contains pairs - (index of 15min period in 24h - starting from 00:00, ending 23:45 -> 96 indices posibles):
# 1) - battery_loading - at given index, how much power to load battery -> price at loading time, not using time;
# 2) - grid_loading - the same but when using energy directly from grid
# 3) - prices is a list of prices at given 15min period (96indices)

def is_loadable(battery_loading:ARR, buy:ARR, total_capacity:float, tol = TOL):
    sum_load = battery_loading + buy
    return np.all(sum_load <= total_capacity + tol)
    

def benchmark(
    battery_loading: ARR, 
    grid_loading: ARR, 
    buy: ARR, 
    sell: ARR,
    buy_prices: ARR, 
    sell_prices: ARR,
    base_prices: ARR,
    selling_buying,
    usage: ARR, 
    battery: Battery, 
    tol: float = TOL
):

    energy_provided = battery_loading.sum() + grid_loading.sum()
    max_load_15min = battery.charging_per_segment()
    total_cap = battery.capacity
    total = sum(usage)
    # ensuring correct input
    assert not (total - energy_provided  > tol), "Not fulfilled entire need"
    assert not (energy_provided - total > tol), f"loading too much energy: energy needed {total}, energy loaded = {energy_provided}"   
    assert not is_overloaded(battery_loading, usage, grid_loading, buy, sell, total_cap), "Battery overloaded"
    


    assert is_loadable(battery_loading,buy, battery.capacity), f"Some values exceeded max load of {max_load_15min + tol}"
        
    cost_per_kwh = battery.one_kwh_cost()
    total_cost = 0
    total_cost += (grid_loading * buy_prices).sum()
    total_cost += (battery_loading * (buy_prices)).sum()
    total_cost += (buy * (buy_prices)).sum()
    selling_buying["bought"] += (grid_loading * base_prices).sum() + (buy * (base_prices)).sum() + (battery_loading * base_prices).sum()
    selling_buying["sold"] += (sell * sell_prices).sum() 

    
    
    return total_cost

def run_best_algos_one_day(prices, usage, sell_prices, battery: Battery, load_to_sell=True, provider="enea", tariff="G11", staying_static=False, date="2025-03-03"):

    match provider:
        case "enea":
            buy_prices, sell_prices, month_const_cost_1 =  calculate_enea_prices(prices, sell_prices, tariff=tariff, static_prices=staying_static)
        case "energa":
            buy_prices, sell_prices, month_const_cost_1 =  calculate_energa_prices(prices, sell_prices, tariff=tariff, static_prices=staying_static)
        case "pge":
            buy_prices, sell_prices, month_const_cost_1 =  calculate_pge_prices(prices, sell_prices, tariff=tariff, static_prices=staying_static)
        case "tauron":
            buy_prices, sell_prices, month_const_cost_1 =  calculate_tauron_prices(prices, sell_prices, tariff=tariff, static_prices=staying_static, date=date)
        case _:
            raise ValueError("Wrong provider")
    
    battery_load_time, grid_time, buy, sell = best_algos_ever(buy_prices, sell_prices, usage,battery,load_to_sell=load_to_sell)
    
    
    # time = np.arange(96)  # X-axis: 96 time steps (15 min intervals)

    # plt.figure(figsize=(14, 6))

    # # Plot each series
    # plt.plot(time, battery_load_time, label="Battery Load", color='green')
    # plt.plot(time, grid_time, label="Grid Usage", color='blue')
    # plt.plot(time, prices, label="Price", color='orange')

    # # Decorations
    # plt.title("Battery Load, Grid Usage & Prices Over a Day")
    # plt.xlabel("Time (15-min intervals)")
    # plt.ylabel("Value")
    # plt.legend()
    # plt.grid(True)
    # plt.tight_layout()

    # plt.show()
    return battery_load_time, grid_time, buy, sell, month_const_cost_1, buy_prices, sell_prices

def parse_date_from_path(path):
    filename = os.path.basename(path)  # -> "2024-07-01.csv"
    date_str = filename.replace(".csv", "")  # -> "2024-07-01"
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def calculate_one_day(f_price, f_usage, f_rce, f_solar, battery: Battery, selling_buying={"sold": 0, "bought": 0}, load_to_sell=True, provider="enea", switching_from_static=False,
                      tariff="G11", staying_static = False, solar_available=False, starting_tariff="G11"):
     
    # prices per kWh
    prices = np.array((pd.read_csv(f_price).values).flatten())
    # usage already in kWh
    usage = np.array((pd.read_csv(f_usage).values).flatten())
    
    if solar_available:
        solar = np.array((pd.read_csv(f_solar).values).flatten())
        usage -= solar
        usage = np.maximum(0, usage)
        
    sell_prices = np.array((pd.read_csv(f_rce).values).flatten())
    date = parse_date_from_path(f_price)
    
    battery_load_time, grid_time, buy, sell, month_const_cost_1, buy_prices, sell_prices = run_best_algos_one_day(prices, usage, sell_prices, battery, load_to_sell, provider, tariff=tariff, staying_static=staying_static, date=date)
    

    res_algos = round(benchmark(battery_load_time,grid_time,buy, sell,buy_prices, sell_prices,  prices, selling_buying, usage, battery),3)
    
    
    prices = np.array((pd.read_csv(f_price).values).flatten())
    match provider:
        case "enea":
            buy_prices, sell_prices,  month_const_cost_2 =  calculate_enea_prices(prices, sell_prices, starting_tariff, switching_from_static)
        case "energa":
            buy_prices, sell_prices,  month_const_cost_2 =  calculate_energa_prices(prices, sell_prices, starting_tariff, switching_from_static)
        case "pge":
            buy_prices, sell_prices,  month_const_cost_2 =  calculate_pge_prices(prices, sell_prices,starting_tariff, switching_from_static)
        case "tauron":
            buy_prices, sell_prices,  month_const_cost_2 =  calculate_tauron_prices(prices, sell_prices, starting_tariff, switching_from_static, date=date)
        case _:
            raise ValueError("Wrong provider")
    selling_buying_fake = {"sold": 0, "bought": 0}

    res_benchmark = round(benchmark(np.zeros(SIZE),usage,np.zeros(SIZE), np.zeros(SIZE), buy_prices,sell_prices, prices, selling_buying_fake,usage, battery),3)
    return res_algos, res_benchmark, month_const_cost_1, month_const_cost_2
    
def total_profit(battery: Battery, load_to_sell=True, provider="enea", switching_from_static=False, solar_avaialable=False,
                 daily_usage=5, tariff="G11", staying_static=False, starting_tariff="G11"):
    prices_pattern = "../data_months/tge/*.csv"
    prices_files = sorted(glob.glob(prices_pattern))
    
    generate_energy_usage_days(total_usage=daily_usage, days=len(prices_files))
    usage_pattern = "../data_months/usage/*.csv"
    usage_files = sorted(glob.glob(usage_pattern))
   
    rce_prices_pattern = "../data_months/rce/*.csv"
    rce_prices_files = sorted(glob.glob(rce_prices_pattern))

    solar_pattern = "../data_months/solar_output/*.csv"
    solar_files = sorted(glob.glob(solar_pattern))
    
    # expected amount to be loaded in entire 15 min period
    results_only_grid = []
    results_michal = []
    selling_buying = {"sold": 0, "bought": 0}

    for i, (f_price, f_usage, f_rce, f_solar) in enumerate(zip(prices_files, usage_files, rce_prices_files, solar_files)):
        res_algos, res_benchmark, month_const_cost_1, month_const_cost_2 = calculate_one_day(f_price,f_usage,f_rce,f_solar, battery, selling_buying, load_to_sell,provider,switching_from_static, tariff=tariff, staying_static=staying_static, solar_available=solar_avaialable, starting_tariff=starting_tariff)
        results_michal.append(res_algos)
        results_only_grid.append(res_benchmark)
    print(selling_buying)
    assert len(results_michal) == len(results_only_grid), "different lenghts of results"
    # if not switching_from_static:
    #     assert all(a <= b for a, b in zip(results_michal, results_only_grid)), "Not all profits in Michal's algo are smaller than in stupid algo"
    max_diff = max([p1 - p2 for p1, p2 in zip(results_only_grid, results_michal)])
    print(f"max profit in one day per entire period = {max_diff} zlotych")
    print(f"days considerd in a period = {min(len(prices_files), len(usage_files))}")
    months = float(len(prices_files)) / 30.0
    print(f"months = {months}")
    cost_algos = sum(results_michal)
    cost_benchmark = sum(results_only_grid)
    print(f"pre deducion cost algos = {cost_algos}, benchmark = {cost_benchmark}")
    
    deductible = min(selling_buying["sold"], selling_buying["bought"])
    # profit += deductible
    # profit += WITHDRAWABLE_RATE * max(0, selling_buying["sold"] - deductible)
    
    cost_algos -= deductible
    cost_algos -= WITHDRAWABLE_RATE * max(0, selling_buying["sold"] - deductible)
    print(f"algos total cost = {cost_algos}, benchmark total cost = {cost_benchmark}")
    loosing = max(0, selling_buying["sold"] - deductible) * (1 - WITHDRAWABLE_RATE)
    print(f"loosing {loosing}")
    
    difference = cost_benchmark - cost_algos
    profit = difference - (month_const_cost_1 - month_const_cost_2) * months
    return profit, months


# load_to_sell - if True, we are enabling selling energy to back to grid,
def simulate(do_print = False, grant=False, daily_usage=7.5, load_to_sell=True, provider="enea",
             switching_from_static=False, solar_avaialable=False, tariff="G11", staying_static=False,
             starting_tariff="G11"):
    print(f'provider = {provider}')
    print(f"tariff = {tariff}")
    
    # for b in BATTERIES:
    #     b.set_grant(grant)
        
    avg_profits = []
    expected_months_to_returns = []
    expected_months_res = []
    for i, bat in enumerate(BATTERIES):
        print(bat)
        print(f"battery kwh cost = {bat.one_kwh_cost()}")

        profit, months = total_profit(bat, load_to_sell=load_to_sell, provider=provider, switching_from_static=switching_from_static, solar_avaialable=solar_avaialable,daily_usage=daily_usage, tariff=tariff, staying_static=staying_static, starting_tariff=starting_tariff)
        avg_profit_month = round(profit / months,2)
        expected_months_to_return = round(bat.get_real_price() / avg_profit_month,2)
        expected_months_cycles = round(bat.get_expected_month_cycles(),2)
        avg_profits.append(avg_profit_month)
        expected_months_to_returns.append(expected_months_to_return)
        expected_months_res.append(expected_months_cycles)
        if do_print:
            print(
                f"average profit of {i} battery per month = {avg_profit_month}, expected months to return = {expected_months_to_return}, "
                f"expected month_life_cycles = {expected_months_cycles}")
        print()
    return BATTERIES, avg_profits, expected_months_to_returns, expected_months_cycles

def simulate_only_static_saving_one_bat(battery: Battery, load_to_sell=False, provider="enea", switching_from_static=True, daily_usage=5, tarifs = ["G11", "G12", "G13"]):
    prices_pattern = "../data_months/tge/*.csv"
    prices_files = sorted(glob.glob(prices_pattern))
    
    generate_energy_usage_days(total_usage=daily_usage, days=len(prices_files))
    usage_pattern = "../data_months/usage/*.csv"
    usage_files = sorted(glob.glob(usage_pattern))
   
    rce_prices_pattern = "../data_months/rce/*.csv"
    rce_prices_files = sorted(glob.glob(rce_prices_pattern))
    
    solar_pattern = "../data_months/solar_output/*.csv"
    solar_files = sorted(glob.glob(solar_pattern))
    
    avg_max_cost = 0
    avg_min_cost = 1000000
    for tariff in tarifs:
        results_only_grid = []
        results_michal = []
        selling_buying = {"sold": 0, "bought": 0, "total_cost":0}
        for i, (f_price, f_usage, f_rce, f_solar) in enumerate(zip(prices_files, usage_files, rce_prices_files, solar_files)):
            res_algos, res_benchmark, _, _ = calculate_one_day(f_price,f_usage,f_rce, f_solar, battery,load_to_sell,provider,switching_from_static,  tariff=tariff, staying_static=True, selling_buying=selling_buying)
            results_michal.append(res_algos)
            results_only_grid.append(res_benchmark)
        months = float(len(prices_files)) / 30.0
        algos_cost = sum(results_michal)
        benchmark_cost = sum(results_only_grid)
        avg_max_cost = max(avg_max_cost, benchmark_cost/ months)
        avg_min_cost = min(avg_min_cost, algos_cost/ months)
        print(f"average cost per month for tarif {tariff} = {algos_cost/ months}")
        print(f"benchmark = {benchmark_cost/ months}")
    profit = avg_max_cost - avg_min_cost
    print(f"avg min cost = {avg_min_cost}, avg max_cost = {avg_max_cost}, profit = {profit}")
    print(f"month to return =  {battery.get_real_price() / profit}")
    print("")
    

def simulate_only_static_saving(provider="enea", daily_usage=5, tarifs = ["G11", "G12", "G13"], load_to_sell=False):
    for i, bat in enumerate(BATTERIES):
        print(bat)
        simulate_only_static_saving_one_bat(bat, provider=provider, daily_usage=daily_usage,tarifs=tarifs, load_to_sell=load_to_sell)


    
if __name__ == "__main__":
    # simulate_only_static_saving(provider="tauron", daily_usage=7, tarifs=["G11", "G12", "G13", "G14"], load_to_sell=True)
    simulate(do_print=True, grant=True, daily_usage=7, load_to_sell=True, provider="tauron", switching_from_static=False, solar_avaialable=False, tariff="G13", staying_static=False, starting_tariff="G11")
