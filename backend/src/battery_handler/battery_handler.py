class Battery:

    def __init__(
            self, 
            capacity: int, 
            voltage: int, 
            power_output: int, 
            efficiency: float
            ):
        self.capacity = capacity
        self.voltage = voltage
        self.power_output = power_output
        self.efficiency = efficiency

    def charging_time(self):
        return (self.capacity * self.voltage) \
                / (self.power_output * self.efficiency)

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

