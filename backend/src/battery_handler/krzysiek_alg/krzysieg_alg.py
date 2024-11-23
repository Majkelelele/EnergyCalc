import pandas as pd
from math import ceil, inf
from typing import List
import matplotlib.pyplot as plt

TIME_IDX = 0
CONSUMPTION_IDX = 1
COST_IDX = 2

class AlgUpdateableData:
    def __init__(self,
                 charge_time_period, 
                 needed_energy, 
                 new_energy_in_b, 
                 all_b_charging_cost, 
                 mean_b_charging_cost,
                 b_charging_times: List,
                 charge_time_set: set
                 ):
        self.charge_time_period = charge_time_period
        self.needed_energy = needed_energy
        self.new_energy_in_b = new_energy_in_b
        self.all_b_charging_cost = all_b_charging_cost
        self.mean_b_charging_cost = mean_b_charging_cost
        self.b_charging_times = b_charging_times
        self.charge_time_set = charge_time_set

class KAlg:
    def __init__(self,
                 charging_time: float,
                 charging_per_hour: float,
                 charge_level: float,
                 battery_cost_per_kWh: float,
                 b_max_capacity: int):
        """
        - charging_time: hours 
        - charging_per_hour: kW 
        - charge_level: kWh 
        - kWh_battery_cost: zl - battery cost a lot of money thus we can 
        estimate the cost of charging the battery for 1kW
        """
        self.charging_time = charging_time
        self.charging_per_hour = charging_per_hour
        self.charge_level = charge_level
        self.kwh_battery_cost = battery_cost_per_kWh
        self.b_max_capacity = b_max_capacity

    def krzysiek_algorithm(self, 
                           prices: pd.DataFrame, 
                           energy_usage: pd.DataFrame):
        assert prices.shape == energy_usage.shape, "Prices and energy usage should have the same shape"

        nbr_15min_periods_to_charge_battery = ceil((self.charging_time * 60) / 15)

        # TODO - battery could be so huge that there are not enough intervals
        # to charge it
        if nbr_15min_periods_to_charge_battery >= len(prices):
            print("IMPLEMENT THIS CASE!!!!")

        prices = [price[0] for price in prices]
        energy_usage = [usage[0] for usage in energy_usage]

        consumption_cost_lst = [
            (idx , cons, cost) for idx, (cons, cost) in enumerate(zip(energy_usage, prices))
        ]

        battery_charging_per_15min = self.charging_per_hour / 4

        # We sort increasingly by cost * how much we can charge in 15 minutes
        sorted_consumption_cost_lst = sorted(consumption_cost_lst, key=lambda x: x[COST_IDX] * battery_charging_per_15min)
        
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
                                         
        lst_of_solutions = self.__find_optimal_charging_hours   (
                                                    consumption_cost_lst,
                                                    battery_charging_times,
                                                    battery_charging_per_15min)
        final_solution = self.__calc_final_solution(
                            consumption_cost_lst,
                            lst_of_solutions,
                            battery_charging_per_15min)
        return final_solution

    def __calc_final_solution(self,
                            consumption_cost_lst: List,
                            all_solutions: List[List],
                            b_charging_kw_per_15min: float) -> List:
        min_grid_cost = inf
        idx_of_min_grid_cost = 0
        final_grid_charging_idxs = []
        final_charging_amounts = []

        for sol_id, solution in enumerate(all_solutions):
            new_energy_in_b = 0
            needed_energy = 0
            all_grid_cost = 0
            cost_without_battery = 0
            charge_time_idx = 0
            charge_time_period = solution[charge_time_idx][TIME_IDX]
            grid_charging_idxs = []
            b_charging_amounts = []

            for curr_time, consum, cost in consumption_cost_lst:
                cost_without_battery += consum * cost
                if curr_time == charge_time_period:
                    # when we encounter charging period, since its one of the 
                    # cheapest periods we take energy from grid, thus total cost 
                    # we pay is for powering house and for powering battery
                    new_energy_in_b += b_charging_kw_per_15min

                    if new_energy_in_b + self.charge_level > self.b_max_capacity:
                        new_energy_in_b -= b_charging_kw_per_15min
                        last_charge = self.b_max_capacity - new_energy_in_b - self.charge_level
                        grid_charging_idxs.append((curr_time, consum + last_charge))
                        new_energy_in_b += last_charge
                        all_grid_cost += (consum * cost  
                                        + last_charge * cost 
                                        + last_charge * self.kwh_battery_cost)
                        b_charging_amounts.append(last_charge)
                    else:
                        grid_charging_idxs.append((curr_time, consum + b_charging_kw_per_15min))
                        all_grid_cost += (consum * cost  
                                        + b_charging_kw_per_15min * cost 
                                        + b_charging_kw_per_15min * self.kwh_battery_cost)
                        b_charging_amounts.append(b_charging_kw_per_15min)

                    charge_time_idx += 1
                    if charge_time_idx < len(solution):
                        charge_time_period = \
                                solution[charge_time_idx][TIME_IDX] 
                else:
                    needed_energy += consum
                    if self.charge_level + new_energy_in_b < needed_energy:
                        all_grid_cost += consum * cost
                        grid_charging_idxs.append((curr_time, consum))

            print(f"Solution {sol_id} cost: {round(all_grid_cost, 4)} zl, cost without battery: {round(cost_without_battery, 4)} zl")

            if all_grid_cost < min_grid_cost:
                min_grid_cost = all_grid_cost
                idx_of_min_grid_cost = sol_id
                final_grid_charging_idxs = grid_charging_idxs
                final_charging_amounts = b_charging_amounts

        if cost_without_battery < min_grid_cost:
            print("CHARGING BATTERY IS NOT WORTH IT -_-")
            return [], [time for time, _, _ in consumption_cost_lst]

        best_sol = [(time, charge_amount) 
                        for charge_amount, (time, _, _) in 
                        zip(final_charging_amounts, 
                            all_solutions[idx_of_min_grid_cost])
        ] 


        return best_sol, final_grid_charging_idxs

    def __find_optimal_charging_hours(self,
                        consumption_cost_lst: List,
                        b_charging_times: List, 
                        b_charging_kw_per_15min: float):
        # charge_time_idx- current index when iterating over charging_times list
        charge_time_idx = 0

        # charge_time_period- current index of time period (we have 15 minute 
        # time periods) we are checking
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

        mean_b_charging_cost = all_b_charging_cost \
                                        / len(b_charging_times)

        # we store all found solutions, so that we can easily check which
        # one was the best
        all_found_solutions = [list(b_charging_times)]

        for curr_time, consum, cost  in consumption_cost_lst:
            if curr_time == charge_time_period:
                new_energy_in_b += b_charging_kw_per_15min

                charge_times_set.add(charge_time_period)
                charge_time_idx += 1
                if charge_time_idx < len(b_charging_times):
                    charge_time_period = \
                            b_charging_times[charge_time_idx][TIME_IDX] 
            else:
                needed_energy += consum
                if self.charge_level + new_energy_in_b < needed_energy:
                    # if there is to little energy in battery we check if 
                    # buying energy from grid is cheaper than taking it from 
                    # battery if we had enough energy in it
                    # TODO - is it GOOD IDEA TO CHECK THAT?
                    if consum * cost > consum * mean_b_charging_cost:
                        alg_data = AlgUpdateableData(
                            charge_time_period, 
                            needed_energy, 
                            new_energy_in_b, 
                            all_b_charging_cost, 
                            mean_b_charging_cost,
                            b_charging_times,
                            charge_times_set
                        )
                        # we need to adjust charging hours
                        success, alg_data  = self.__adjust_charging_hours(
                                                    consumption_cost_lst,
                                                    curr_time,
                                                    b_charging_kw_per_15min,
                                                    alg_data
                                                )
                        if success:
                            charge_time_period = alg_data.charge_time_period
                            needed_energy = alg_data.needed_energy
                            new_energy_in_b = alg_data.new_energy_in_b
                            all_b_charging_cost = alg_data.all_b_charging_cost
                            mean_b_charging_cost = alg_data.mean_b_charging_cost
                            b_charging_times = alg_data.b_charging_times
                            charge_times_set = alg_data.charge_time_set

                            b_charging_times = sorted(b_charging_times, key=lambda x: x[TIME_IDX])
                            all_found_solutions.append(list(b_charging_times))
                            charge_time_idx = self.__find_new_charge_time_idx(
                                                            b_charging_times, 
                                                            charge_time_period)
                        # if not success we simply take energy from grid,
                        # since we cannot satisfy consumption only from battery
        return all_found_solutions

    def __adjust_charging_hours(self, 
                                consumption_cost_lst: List, 
                                curr_time: int,
                                b_charging_kw_per_15min: float,
                                alg_data: AlgUpdateableData):
        charge_time_period = alg_data.charge_time_period
        needed_energy = alg_data.needed_energy
        new_energy_in_b = alg_data.new_energy_in_b
        all_b_charging_cost = alg_data.all_b_charging_cost
        mean_b_charging_cost = alg_data.mean_b_charging_cost

        # we want to work on copies since adjusting might not always succeed
        # as a whole, it might encounter found_time < 0 in the middle of it, so 
        # we dont want to change the original data
        b_charging_times = list(alg_data.b_charging_times)
        charge_time_set = set(alg_data.charge_time_set)

        while (new_energy_in_b + self.charge_level < needed_energy):
            # We calculate minimal battery charging cost on [0, curr_time] 
            # interval, since we lacked energy for curr_time. There is a 
            # possibility that we will not find any free spot for charging,
            # because all of them might be already taken in charge_time_set, 
            # in that scenario we need to take energy from grid, since we cannot
            # satisfy consumption only from battery
            found_time_min, min_cost, consum_at_min, energy_cost_at_min = \
                                self.__find_time_with_min_charge_cost(
                                                consumption_cost_lst, 
                                                charge_time_set, 
                                                curr_time, 
                                                b_charging_kw_per_15min)
            if found_time_min < 0:
                print("Didnt find time, we need to take this energy from grid")
                print("unexpected HIGH ENERGY consumption!!!")
                # if something went wrong we always return original data
                return False, alg_data

            found_time_max, max_cost = \
                        self.__find_max_charge_cost_after_curr_time(
                                                b_charging_times, 
                                                curr_time, 
                                                b_charging_kw_per_15min)
            if found_time_max < 0:
                print("Didnt find time, we need to remove AFTER CURRENT TIME")
                print("unexpected HIGH ENERGY consumption!!!")
                return False, alg_data

            # we need to update most recent time we charged battery
            if charge_time_period < found_time_min:
                charge_time_period = found_time_min

            charge_time_set.add(found_time_min) 

            self.__adjust_battery_charging_times(consumption_cost_lst,
                                                    b_charging_times, 
                                                    found_time_min, found_time_max)
            # all charging times till curr_time are in charge_time_set,
            # curr_time cannot be in that set at the beginning of this function
            # since if it were we are in IF statement not in ELSE in main func
            new_energy_in_b += b_charging_kw_per_15min

            needed_energy -= consum_at_min

            all_b_charging_cost = all_b_charging_cost \
                                        + min_cost - max_cost
            mean_b_charging_cost = all_b_charging_cost / len(b_charging_times)
        
        updated_data = AlgUpdateableData(
            charge_time_period, 
            needed_energy, 
            new_energy_in_b, 
            all_b_charging_cost, 
            mean_b_charging_cost,
            b_charging_times,
            charge_time_set
        )
        return True, updated_data

    def __find_new_charge_time_idx(self,
                                    b_charging_times,
                                    charge_time_period):
        charge_time_idx = 0
        for time, _, _ in b_charging_times:
            if time == charge_time_period:
                break
            charge_time_idx += 1
        return charge_time_idx

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
    
    def __adjust_battery_charging_times(self,
                                        consumption_cost_lst, 
                                        battery_charging_times,
                                        found_time_min,
                                        found_time_max):
        """
        We remove the found_time_max from the battery_charging_times and add
        the found_time_min at the end of the list --> We need to sort the list
        in maing function again
        """
        new_val = consumption_cost_lst[found_time_min]
        battery_charging_times.append(new_val)
        idx = 0
        for i in range(len(battery_charging_times)):
            if battery_charging_times[i][TIME_IDX] == found_time_max:
                idx = i
                break

        battery_charging_times.pop(idx)

