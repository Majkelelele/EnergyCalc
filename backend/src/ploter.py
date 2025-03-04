import pandas as pd
import matplotlib.pyplot as plt

# Read CSV file
usage = pd.read_csv('../data_months/usage_150.csv')
prices_march = pd.read_csv('../data_months/enea_2025-03-01.csv')
prices_november = pd.read_csv('../data_months/enea_2024-11-13.csv')
prices_aug = pd.read_csv('../data_months/enea_2024-08-29.csv')


# Check if the column exists
plt.figure(figsize=(10, 5))
plt.plot(usage, marker='o', linestyle='-', color='b', label='Energy Usage (kWh)')
plt.plot(prices_march, marker='o', linestyle='-', color='g', label='prices march per kWh')
plt.plot(prices_november, marker='o', linestyle='-', color='y', label='prices aug per kWh')
plt.plot(prices_aug, marker='o', linestyle='-', color='black', label='prices november per kWh')

plt.xlabel('15min periods')
plt.ylabel('Energy(kWh)')
plt.title('XXX')
plt.legend()
plt.grid()
plt.show()
