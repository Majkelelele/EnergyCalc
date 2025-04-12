import requests
import datetime
import csv

# Mapping znacznik values to G14_TAURON pricing
G14_TAURON = {
    0: 0.011,
    1: 0.047,
    2: 0.35,
    3: 2.35,
}

def fetch_data(selected_date=""):
    try:
        # Convert string to date
        date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
        next_date = date + datetime.timedelta(days=1)

        # Format for API
        date_str = date.strftime("%Y-%m-%d")
        next_date_str = next_date.strftime("%Y-%m-%d")
        
        # API URL
        url = f"https://api.raporty.pse.pl/api/pdgsz?$filter=udtczas ge '{date_str}' and udtczas lt '{next_date_str}'"
        print(url)
        # Get API response
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("value", [])

        mapped_values = []
        
        for item in data:
            znacznik = item.get("znacznik", None)
            if isinstance(znacznik, int) and znacznik in G14_TAURON:
                value = G14_TAURON[znacznik]
                mapped_values.extend([[value]] * 4)  # Repeat 4 times
                # print((f"{value}\n") * 4, end="")

        # Check row count
        if len(mapped_values) != 96:
            print(f"\nOstrzeżenie: {selected_date} — oczekiwano 96 wierszy, otrzymano {len(mapped_values)}.")

        # Save to CSV
        if mapped_values:
            filename = f"../data_months/kompas_energetyczny/{date_str}.csv"
            with open(filename, mode="w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Cena [zł/kWh]"])
                writer.writerows(mapped_values)
            print(f"Zapisano do pliku: {filename}\n")
        else:
            print(f"{selected_date} — Brak danych do zapisania.\n")

    except Exception as e:
        print(f"{selected_date} — Błąd: {e}\n")

def fetch_range(start_date="2024-07-01", end_date="2025-04-12"):
    current = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    while current <= end:
        fetch_data(current.strftime("%Y-%m-%d"))
        current += datetime.timedelta(days=1)

# Run for the full date range
fetch_range()
