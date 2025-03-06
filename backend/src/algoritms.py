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

def load_only_to_sell(battery_time: list, prices: list, battery: Battery):
#     free_load = np.full(96, battery.charging_per_segment(), dtype=float)
#     free_load -= battery_time
#     cost_kw = battery.one_kwh_cost()
#     heap = []
    buy_time = np.zeros(96)
    sell_time = np.zeros(96)

#     # Load battery to full
    

    return buy_time, sell_time

def best_algos_ever(prices: np.ndarray, usages: np.ndarray, battery: Battery):
    # Ensure we have 96 periods
    assert prices.shape[0] == usages.shape[0] == 96, "prices and usages must have 96 elements (one for each 15-min period)"
    
    battery_cost_per_kwh = battery.one_kwh_cost()
    loading_per_segment = battery.charging_per_segment()
    battery_cap = battery.capacity
    
    info_list = []
    battery_time = np.zeros(96)
    grid_time = np.zeros(96)
    
    battery_load_curr = 0
    
    for i in range(96):
        price = float(prices[i])
        usage = float(usages[i])
        
        while info_list and info_list[0].get_cost() < price and usage > 0:
            curr_period = heapq.heappop(info_list)
            remaining_energy = curr_period.get_remaining_energy()
            
            if usage >= remaining_energy:
                usage -= remaining_energy
                battery_time[curr_period.get_start()] += remaining_energy
                battery_load_curr -= remaining_energy
            else:
                curr_period.lower_remaining_energy(usage)
                heapq.heappush(info_list, curr_period)
                battery_time[curr_period.get_start()] += usage
                battery_load_curr -= usage
                usage = 0
        
        if usage > 0:
            grid_time[i] += usage
            
        if  battery_load_curr < battery_cap:
            to_load = min(loading_per_segment, battery_cap - battery_load_curr)
            heapq.heappush(info_list, Info(to_load, battery_cost_per_kwh + price, i))
            battery_load_curr += to_load
        
        
        buy_time, sell_time = load_only_to_sell(battery_time, prices, battery)

    return battery_time, grid_time, buy_time, sell_time

