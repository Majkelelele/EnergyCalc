import pandas as pd
import matplotlib.pyplot as plt

# Read CSV file
data = pd.read_csv('../data_months/usage_150.csv')

# Check if the column exists
if 'Energy_Usage_kWh' in data.columns:
    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.plot(data['Energy_Usage_kWh'], marker='o', linestyle='-', color='b', label='Energy Usage (kWh)')
    plt.xlabel('Index')
    plt.ylabel('Energy Usage (kWh)')
    plt.title('Energy Usage Over Time')
    plt.legend()
    plt.grid()
    plt.show()
else:
    print("Column 'Energy_Usage_kWh' not found in the CSV file.")