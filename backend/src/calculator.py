import pandas as pd
from battery_handler.battery_handler import Battery
from algoritms import best_algos_ever
import glob



def is_overloaded(battery_loading, usage, total_capacity):
    battery = 0  # Initial battery level
    timeline = [0] * 96  # 96 time slots for the day
    
    # Apply battery loading events
    for i, load in battery_loading:
        timeline[i] += load
    
    # Simulate battery level over time
    for i in range(96):
        battery += timeline[i] 
        battery -= usage[i]  
        
        if battery > total_capacity:
            return True 
        
        battery = max(battery, 0)  # Ensure battery does not go below 0
    
    return False 

# benchmark accepts two lists, each list contains pairs - (index of 15min period in 24h - starting from 00:00, ending 23:45 -> 96 indices posibles):
# 1) - battery_loading - at given index, how much power to load battery -> price at loading time, not using time;
# 2) - grid_loading - the same but when using energy directly from grid
# 3) - prices is a list of prices at given 15min period (96indices)

def benchmark(battery_loading:list, grid_loading:list, prices:list, needed:list, battery:Battery, tol = 0.01):
    usage_list = battery_loading + grid_loading
    sum_of_js = sum(j for _, j in usage_list)
    max_load_15min = battery.charging_per_segment()
    total_cap = battery.capacity
    total = sum(needed)
    # ensuring correct input
    assert not (total - sum_of_js  > tol), "Not fulfilled entire need"
    assert not (sum_of_js - total > tol), f"loading too much energy: energy needed {total}, energy loaded = {sum_of_js}"
    # assert sum(j for _, j in battery_loading) <= total_cap, f"loaded more to battery than total cap"
    if is_overloaded(battery_loading,needed,total_cap):
        print(f"loaded {sum(j for _, j in battery_loading)} battery and total cap = {total_cap}")

    load_per_index = {}
    for start, amount in usage_list:
        load_per_index[start] = load_per_index.get(start, 0) + amount
        assert load_per_index[start] <= max_load_15min + tol, f"Exceeded max load of {max_load_15min} at index {start}, with value = {load_per_index[start]}" 


    total_cost = 0
    for start, amount in grid_loading:
        cost = prices[start]
        total_cost += cost * amount   
    for start, amount in battery_loading:
        cost = prices[start]
        total_cost += cost * amount

    return total_cost

def total_profit(battery: Battery, do_print = False):
    battery_cost_per_kwh = battery.one_kwh_cost()

    usage_pattern = "../data_months/usage*.csv"
    usage_files = sorted(glob.glob(usage_pattern))
    #ensuring that files are starting from day 0, and ascending
    prices_pattern = "../data_months/day_*.csv"
    prices_files = sorted(glob.glob(prices_pattern))
    # expected amount to be loaded in entire 15 min period

    results_only_grid = []
    results_michal = []

    for i, (f_price, f_usage) in enumerate(zip(prices_files, usage_files)):
        if do_print:
            print(f"DAY {i}")
        # converting to prices per kWh
        prices = ((pd.read_csv(f_price).values / 1000).flatten()).tolist() 
        # usage already in kWh
        usage = (pd.read_csv(f_usage).values).flatten().tolist()
        
        basic_grid_time = [(i, float(usage)) for i, usage in 
                    enumerate(usage)]
        
        res = round(benchmark([],basic_grid_time,prices,usage, battery),3)
        results_only_grid.append(res)
        if do_print:
            print(f"total cost of stupid using only grid = {res}")

        battery_time, grid_time = best_algos_ever(prices,usage,battery)
        res = round(benchmark(battery_time,grid_time,prices, usage, battery),3)
        results_michal.append(res)
        if do_print:
            print(f"total cost of best algos ever = {res}")

    assert len(results_michal) == len(results_only_grid), "different lenghts of results"
    assert all(a <= b for a, b in zip(results_michal, results_only_grid)), "Not all profits in michal's algo are smaller than in stupid algo"

    return sum(m - g for m, g in zip(results_only_grid, results_michal))



if __name__ == "__main__":

    # Mój Prą 6.0 - 50% grant
    # https://www.4sun.eu/strona-glowna/magazyn-energii-foxess-518-kwh-ep5-hv
    batteries = [
    Battery(
        price=8000, 
        capacity=5.18, 
        DoD=0.95, 
        efficiency=0.98, 
        life_cycles=4000,
        grant_reduction=4000
    ),
    Battery(
        price=4800, 
        capacity=2.88, 
        DoD=0.9, 
        efficiency=0.95, 
        life_cycles=6000,
        grant_reduction=2400
    ),
    Battery(
        price=14350, 
        capacity=10.36, 
        DoD=0.9, 
        efficiency=0.95, 
        life_cycles=4000,
        grant_reduction=7175
    )
    ]
    
    print("\n".join(f"profit of {i} battery = {total_profit(battery)}, expected months to return = {battery.get_real_price() / total_profit(battery)}"
                     for i, battery in enumerate(batteries)))
    
    
   