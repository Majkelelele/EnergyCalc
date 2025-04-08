import requests
import datetime
import csv
import os

def fetch_data(selected_date=""):
    try:
        # Parse the selected date
        # date = datetime.datetime.strptime(selected_date, "%d/%m/%Y")
        # next_date = date + datetime.timedelta(days=1)
        formatted_date = "2025-04-08"
        formatted_next_date = "2025-04-09"
        
        # Prepare URL for fetching data
        url = f"https://api.raporty.pse.pl/api/pdgsz?$filter=udtczas ge '{formatted_date}' and udtczas lt '{formatted_next_date}'"
        
        # Fetch data from API
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        data = data.get("value", [])

        # Map for znacznik values
        znacznik_map = {
            0: "ZALECANE UŻYTKOWANIE",
            1: "NORMALNE UŻYTKOWANIE",
            2: "ZALECANE OSZCZĘDZANIE",
            3: "WYMAGANE OGRANICZANIE"
        }
        
        # CSV rows to be written
        csv_rows = []
        
        # Initialize values for business date and source datetime
        business_date_value = "Brak danych"
        source_datetime_value = "Brak danych"
        
        for item in data:
            # Extract required values from API response
            udtczas = item.get("udtczas", "Brak danych")
            hour = udtczas.split(" ")[1] if udtczas != "Brak danych" else "Brak danych"
            znacznik = item.get("znacznik", "Brak danych")
            znacznik_text = znacznik_map.get(znacznik, "Nieznany znacznik")
            business_date = item.get("business_date", "Brak danych")
            source_datetime = item.get("source_datetime", "Brak danych")
            
            if source_datetime != "Brak danych":
                source_datetime = source_datetime.split(".")[0]
            
            if business_date != "Brak danych" and business_date_value == "Brak danych":
                business_date_value = business_date
            if source_datetime != "Brak danych" and source_datetime_value == "Brak danych":
                source_datetime_value = source_datetime
            
            # Print data (you can replace this with other logic if needed)
            print(f"Godzina: {hour}, Alert: {znacznik_text}")
            
            # Prepare CSV row
            csv_rows.append([hour, znacznik_text])

        # Output business date and source datetime to the console
        print(f"\nDoba handlowa: {business_date_value}")
        print(f"Data publikacji: {source_datetime_value}")
        
        # Save data to CSV
        if csv_rows:
            filename = f"alerty_{formatted_date}.csv"
            with open(filename, mode="w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Godzina", "Alert"])
                writer.writerows(csv_rows)
            print(f"Dane zapisano do pliku: {filename}")
        
    except Exception as e:
        print(f"Błąd: {e}")

# Prompt user to enter the date (DD/MM/YYYY format)
selected_date = input("03/03/2025")

# Fetch and save the data based on the selected date
fetch_data(selected_date)
