from battery_handler.consts import DEFAULT_VOLTAGE, DEFAULT_AMPERAGE
import pandas as pd
from math import ceil
import numpy as np

class Battery:
    # TODO - add more description to used algorithms in Battery class 
    def __init__(
            self, 
            price: float,
            capacity: int, 
            DoD: float, 
            efficiency: float,
            life_cycles: int,
            socket_amperage: int = DEFAULT_AMPERAGE,
            socket_voltage: int = DEFAULT_VOLTAGE,
            full_cycles_done = 0
            ):
        # Price of the battery
        self.price = price
        # Battery capacity in kWh
        self.capacity = capacity

        # Depth of Discharge (DoD) is the fraction of the battery that is
        # discharged relative to the overall capacity of the battery.
        self.DoD = DoD

        self.socket_amperage = socket_amperage
        self.socket_voltage = socket_voltage

        # Socket power output in kW (socket that we plugged the battery in)
        self.socket_power_output = (socket_amperage * socket_voltage) / 1000

        # The battery charging efficiency is the ratio between the energy 
        # consumed by the charging process and saved battery energy.
        # e.g. 0.9 means 90% efficiency
        self.efficiency = efficiency

        self.charging_time = self.__charging_time()

        # The battery life cycles. The number of cycles a battery can undergo 
        # is directly related to its lifespan. After this number of cycles,
        # the battery capacity will drop (for example to  80% of its original capacity).
        self.life_cycles = life_cycles

        # The number of full cycles the battery has undergone.
        self.full_cycles_done = full_cycles_done
        
    def __charging_time(self):
        return (self.capacity * self.DoD) \
                / (self.socket_power_output * self.efficiency)

    def check_how_many_cycles_and_change_capacity(self):
        if self.life_cycles >= self.full_cycles_done:
            self.capacity = self.capacity * 0.8
            self.full_cycles_done = 0
            self.DoD = 0.8

    def one_cycle_cost(self):
        return self.price / self.life_cycles

    # TODO - add one big descriptive comment about what is happening here
    # prices - 24 ceny godzinowe
    # TODO add adjusting by DoD
    def __calc_min_interval(self, prices: pd.DataFrame):
        size = len(prices)
        
        
        curr_sum = np.sum(prices[:ceil(self.charging_time)])
        min_price_sum = curr_sum
        curr_start = 0
        final_start = 0
        final_end = ceil(self.charging_time) - 1
        for curr_hour in range(ceil(self.charging_time), size):
            if curr_sum < min_price_sum:
                min_price_sum = curr_sum
                final_end = curr_hour - 1
                final_start = curr_start

            curr_sum -= prices[curr_start]
            curr_sum += prices[curr_hour]
            curr_start += 1
        return min_price_sum, final_start, final_end
    
    def __calc_max_interval(self, prices: pd.DataFrame, min_end: int):
        size = len(prices)
        curr_start = min_end + 1
        curr_sum = np.sum(prices[curr_start: curr_start + ceil(self.charging_time)])
        max_price_sum = curr_sum
        
        final_start = curr_start
        final_end =  curr_start + ceil(self.charging_time) - 1

        for curr_hour in range(final_end + 1, size):
            if curr_sum > max_price_sum:
                max_price_sum = curr_sum
                final_end = curr_hour - 1
                final_start = curr_start

            curr_sum -= prices[curr_start]
            curr_sum += prices[curr_hour]
            curr_start += 1
        return max_price_sum, final_start, final_end
    
    def efficient_charging_algorithm(self, prices: pd.DataFrame):
        min_price_sum, min_interval_start, min_interval_end = \
                                                self.__calc_min_interval(prices)
        max_price_sum, max_interval_start, max_interval_end = \
                            self.__calc_max_interval(prices, min_interval_end)
        
        return max_price_sum - min_price_sum

    def calc_deposit_profit(self, prices):
        prices_new = prices.flatten()
        return self.efficient_charging_algorithm(prices_new) - self.one_cycle_cost()

if __name__ == '__main__':
    battery = Battery(capacity=10, DoD=0.95, efficiency=0.9, life_cycles=1000)
    print(f"{round(battery.charging_time, 2)}h")
