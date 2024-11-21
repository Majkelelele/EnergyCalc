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
            charge_level: float = 0.0,
            socket_amperage: int = DEFAULT_AMPERAGE,
            socket_voltage: int = DEFAULT_VOLTAGE,
            full_cycles_done = 0,
            ):
        # Price of the battery
        self.price = price
        # Battery capacity in kWh
        self.capacity = capacity

        # Battery current charge level in kWh
        if charge_level > self.capacity:
            except ValueError("charge level of battery greater than its capacit")
        self.charge_level = charge_level

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

        # how many kwh can be charged per hour
        self.charging_per_hour = self.__calculate_charging_per_hour()
        
    def __charging_time(self) -> float:
        return ((self.capacity - self.charge_level) * self.DoD) \
                / (self.socket_power_output * self.efficiency)

    def __max_charging_time(self) -> float:
        return (self.capacity * self.DoD) \
                / (self.socket_power_output * self.efficiency)

    
    def __calculate_charging_per_hour(self) -> float:
        return self.capacity / self.__max_charging_time()

    def check_how_many_cycles_and_change_capacity(self):
        # TODO - should be <=
        if self.life_cycles >= self.full_cycles_done:
            self.capacity = self.capacity * 0.8
            self.full_cycles_done = 0
            self.DoD = 0.8

    def one_cycle_cost(self):
        return self.price / self.life_cycles

    def __find_time_with_min_charge_cost(self,
                                        consump_cost_lst,
                                        charge_time_set,
                                        curr_time,
                                        battery_charging_kw_per_15min):
        min_cost = 100000
        found_time = -1
        consumption_at_found_time = 0
        energy_cost = 0
        for time, cons, cost in consump_cost_lst:
            if time > curr_time:
                break
            if time not in charge_time_set:
                new_cost = cost * battery_charging_kw_per_15min
                if new_cost < min_cost:
                    min_cost = new_cost
                    found_time = time
                    consumption_at_found_time = cons
                    energy_cost = cost
        
        return found_time, min_cost, consumption_at_found_time, energy_cost

    def __find_max_charge_cost_after_curr_time(self,
                                               battery_charging_times,
                                               curr_time,
                                               battery_charging_kw_per_15min):
        max_cost = 0
        found_time = -1
        for time, cons, cost in battery_charging_times:
            if time > curr_time:
                new_cost = cost * battery_charging_kw_per_15min
                if new_cost > max_cost:
                    found_time = time
                    max_cost = new_cost

        return found_time, max_cost
    
    def __adjust_battery_charging_times(consumption_cost_lst, 
                                        battery_charging_times,
                                        found_time_min,
                                        found_time_max):
        new_val = consumption_cost_lst[found_time_min]
        battery_charging_times.append(new_val)
        idx = 0
        for i in range(len(battery_charging_times)):
            if battery_charging_times[i][0] == found_time_max:
                idx = i
                break

        battery_charging_times.pop(idx)


    def __adjust_charging_hours(self, 
                                consumption_cost_lst, 
                                battery_charging_times,
                                charge_time_set,
                                curr_time,
                                needed_energy,
                                new_energy_in_battery,
                                all_grid_cost,
                                battery_charging_kw_per_15min,
                                all_battery_charging_cost
                                ):
        while (new_energy_in_battery + self.charge_level < needed_energy):
            # We calculate minimal battery charging cost on [0, curr_time] 
            # interval, since we lacked energy for curr_time, there is a 
            # possibility that we will not find any free spot for charging,
            # because all of them might be already taken in charge_time_set, 
            # in that scenario we need to take energy from grid, since we cannot
            # satisfy consumption only from battery
            found_time_min, min_cost, consum_at_min, energy_cost_at_min = \
                                self.__find_time_with_min_charge_cost(
                                                consumption_cost_lst, 
                                                charge_time_set, 
                                                curr_time, 
                                                battery_charging_kw_per_15min)
            if found_time_min < 0:
                print("Didnt find time, we need to take this energy from grid")
                print("unexpected HIGH ENERGY consumption!!!")
                return False
            
            found_time_max, max_cost = \
                        self.__find_max_charge_cost_after_curr_time(
                                                battery_charging_times, 
                                                curr_time, 
                                                battery_charging_kw_per_15min)
            if found_time_max < 0:
                print("Didnt find time, we need to remove AFTER CURRENT TIME")
                print("unexpected HIGH ENERGY consumption!!!")
                return False


            # all charging times till curr_time are in charge_time_set,
            # curr_time cannot be in that set at the beginning of this function
            # since if it were we are in IF statement not in ELSE in main func
            charge_time_set.add(found_time_min)
            new_energy_in_battery += battery_charging_kw_per_15min

            all_grid_cost = all_grid_cost \
                            + min_cost \
                            + energy_cost_at_min * consum_at_min
            needed_energy -= consum_at_min

            all_battery_charging_cost = all_battery_charging_cost \
                                        + min_cost - max_cost
            mean_charging_cost = all_battery_charging_cost / len(battery_charging_times)

            


    def krzysiek_algorithm(self, 
                           prices: pd.DataFrame, 
                           energy_usage: pd.DataFrame):
        assert prices.shape == energy_usage.shape, "Prices and energy usage should have the same shape"

        nbr_15min_periods_to_charge_battery = ceil((self.charging_time * 60) / 15)

        assert nbr_15min_periods_to_charge_battery >= len(prices), "Prices data is not in 15minute interval unit"

        TIME_IDX = 0
        CONSUMPTION_IDX = 1
        COST_IDX = 2

        consumption_cost_lst = [
            (idx , cons, cost) for idx, (cons, cost) in enumerate(zip(energy_usage, prices))
        ]

        battery_charging_kw_per_15min = self.charging_per_hour / 4
        # We sort increasingly by cost * how much we can charge in 15 minutes
        sorted_consumption_cost_lst = sorted(consumption_cost_lst, key=lambda x: x[COST_IDX] * battery_charging_kw_per_15min)

        # We take the first n elements from the sorted list, meaning these are 
        # the cheapest periods to charge the battery - thus we have the best 
        # possible solution now - we will make it a little less optimal since we
        # want to guarantee that in every moment during the day we have enough 
        # energy in battery to power our house
        battery_charging_times = sorted_consumption_cost_lst[:nbr_15min_periods_to_charge_battery]

        # We sort the battery charging times by the index of the period, so that
        # we can charge the battery in the correct order
        battery_charging_times = sorted(battery_charging_times,
                                         key=lambda x: x[TIME_IDX])

        charge_time_idx = 0
        charge_time_period = battery_charging_times[charge_time_idx][TIME_IDX]
        # here we store good charge times, so that we can easily check which 
        # times we cannot add again when optimizing
        charge_times_set = set()

        new_energy_in_battery = 0
        needed_energy = 0

        # all_battery_cost needed to calc mean price of charging battery 
        all_battery_charging_cost = 0
        for idx, cons, cost in battery_charging_times:
            all_battery_charging_cost += cost * battery_charging_kw_per_15min
        mean_cost_to_charge_battery = all_battery_charging_cost \
                                        / len(battery_charging_times)
        # needed to sum whole cost of buying energy from grid
        all_grid_cost = 0

        for curr_hour, consumption, cost  in consumption_cost_lst:
            if curr_hour == charge_time_period:
                # when we encounter charging period, since its one of the 
                # cheapest periods we take energy from grid, thus total cost 
                # we pay is for powering house and for powering battery
                all_grid_cost += (consumption * cost  
                                  + battery_charging_kw_per_15min * cost)
                new_energy_in_battery += battery_charging_kw_per_15min

                charge_times_set.add(charge_time_period)
                charge_time_idx += 1
                if charge_time_idx < len(battery_charging_times):
                    charge_time_period = \
                            battery_charging_times[charge_time_idx][TIME_IDX] 
            else:
                needed_energy += consumption
                if self.charge_level + new_energy_in_battery < needed_energy:
                    if consumption * cost < mean_cost_to_charge_battery:
                        all_grid_cost += consumption * cost
                    else:
                        pass



            


        

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
        return (max_price_sum - min_price_sum) * self.charging_per_hour

    def calc_deposit_profit(self, prices):
        prices_new = prices.flatten()
        print(f"roznica = {self.efficient_charging_algorithm(prices_new)}")
        return self.efficient_charging_algorithm(prices_new) - self.one_cycle_cost()
    
    def calc_battery_autonsumption_cost(self, prices, energy_needed): 
        prices = prices.flatten()
        charging_cost = 0
        i = 0
        while(energy_needed >= self.charging_per_hour):
            energy_needed -= self.charging_per_hour
            charging_cost += self.charging_per_hour * prices[i]
            i += 1

        charging_cost += energy_needed  * prices[i]
        
        return charging_cost + self.one_cycle_cost()


if __name__ == '__main__':
    battery = Battery(capacity=10, DoD=0.95, efficiency=0.9, life_cycles=1000)
    print(f"{round(battery.charging_time, 2)}h")
