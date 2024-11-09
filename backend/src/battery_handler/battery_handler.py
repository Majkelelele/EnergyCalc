class Battery:
    # TODO - add more description to used algorithms in Battery class 
    def __init__(
            self, 
            capacity: int, 
            voltage: int, 
            power_output: int, 
            efficiency: float
            ):
        # Watt hours = Amp hours × Volts
        # Milliamp hours = Amp hours × 1000
        # Battery capacity in Ah
        self.capacity = capacity
        # Battery voltage in V
        self.voltage = voltage
        # Battery power output in W
        self.power_output = power_output
        # The battery charging efficiency is the ratio between the energy 
        # consumed by the charging process and saved battery energy.
        self.efficiency = efficiency

    def charging_time(self):
        # is it good formula?
        return (self.capacity * self.voltage) \
                / (self.power_output * self.efficiency)

    # TODO - add one big descriptive comment about what is happening here
    def calc_deposit_profit(self, prices, charging_time):
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
                sum += amplitude * charging_time
                charging_time = 0
            idx += 1

        return sum

if __name__ == '__main__':
    battery = Battery(10, 5, 2, 0.9)
    prices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    charging_time = battery.charging_time()
    print(battery.calc_deposit_profit(prices, charging_time))