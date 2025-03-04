import heapq
from battery_handler.battery_handler import Battery

class Info:
    def __init__(self, remaining_energy, cost, start):
        self.remaining_energy = remaining_energy
        self.cost = cost
        self.start = start

    def __lt__(self, other):
        return self.cost < other.get_cost()

    def get_cost(self):
        return self.cost

    def get_remaining_energy(self):
        return self.remaining_energy

    def lower_remaining_energy(self, amount):
        self.remaining_energy -= amount

    def get_start(self):
        return self.start

def best_algos_ever(prices, usages, battery:Battery):
    assert len(prices) == len(usages), "different lengths of prices and usages"
    assert type(prices) == type(usages) == list, "prices or usages are not list"
    battery_cost_per_kwh = battery.one_kwh_cost()
    loading_per_segment = battery.charging_per_segment()
    battery_cap = battery.capacity
    
    battery_cost_per_15min = battery_cost_per_kwh * loading_per_segment
    info_list = []
    battery_time = []
    grid_time = []
    battery_load_curr = 0
    
    for i, (price, usage) in enumerate(zip(prices, usages)):
        usage = float(usage)
        
        while info_list and info_list[0].get_cost() < price and usage > 0:
            curr_period = heapq.heappop(info_list)
            remaining_energy = curr_period.get_remaining_energy()
            
            if usage >= remaining_energy:
                usage -= remaining_energy
                battery_time.append((curr_period.get_start(), remaining_energy))
                battery_load_curr -= remaining_energy
            else:
                curr_period.lower_remaining_energy(usage)
                heapq.heappush(info_list, curr_period)
                battery_time.append((curr_period.get_start(), usage))
                battery_load_curr -= usage
                usage = 0
        
        if usage > 0:
            grid_time.append((i, usage)) 
            if loading_per_segment - usage > 0 and battery_load_curr < battery_cap:
                to_load = min(loading_per_segment - usage, battery_cap - battery_load_curr)
                heapq.heappush(info_list, Info(to_load, battery_cost_per_kwh + price, i))
                battery_load_curr += to_load

        else:
            to_load = min(loading_per_segment, battery_cap - battery_load_curr)
            battery_load_curr += to_load
            heapq.heappush(info_list, Info(to_load, price + battery_cost_per_kwh, i))
 

    return battery_time, grid_time