import matplotlib.dates as mdates

if __name__ == "__main__":
    # Example inputs
    prices = pd.read_csv("./prices.csv")
    prices["price"] = prices["price"] / 1000
    usage = pd.read_csv("./energy_usage.csv")

    # Create a time range for the X-axis
    # time_range = pd.date_range(start='00:00', periods=len(prices), freq='15T')

    # # Plot the data
    # plt.figure(figsize=(12, 6))
    # plt.plot(time_range, prices["price"], label='Price (per kWh)', color='blue')
    # plt.plot(time_range, usage["Energy_Usage_kWh"], label='Energy Usage (kWh)', color='orange')

    # # Formatting the plot
    # plt.xlabel('Time')
    # plt.ylabel('Value')
    # plt.title('Prices and Energy Usage Over Time')
    # plt.xticks(rotation=45)
    # plt.legend()
    # plt.grid(True)

    # # Format the x-axis to show hours and minutes
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))

    # # Show the plot
    # plt.tight_layout()
    # plt.savefig('obrazek.png')

    # Optimize battery usage
    kalg = KAlg(charging_time=5, charging_per_hour=2, charge_level=0, battery_cost_per_kWh=0.266)
    solution = kalg.krzysiek_algorithm(prices, usage)
    # print(solution)
    # print("DONE")

