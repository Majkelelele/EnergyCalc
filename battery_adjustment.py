
class Battery:
    def __init__(self, capacity: int, voltage, power_output, efficiency):
        self.capacity = capacity
        self.voltage = voltage
        self.power_output = power_output
        self.efficiency = efficiency

    def charging_time(self):
        return (self.capacity * self.voltage) / (self.power_output * self.efficiency)

    def calc_deposit_profit(self, prices, charging_time):
        size = len(prices)
        biggest_change = 0
        coords = (0,0)
        all_amplitudes = []
        for i in range(size):
            for j in range(i + 1, size):
                if prices[j] - prices[i] > biggest_change:
                    all_amplitudes.append([prices[j] - prices[i], i, j])

        all_amplitudes.sort(key=lambda x: x[0])
        idx = 1
        curr = all_amplitudes[0]
        while idx < size:
            if curr[1] == all_amplitudes[idx][1] or curr[2] == all_amplitudes[idx][2]:
                all_amplitudes.pop(idx)
            else:
                curr = all_amplitudes[idx]
            idx += 1

        sum = 0
        idx = 0

        while charging_time > 0:
            if charging_time < 1:
                sum += all_amplitudes[idx] * charging_time
            sum += all_amplitudes[idx]
            idx += 1
            charging_time -= 1


        return sum
