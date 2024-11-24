import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    idx_of_files = 7

    image_name = "../data/img_prices_usage" + str(idx_of_files) + ".png"
    prices_file_path = '../data/prices' + str(idx_of_files) + '.csv'
    usage_file_path = '../data/energy_usage' + str(idx_of_files) + '.csv'

    prices = pd.read_csv(prices_file_path)
    prices["price"] = prices["price"] / 1000

    usage = pd.read_csv(usage_file_path)

    # Create a time range for the X-axis
    time_range = pd.date_range(start='00:00', periods=len(prices), freq='15T')

    # # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(time_range, prices["price"], label='Price (per kWh)', color='blue')
    plt.plot(time_range, usage["Energy_Usage_kWh"], label='Energy Usage (kWh)', color='orange')

    # # Formatting the plot
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Prices and Energy Usage Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    # # Format the x-axis to show hours and minutes
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))

    # # Show the plot
    plt.tight_layout()
    plt.savefig(image_name)

if __name__ == "__main__":
    main()