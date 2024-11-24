import pandas as pd
import numpy as np

def generate_energy_usage():
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
    total_usage = 7.5  # Total usage in kWh
    energy_usage = base_usage / base_usage.sum() * total_usage

    # Create a DataFrame
    df = pd.DataFrame({
        'Energy_Usage_kWh': energy_usage
    })

    # Save to CSV
    df.to_csv('../data/energy_usage7.csv', index=False)

    print("CSV file 'energy_usage.csv' has been created.")

def row_duplication():
    file_path = '../data/prices7.csv'
    # Read the CSV file into a DataFrame
    prices_df = pd.read_csv(file_path)

    # Duplicate the rows
    duplicated_prices_df = prices_df.loc[prices_df.index.repeat(4)].reset_index(drop=True)

    # Save the modified DataFrame back to a CSV file (optional)
    duplicated_prices_df.to_csv(file_path, index=False)

    print(duplicated_prices_df)

generate_energy_usage()