import pandas as pd
from battery_handler.battery_handler import Battery
import matplotlib.pyplot as plt

possible_cycles = 1500
battery_price = 20000
installation_cost = 0
current_month = "November"
# PGE
trade_fee_per_month = 49.90
trade_fee_per_day = trade_fee_per_month/30
additional_shit_idont_know = 0
expected_energy_usage_yearly_kWH = 3000
expected_daily_energy_usage = expected_energy_usage_yearly_kWH / 365
number_of_segments_daily = 24

# import daily distribution of power use per hour
expected_daily_energy_distribution = pd.read_csv("../data/distribution.csv").values

solar_power_monthly = pd.read_csv("../data/SolarPower.csv")

# calculate daily usage of power in kWH per hour
hours_usage_day_kWH = expected_daily_energy_distribution * expected_daily_energy_usage
# fetching daily dynamic prices per hour per mWh
prices = pd.read_csv("../data/prices.csv")
# prices are in zl per MWh, we want them in zl per kWh
prices = prices.values / 1000
hours_cost_day_kWH = prices

# calculating K from cost equation - see backend/docs/Zalacznik-nr-2-Algorytm-wyznaczania-ceny.pdf
K_pge_kWH = 0.0812
K_month = hours_usage_day_kWH.sum() * K_pge_kWH
K_day = K_month/30

# calculating A from cost equation
A_mWH = 5
A_kwH = 5 / 1000
A_month = A_kwH * hours_usage_day_kWH.sum()
A_day = A_month/30

def calc_energy_price_daily(solar_deduction):
    cost_energy_alone = ((hours_usage_day_kWH - solar_deduction) * hours_cost_day_kWH).sum()
    return cost_energy_alone + K_day + A_day

def calc_brutto_price_daily(solar_deduction):
    return calc_energy_price_daily(solar_deduction) + trade_fee_per_day + additional_shit_idont_know



if __name__ == "__main__":
    solar_power_output = solar_power_monthly.loc[solar_power_monthly["Month"] == current_month, "PowerOutput"].values[0]

    battery = Battery(
        price=16000, 
        capacity=10, 
        DoD=0.95, 
        efficiency=0.9, 
        life_cycles=6000
        )
    print(f"deposit profit: {battery.calc_deposit_profit((prices.copy() - solar_power_output )/ number_of_segments_daily)}")
    print(f"energy cost per day = {round(calc_brutto_price_daily(solar_power_output), 3)}zl")
    print(f"energy cost if using battery for autoconsumption {battery.calc_battery_autonsumption_cost(prices - solar_power_output / number_of_segments_daily,expected_daily_energy_usage)}")
    # Example inputs
    # prices = np.random.uniform(0.1, 0.5, 96)  # Random energy prices for 96 slots
    # usage = np.random.uniform(0, 2, 96)  # Random energy usage for 96 slots

    # Optimize battery usage
    # total_cost, battery_states, actions = optimize_battery(prices, hours_usage_day_kWH)

    # # Print results
    # print(f"Total Cost: {total_cost}")
    # print(f"Battery States: {battery_states}")
    # print(f"Actions: {actions}")
    # plt.plot(np.arange(0, 24), prices, label="Energy Prices")
    # plt.xlabel("Hour of Day")
    # plt.ylabel("Price (arbitrary units)")
    # plt.title("Energy Prices Over 24 Hours")
    # plt.legend()
    # plt.grid(True)
    # # plt.show()
    # # plt.savefig("plot.png")  # Save the plot to a file

    # plt.plot(np.arange(0, 24), hours_usage_day_kWH, label="usage")
   
    # # plt.show()
    # plt.savefig("plot.png")  # Save the plot to a file

    

