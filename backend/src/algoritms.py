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



def best_algos_ever(buy_prices: np.ndarray,
                    sell_prices: np.ndarray,
                    usages: np.ndarray,
                    battery: Battery,
                    load_to_sell: bool = True,
                    provider: str = "enea"):
    assert SIZE == usages.shape[0], "prices and usages must have 96 elements"
    
    battery_cost_per_kwh = battery.one_kwh_cost()
    loading_per_segment = battery.charging_per_segment()
    battery_cap = battery.capacity

    # Outputs
    battery_load_time = np.zeros(SIZE, dtype=float)
    battery_use_time  = np.zeros(SIZE, dtype=float)
    grid_time         = np.zeros(SIZE, dtype=float)

    # Track SoC at each period, updated incrementally
    soc = np.zeros(SIZE, dtype=float)

    # Build heap of all possible charge-slots
    info_heap = [(buy_prices[i] + battery_cost_per_kwh, i, loading_per_segment)
                 for i in range(SIZE)]
    heapq.heapify(info_heap)

    # Handle most expensive usage times first
    for t in np.argsort(-buy_prices):
        price_t = buy_prices[t]
        need = usages[t]

        # Try to cover 'need' from earlier cheap charges
        while need > 1e-8 and info_heap and info_heap[0][1] < t:
            cost_i, start_i, rem = heapq.heappop(info_heap)
            if cost_i >= price_t:
                # No more profitable slots
                heapq.heappush(info_heap, (cost_i, start_i, rem))
                break

            # available headroom before period t is min(cap - soc[k]) for k in [start_i, t)
            headroom = battery_cap - soc[start_i:t]
            max_move = headroom.min() if headroom.size > 0 else battery_cap
            to_move = min(rem, need, max_move)

            if to_move <= 1e-8:
                continue

            # record flows
            battery_load_time[start_i] += to_move
            battery_use_time[t]      += to_move

            # bump SoC on [start_i, t)
            soc[start_i:t] += to_move

            need -= to_move
            rem  -= to_move

            # push back any leftover from this charge slot
            if rem > 1e-8:
                heapq.heappush(info_heap, (cost_i, start_i, rem))

        # leftover from grid
        if need > 1e-8:
            grid_time[t] = need

    # sanity check: never exceeded capacity
    assert np.all(soc <= battery_cap + 1e-6), "SoC exceeded battery capacity!"

    
            
        
    final_cum_use = np.cumsum(battery_load_time) - np.cumsum(battery_use_time)
        
    if load_to_sell:
        buy_time, sell_time = load_only_to_sell(final_cum_use, buy_prices, sell_prices, battery)
    else:
        buy_time = np.zeros(SIZE)
        sell_time = np.zeros(SIZE)

    return battery_load_time, grid_time, buy_time, sell_time

