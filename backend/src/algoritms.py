from bisect import insort

class Info():
    def __init__(self, remaining_energy, cost, start):
        self.remaining_energy  = remaining_energy
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

# class SortedInfoList:
#     def __init__(self):
#         self._data = []

#     def add(self, info):
#         insort(self._data, (info.get_cost(), info))
    
#     def first(self):
#         return self._data[0][1] if self._data else None
    
#     def pop(self):
#         return self._data.pop()[0][1] if self._data else None

def best_algos_ever(prices, usages, battery_cost_per_kwh, loading_per_segment):
    battery_cost_per_15min = battery_cost_per_kwh * loading_per_segment
    info_list = []
    battery_time = []
    grid_time = []
    i = 0
    for price, usage in zip(prices, usages):
        usage = float(usage)
        info_list.insert(0, Info(loading_per_segment,price + battery_cost_per_15min, i))
        info_list.sort()
        if len(info_list) != 0 and info_list[0].get_cost() < price:
            while len(info_list) != 0 and info_list[0].get_cost() < price and usage >= info_list[0].get_remaining_energy():
                curr_period = info_list.pop(0)
                remaining_energy = curr_period.get_remaining_energy()
                usage -= remaining_energy
                battery_time.append((curr_period.get_start(), remaining_energy))
            if info_list[0] != 0 and info_list[0].get_cost() < price:
                curr_period = info_list[0]
                curr_period.lower_remaining_energy(usage)
                battery_time.append((curr_period.get_start(), usage))
            else:
                grid_time.append((i, usage)) 
        else:
            grid_time.append((i, usage)) 
            # use grid
        i += 1
    return battery_time, grid_time

        