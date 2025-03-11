import pandas as pd
from battery_handler.battery_handler import Battery
from algoritms import best_algos_ever
import glob
import numpy as np
from numpy.typing import NDArray  # Available in NumPy 1.20 and later
from backend.scripts.making_data_script import generate_energy_usage_200days
from backend.const import TOL, SIZE, CURRENT_B
from providers import calculate_enea_price



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
    prices: ARR, 
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
    total_cost += (grid_loading * prices).sum()
    total_cost += (battery_loading * (prices + cost_per_kwh)).sum()
    total_cost += (buy * (prices + cost_per_kwh)).sum()
    total_cost -= (sell * prices).sum() 
    

    return total_cost

def total_profit(battery: Battery, load_to_sell=True, provider="enea"):

    usage_pattern = "../data_months/usage*.csv"
    usage_files = sorted(glob.glob(usage_pattern))
    #ensuring that files are starting from day 0, and ascending
    prices_pattern = "../data_months/tge*.csv"
    prices_files = sorted(glob.glob(prices_pattern))
    # expected amount to be loaded in entire 15 min period

    results_only_grid = []
    results_michal = []
    for i, (f_price, f_usage) in enumerate(zip(prices_files, usage_files)):
        # prices per kWh
        prices = np.array((pd.read_csv(f_price).values).flatten())
        # usage already in kWh
        usage = np.array((pd.read_csv(f_usage).values).flatten())
        match provider:
            case "enea":
                prices, month_const_cost =  calculate_enea_price(prices)
            case _:
                raise ValueError("Wrong provider")
        
        battery_time, grid_time, buy, sell = best_algos_ever(prices,usage,battery,load_to_sell=load_to_sell, provider=provider)
        res = round(benchmark(battery_time,grid_time,buy, sell, prices, usage, battery),3)
        results_michal.append(res)
        
        res = round(benchmark(np.zeros(SIZE),usage,np.zeros(SIZE), np.zeros(SIZE), prices,usage, battery),3)
        results_only_grid.append(res)


        

    assert len(results_michal) == len(results_only_grid), "different lenghts of results"
    assert all(a <= b for a, b in zip(results_michal, results_only_grid)), "Not all profits in Michal's algo are smaller than in stupid algo"
    return sum(m - g for m, g in zip(results_only_grid, results_michal)), float(len(prices_files)) / 30.0, month_const_cost

def simulate(do_print = False, grant=False, daily_usage=7.5, load_to_sell=True, provider="enea"):
    generate_energy_usage_200days(total_usage=daily_usage)
    batteries = [
        Battery(
        price=4800, 
        capacity=2.88, 
        DoD=0.9, 
        efficiency=0.95, 
        life_cycles=6000,
        grant_reduction=grant
    ),
    Battery(
        price=8000, 
        capacity=5.18, 
        DoD=0.95, 
        efficiency=0.98, 
        life_cycles=4000,
        grant_reduction=grant
    ),
    Battery(
        price=14350, 
        capacity=10.36, 
        DoD=0.9, 
        efficiency=0.95, 
        life_cycles=4000,
        grant_reduction=grant
    ),
    ]
    avg_profits = []
    expected_months_to_returns = []
    expected_months_res = []
    for i, bat in enumerate(batteries):
        profit, months, month_const_cost = total_profit(bat, load_to_sell=load_to_sell, provider=provider)
        avg_profit_month = round(profit / months  - month_const_cost,2)
        expected_months_to_return = round(bat.get_real_price() / avg_profit_month,2)
        expected_months_cycles = round(bat.get_expected_month_cycles(),2)
        avg_profits.append(avg_profit_month)
        expected_months_to_returns.append(expected_months_to_return)
        expected_months_res.append(expected_months_cycles)
        if do_print:
            print(
                f"average profit of {i} battery per month = {avg_profit_month}, expected months to return = {expected_months_to_return}, "
                f"expected month_life_cycles = {expected_months_cycles}")
    return batteries, avg_profits, expected_months_to_returns, expected_months_cycles

if __name__ == "__main__":
    simulate(do_print=True, grant=True, daily_usage=2, load_to_sell=True, provider="enea")
