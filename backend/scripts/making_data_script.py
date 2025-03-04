import pandas as pd
import numpy as np

def generate_energy_usage(day, total_usage=7.5):
    # Number of 15-minute periods in a day
    num_periods = 24 * 4

    # Generate base energy usage data
    base_usage = np.random.uniform(0.01, 0.1, num_periods)

    # Define peak periods (6-9 AM and 5-10 PM)
    peak_periods = list(range(6 * 4, 8 * 4)) + list(range(14 * 4, 22 * 4))

    # Increase energy usage during peak periods
    for i in peak_periods:
        base_usage[i] = np.random.uniform(0.2, 0.5)

    # Ensure the total usage does not exceed 8 kWh
    energy_usage = base_usage / base_usage.sum() * total_usage

    # Create a DataFrame
    df = pd.DataFrame({
        'Energy_Usage_kWh': energy_usage
    })

    # Save to CSV
    df.to_csv(f"../data_months/usage_{day:02d}.csv", index=False)
    
def generate_energy_usage_200days(total_usage=7.5):
    for i in range(200):
        generate_energy_usage(i, total_usage=total_usage)
        
generate_energy_usage_200days(7.5)
