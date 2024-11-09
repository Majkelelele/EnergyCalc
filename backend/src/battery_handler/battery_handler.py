from battery_handler.consts import DEFAULT_VOLTAGE, DEFAULT_AMPERAGE

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
            full_cycles = 0
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
        self.full_cycles = full_cycles
        
    def __charging_time(self):
        return (self.capacity * self.DoD) \
                / (self.socket_power_output * self.efficiency)

    def check_how_many_cycles_and_change_capacity(self):
        if self.life_cycles >= self.life_cycles:
            self.capacity = self.capacity * 0.8
            self.full_cycles = 0
            self.DoD = 0.8

    # TODO - add one big descriptive comment about what is happening here
    # prices - 24 ceny godzinowe
    def calc_deposit_profit(self, prices):
        size = len(prices)
        all_amplitudes = []
        for i in range(size):
            for j in range(i + 1, size):
                amplitude = prices[j] - prices[i]
                # We only consider profitable transactions
                if amplitude > 0:  
                    all_amplitudes.append([amplitude, i, j])

        # Sort in descending order to maximize profit
        all_amplitudes.sort(key=lambda x: x[0], reverse=True)

        # Select non-overlapping transactions
        selected_amplitudes = []
        used_times = set()

        for amplitude in all_amplitudes:
            buy_time, sell_time = amplitude[1], amplitude[2]
            # Check if times are not already used
            if buy_time not in used_times and sell_time not in used_times:
                selected_amplitudes.append(amplitude)
                used_times.update([buy_time, sell_time])

        # Calculate total profit based on charging time
        sum = 0
        idx = 0
        total_amplitudes = len(selected_amplitudes)

        while charging_time > 0 and idx < total_amplitudes:
            amplitude = selected_amplitudes[idx][0]
            if charging_time >= 1:
                sum += amplitude
                charging_time -= 1
            else:
                sum += amplitude * self.charging_time
                charging_time = 0
            idx += 1

        return sum
    
    def one_cycle_cost(self):
        return self.price / self.life_cycles

if __name__ == '__main__':
    battery = Battery(capacity=10, DoD=0.95, efficiency=0.9, life_cycles=1000)
    print(f"{round(battery.charging_time, 2)}h")
