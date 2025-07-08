import heapq
from battery_handler.battery_handler import Battery
from backend.const import SIZE
from linear import optimise_battery
import numpy as np

def load_only_to_sell(battery_load: np.ndarray,
                      buy_prices: np.ndarray,
                      sell_prices: np.ndarray,
                      battery: Battery):
    SIZE = len(buy_prices)
    free_capacity = np.full(SIZE, battery.capacity) - battery_load
    battery_usage_cost = battery.one_kwh_cost()

    buy_time  = np.zeros(SIZE, dtype=float)
    sell_time = np.zeros(SIZE, dtype=float)

    # 1) Build array of future peaks in one pass
    future_max = np.empty(SIZE, dtype=float)
    max_so_far = -np.inf
    for i in range(SIZE - 1, -1, -1):
        max_so_far = max(max_so_far, sell_prices[i])
        future_max[i] = max_so_far

    buy_idx = None
    for i in range(SIZE - 1):
        eff_buy = buy_prices[i] + battery_usage_cost

        # pick lowest effective buy index so far
        if buy_idx is None or eff_buy < buy_prices[buy_idx] + battery_usage_cost:
            buy_idx = i

        # check selling condition
        if (sell_prices[i] >= 0.95 * future_max[i] and
            sell_prices[i] > buy_prices[buy_idx] + battery_usage_cost):

            # clamp by true current free capacity
            avail = free_capacity[buy_idx:i+1].min()
            if avail <= 0:
                # nothing left to sell from that buy slot
                buy_idx += 1
                continue

            # record transactions
            buy_time[buy_idx]  += avail
            sell_time[i]       += avail

            # immediately reduce free capacity so we can't oversell later
            free_capacity[buy_idx:i+1] -= avail

            # advance buy_idx so we don’t reuse an exhausted slot
            buy_idx = None

    return buy_time, sell_time


def best_algos_ever(buy_prices: np.ndarray,
                    sell_prices: np.ndarray,
                    usages: np.ndarray,
                    battery: Battery,
                    solar_free: np.ndarray,
                    load_to_sell: bool = False):
    assert SIZE == usages.shape[0], "prices and usages must have 96 elements"
    
    battery_cost_per_kwh = battery.one_kwh_cost()
    loading_per_segment = battery.charging_per_segment()
    battery_cap = battery.capacity
    
    sched, cost = optimise_battery(buy_prices, usages, C = battery_cap, c_batt=battery_cost_per_kwh, P_ch = loading_per_segment, P_dis=loading_per_segment)
    # print(sched)
    battery_load_time, battery_use_time, grid_time  = sched["charge"], sched["discharge"], sched["grid_buy"]
    final_cum_use = np.cumsum(battery_load_time) - np.cumsum(battery_use_time)

    
        
    if load_to_sell:
        buy_time, sell_time = load_only_to_sell(final_cum_use, buy_prices, sell_prices, battery)
    else:
        buy_time = np.zeros(SIZE)
        sell_time = np.zeros(SIZE)

    return battery_load_time, grid_time, buy_time, sell_time

