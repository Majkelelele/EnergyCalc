import heapq
from battery_handler.battery_handler import Battery
import numpy as np

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

def load_only_to_sell(battery_load: list, prices: list, battery):
    max_load = battery.charging_per_segment()
    battery_cap = battery.capacity
    buy_time = np.zeros(96)
    sell_time = np.zeros(96)
    cost_per_kwh = battery.one_kwh_cost()
    
    # Convert lists to numpy arrays for easier manipulation
    # battery_load = np.array(battery_load)
    # prices = np.array(prices)
    
    # # Adjust prices to include amortization cost
    # adjusted_prices = prices + cost_per_kwh
    
    # # Sort indices based on adjusted prices to buy at lowest and sell at highest
    # buy_indices = np.argsort(adjusted_prices)  # Ascending order (cheapest first)
    # sell_indices = np.argsort(prices)[::-1]  # Descending order (most expensive first)
    
    # for buy_idx in buy_indices:
    #     available_capacity = battery_cap - battery_load[buy_idx]  # Remaining capacity at this time step
    #     if available_capacity > 0:
    #         charge_amount = min(max_load, available_capacity)
    #         potential_profit = any(prices[sell_indices] > adjusted_prices[buy_idx])
            
    #         if potential_profit:
    #             buy_time[buy_idx] = charge_amount
    #             battery_load[buy_idx] += charge_amount  # Update battery state
    
    # for sell_idx in sell_indices:
    #     if battery_load[sell_idx] > 0:  # Only sell if there's charge
    #         sell_amount = min(max_load, battery_load[sell_idx])
    #         sell_time[sell_idx] = sell_amount
    #         battery_load[sell_idx] -= sell_amount  # Update battery state
    
    return buy_time, sell_time


def best_algos_ever(prices: np.ndarray, usages: np.ndarray, battery: Battery):
    # Ensure we have 96 periods
    assert prices.shape[0] == usages.shape[0] == 96, "prices and usages must have 96 elements (one for each 15-min period)"
    
    battery_cost_per_kwh = battery.one_kwh_cost()
    loading_per_segment = battery.charging_per_segment()
    battery_cap = battery.capacity
    
    info_list = []
    battery_load_time = np.zeros(96)
    grid_time = np.zeros(96)
    battery_use_time = np.zeros(96)
    
    battery_load_curr = 0
    
    for i in range(96):
        price = float(prices[i])
        usage = float(usages[i])
        assert usage >= 0, "usage < 0"
        
        
        while info_list and info_list[0].get_cost() < price and usage > 0 and battery_load_curr < battery_cap:
            curr_period = heapq.heappop(info_list)
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
                
        
        if usage > 0:
            grid_time[i] += usage
            
        heapq.heappush(info_list, Info(loading_per_segment, battery_cost_per_kwh + price, i))

        # buy_time, sell_time = load_only_to_sell(cummulative_load, prices, battery)
        buy_time = np.zeros(96)
        sell_time = np.zeros(96)

    return battery_load_time, grid_time, buy_time, sell_time

