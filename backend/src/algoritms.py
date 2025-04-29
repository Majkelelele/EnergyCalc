import heapq
from battery_handler.battery_handler import Battery
from backend.const import SIZE
import numpy as np
import pandas as pd


class Info:
    def __init__(self, remaining_energy, cost, start):
        self.remaining_energy = remaining_energy
        self.cost = cost
        self.start = start

    def __lt__(self, other):
        if(self.cost == other.get_cost()):
            return self.start < other.start
        return self.cost < other.get_cost()

    def get_cost(self):
        return self.cost

    def get_remaining_energy(self):
        return self.remaining_energy

    def lower_remaining_energy(self, amount):
        self.remaining_energy -= amount

    def get_start(self):
        return self.start
 
 

def load_only_to_sell(battery_load, buy_prices, sell_prices, battery):
    free_capacity = np.full(SIZE, battery.capacity) - battery_load
    battery_usage_cost = battery.one_kwh_cost()
    
    n = len(buy_prices)
    buy_time = np.zeros(n)  # Stores amount of energy bought at each index
    sell_time = np.zeros(n)  # Stores amount of energy sold at each index
    
    buy_idx = None  # Stores the last buy index
    
    for i in range(n - 1):
        # Buying condition: Local minima and free capacity available
        effective_buy_price = buy_prices[i] + battery_usage_cost
        if buy_idx is None or effective_buy_price < buy_prices[buy_idx] + battery_usage_cost:
            buy_idx = i
        
        # Lookahead strategy to find better selling opportunities
        if buy_idx is not None:
            future_max_price = max(sell_prices[i:])  # Find highest price in the remaining periods
            
            if  sell_prices[i] >= future_max_price * 0.95 and sell_prices[i] > buy_prices[buy_idx] + battery_usage_cost:  # Sell only if close to future peak
                # Buy as much as possible at buy_idx and sell it here
                energy_bought = np.min(free_capacity[buy_idx:i+1])                
                # Adjust free capacity between buy_idx and i (holding energy until selling)
                for t in range(buy_idx, i + 1):
                    free_capacity[t] -= energy_bought
                
                # Store buy and sell amounts
                buy_time[buy_idx] += energy_bought
                sell_time[i] += energy_bought
                
                # Reset buy index after selling
                buy_idx += 1
    
    return buy_time, sell_time


def best_algos_ever(buy_prices: np.ndarray, sell_prices, usages: np.ndarray, battery: Battery, load_to_sell=True, provider="enea"):
    # Ensure we have 96 periods
    assert buy_prices.shape[0] == usages.shape[0] == SIZE, "prices and usages must have 96 elements (one for each 15-min period)"
            
    battery_cost_per_kwh = battery.one_kwh_cost() # cost of charging and discharging 1 kWh
    loading_per_segment = battery.charging_per_segment() # how many kWh per 15 min
    battery_cap = battery.capacity
    
    info_list = []
    battery_load_time = np.zeros(SIZE)
    grid_time = np.zeros(SIZE)
    battery_use_time = np.zeros(SIZE)
    
    battery_load_curr = 0
    
    needs = list(sorted(range(SIZE), key=lambda x: buy_prices[x], reverse=True))
    
    for i in range(SIZE):
        heapq.heappush(info_list, Info(loading_per_segment, battery_cost_per_kwh + buy_prices[i], i))

    temp_heap = []
    print(f"ENTERING NEW DAY")
    for i in needs:

        price = float(buy_prices[i])
        usage = float(usages[i])
        assert usage >= 0, "usage < 0"
        print(f"need = {i}")
        
        while info_list and info_list[0].get_cost() < price and usage > 0 and battery_load_curr < battery_cap:
            curr_period = heapq.heappop(info_list)
            if curr_period.get_start() < i:
                cum_use = np.cumsum(battery_use_time)
                cum_load = np.cumsum(battery_load_time)
                battery_load = cum_load - cum_use
                # print(battery_load.round(2))
                battery_load_curr = np.max(battery_load[curr_period.get_start():i])
                remaining_energy = curr_period.get_remaining_energy()
                remaining_cap = max(0,battery_cap - battery_load_curr)
                # print(f"cap = {remaining_cap}, battery_load_curr = {battery_load_curr}, battery_cap = {battery_cap}")
                
                to_load = min(remaining_cap, min(usage, remaining_energy))
                # print(f"to_load = {to_load}")

                if to_load == usage or to_load == remaining_cap:
                    curr_period.lower_remaining_energy(to_load)
                    if curr_period.get_remaining_energy() > 0:
                        heapq.heappush(info_list, curr_period)
                battery_use_time[i] += to_load
                usage -= to_load
                battery_load_curr += to_load
                battery_load_time[curr_period.get_start()] += to_load
            else:   
                temp_heap.append(curr_period)
                
        
        if usage > 0:
            grid_time[i] += usage
        for i in temp_heap:
            heapq.heappush(info_list, curr_period)
            
        
    final_cum_use = np.cumsum(battery_load_time) - np.cumsum(battery_use_time)
        
    if load_to_sell:
        buy_time, sell_time = load_only_to_sell(final_cum_use, buy_prices, sell_prices, battery)
    else:
        buy_time = np.zeros(SIZE)
        sell_time = np.zeros(SIZE)

    return battery_load_time, grid_time, buy_time, sell_time

