import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# def generate_energy_usage(day, total_usage=7.5):
#     # Number of 15-minute periods in a day
#     num_periods = 24 * 4

#     # Generate base energy usage data
#     base_usage = np.random.uniform(0.01, 0.1, num_periods)

#     # Define peak periods (6-9 AM and 5-10 PM)
#     peak_periods = list(range(6 * 4, 8 * 4)) + list(range(14 * 4, 22 * 4))

#     # Increase energy usage during peak periods
#     for i in peak_periods:
#         base_usage[i] = np.random.uniform(0.2, 0.5)

#     # Ensure the total usage does not exceed 8 kWh
#     energy_usage = base_usage / base_usage.sum() * total_usage

#     # Create a DataFrame
#     df = pd.DataFrame({
#         'Energy_Usage_kWh': energy_usage
#     })
    
#     # Save to CSV
#     df.to_csv(f"../data_months/usage/{day}.csv", index=False)
    
# def generate_energy_usage_days(total_usage=7.5, days=360):
#     for i in range(days):
#         # Generate past date string (YYYY-MM-DD)
#         day = (datetime.now() - timedelta(days=i-1)).strftime("%Y-%m-%d")
#         generate_energy_usage(day, total_usage=total_usage)



def generate_energy_usage(day, total_usage=7.5):
    # Number of 15-minute periods in a day
    num_periods = 24 * 4

    # Parse the date
    date_obj = datetime.strptime(day, "%Y-%m-%d")
    weekday = date_obj.weekday()
    month = date_obj.month

    # Adjust total_usage based on season
    if month in [12, 1, 2]:
        total_usage += np.random.uniform(0.8, 2.0)
    elif month in [6, 7, 8]:
        total_usage -= np.random.uniform(0.5, 1.0)
    else:
        total_usage += np.random.uniform(-0.3, 0.5)

    if weekday >= 5:
        total_usage *= np.random.uniform(1.05, 1.15)

    # Generate base usage
    base_usage = np.random.uniform(0.01, 0.07, num_periods)

    morning_peak = range(6 * 4, 9 * 4)
    evening_peak = range(17 * 4, 22 * 4)
    night_low = range(0, 5 * 4)

    for i in morning_peak:
        base_usage[i] += np.random.uniform(0.1, 0.25)
    for i in evening_peak:
        base_usage[i] += np.random.uniform(0.2, 0.5)
    for i in night_low:
        base_usage[i] *= np.random.uniform(0.2, 0.4)

    # Normalize and clip to ensure sum equals target and length is correct
    energy_usage = base_usage / base_usage.sum() * total_usage
    energy_usage = energy_usage[:96]  # just in case
    if len(energy_usage) < 96:
        energy_usage = np.pad(energy_usage, (0, 96 - len(energy_usage)), 'constant')

    # Create DataFrame
    df = pd.DataFrame({
        'Energy_Usage_kWh': energy_usage
    })

    df.to_csv(f"../data_months/usage/{day}.csv", index=False)



def generate_energy_usage_days(total_usage=7.5, days=360):
    for i in range(days):
        day = (datetime.now() - timedelta(days=i - 1)).strftime("%Y-%m-%d")
        generate_energy_usage(day, total_usage=total_usage)

import matplotlib.pyplot as plt
import os

def read_usage_file(file_path):
    """Reads the CSV file and returns a list/array of usage values"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such file: {file_path}")
    
    df = pd.read_csv(file_path)
    
    if 'Energy_Usage_kWh' not in df.columns:
        raise ValueError("File must contain 'Energy_Usage_kWh' column")
    
    if len(df) != 96:
        raise ValueError(f"Expected 96 values, but got {len(df)} in file: {file_path}")
    
    return df['Energy_Usage_kWh'].values

def plot_usage(file_path):
    """Reads and plots the energy usage file"""
    usage = read_usage_file(file_path)

    time_labels = [f"{h:02}:00" for h in range(0, 24)]
    ticks = [i * 4 for i in range(24)]

    plt.figure(figsize=(12, 4))
    plt.plot(usage, label='Energy Usage (kWh)', color='dodgerblue')
    plt.xticks(ticks, time_labels, rotation=45)
    plt.ylabel("kWh")
    plt.title(f"Energy Usage - {os.path.basename(file_path).replace('.csv','')}")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.legend()
    plt.show()

# generate_energy_usage_days()
# plot_usage("../data_months/usage/2024-07-09.csv")
