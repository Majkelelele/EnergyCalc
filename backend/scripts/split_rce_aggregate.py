import pandas as pd
import os

def split_csv_by_day(input_file, output_dir=None):
    if not os.path.isfile(input_file):
        print(f"Error: The file {input_file} does not exist.")
        return
    
    try:
        df = pd.read_csv(input_file, sep=';', names=["Doba handlowa", "Doba", "OREB [Jednostka czasu od-do]", "RCE [zł/MWh]", "Data publikacji"], skiprows=1, quotechar='"')
    except pd.errors.EmptyDataError:
        print(f"Error: The file {input_file} is empty.")
        return
    except pd.errors.ParserError as e:
        print(f"Error parsing the file: {e}")
        return
    
    df['date'] = pd.to_datetime(df['Doba'], format='%Y-%m-%d', errors='coerce')
    df = df.dropna(subset=['date'])
    
    df['day'] = df['date'].dt.date
    
    output_dir = output_dir or "../data_months/rce"
    os.makedirs(output_dir, exist_ok=True)
    
    for day, group in df.groupby('day'):
        prices = group['RCE [zł/MWh]'].tolist()
        prices = [price / 1000.0 for price in prices]
        
        output_df = pd.DataFrame({'Data': prices})
        output_df.to_csv(os.path.join(output_dir, f"{day}.csv"), index=False)
        
        print(f"Saved: {day}.csv")

split_csv_by_day("../data_months/aggregate_files/RCE_2024-07-01_2024-08-01.csv")
