import pandas as pd
import os

def split_csv_by_day(input_file, output_dir=None):
    if not os.path.isfile(input_file):
        print(f"Error: The file {input_file} does not exist.")
        return
    
    try:
        df = pd.read_csv(input_file, names=["date", "fixing_i_price", "fixing_i_volume", "fixing_ii_price", "fixing_ii_volume"], skiprows=1)
    except pd.errors.EmptyDataError:
        print(f"Error: The file {input_file} is empty.")
        return
    except pd.errors.ParserError as e:
        print(f"Error parsing the file: {e}")
        return
    
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y %H:%M', errors='coerce')
    df = df.dropna(subset=['date'])
    
    df['day'] = df['date'].dt.date
    
    output_dir = output_dir or "../data_months/tge"
    os.makedirs(output_dir, exist_ok=True)
    
    for day, group in df.groupby('day'):
        prices = group['fixing_i_price'].tolist()
        repeated_prices = [price/1000.0 for price in prices for _ in range(4)]
        
        output_df = pd.DataFrame({'Data': repeated_prices})
        output_df.to_csv(os.path.join(output_dir, f"{day}.csv"), index=False)
        
        print(f"Saved: {day}.csv")

split_csv_by_day("../data_months/aggregate_files/tge_prices_since_July2024.csv")
