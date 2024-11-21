import pandas as pd
from math import ceil

TIME_IDX = 0
CONSUMPTION_IDX = 1
COST_IDX = 2

class KAlg:
    def __init__(self,
                 charging_time,
                 charging_per_hour,
                 charge_level):
        self.charging_time = charging_time
        self.charging_per_hour = charging_per_hour
        self.charge_level = charge_level

    def krzysiek_algorithm(self, 
                           prices: pd.DataFrame, 
                           energy_usage: pd.DataFrame):
        assert prices.shape == energy_usage.shape, "Prices and energy usage should have the same shape"

        nbr_15min_periods_to_charge_battery = ceil((self.charging_time * 60) / 15)

        # TODO - battery could be so huge that there are not enough intervals
        # to charge it
        assert nbr_15min_periods_to_charge_battery >= len(prices), "Prices data is not in 15minute interval unit"


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
                                         
        self.__main_alg_loop(consumption_cost_lst,
                             battery_charging_times,
                             battery_charging_kw_per_15min)
    
    def __main_alg_loop(self,
                        consumption_cost_lst,
                        b_charging_times, 
                        b_charging_kw_per_15min):
        
        charge_time_idx = 0
        charge_time_period = b_charging_times[charge_time_idx][TIME_IDX]
        # here we store good charge times, so that we can easily check which 
        # times we cannot add again when optimizing
        charge_times_set = set()
        new_energy_in_b = 0
        needed_energy = 0

        # all_battery_cost needed to calc mean price of charging battery 
        all_b_charging_cost = 0
        for idx, cons, cost in b_charging_times:
            all_b_charging_cost += cost * b_charging_kw_per_15min

        mean_cost_to_charge_battery = all_b_charging_cost \
                                        / len(b_charging_times)
        # needed to sum whole cost of buying energy from grid
        all_grid_cost = 0

        for curr_time, consum, cost  in consumption_cost_lst:
            if curr_time == charge_time_period:
                # when we encounter charging period, since its one of the 
                # cheapest periods we take energy from grid, thus total cost 
                # we pay is for powering house and for powering battery
                all_grid_cost += (consum * cost  
                                  + b_charging_kw_per_15min * cost)
                new_energy_in_b += b_charging_kw_per_15min

                charge_times_set.add(charge_time_period)
                charge_time_idx += 1
                if charge_time_idx < len(b_charging_times):
                    charge_time_period = \
                            b_charging_times[charge_time_idx][TIME_IDX] 
            else:
                needed_energy += consum
                if self.charge_level + new_energy_in_b < needed_energy:
                    if consum * cost < mean_cost_to_charge_battery:
                        all_grid_cost += consum * cost
                    else:
                        pass

    def __adjust_charging_hours(self, 
                                consumption_cost_lst, 
                                battery_charging_times,
                                charge_time_set,
                                curr_time,
                                charge_time_period,
                                needed_energy,
                                new_energy_in_battery,
                                all_grid_cost,
                                battery_charging_kw_per_15min,
                                all_battery_charging_cost,
                                mean_charging_cost
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
                return False, new_energy_in_battery, all_grid_cost, all_battery_charging_cost, mean_charging_cost, charge_time_period

            

            if charge_time_period < found_time_min:
                charge_time_period = found_time_min
            
            found_time_max, max_cost = \
                        self.__find_max_charge_cost_after_curr_time(
                                                battery_charging_times, 
                                                curr_time, 
                                                battery_charging_kw_per_15min)
            if found_time_max < 0:
                print("Didnt find time, we need to remove AFTER CURRENT TIME")
                print("unexpected HIGH ENERGY consumption!!!")
                return -2

            self.__adjust_battery_charging_times(battery_charging_times, 
                                                    found_time_min, found_time_max)
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
        

        return 0, new_energy_in_battery, all_grid_cost, all_battery_charging_cost, mean_charging_cost, charge_time_period


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



