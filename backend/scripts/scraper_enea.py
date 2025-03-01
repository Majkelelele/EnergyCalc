from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import time
import csv
import os


options = Options()
# options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.enea.pl/ceny-dynamiczne"

try:
    driver.get(url)
    time.sleep(3)  

    cokkies_xpath = '/html/body/div[1]/div/div[4]/div/div[2]/button[4]'
    base_xpath = '//*[@id="questions"]/section/div/div/div/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[{}]/td[2]'
    input_xpath = '/html/body/div[1]/div[4]/section/div/div/div/div/div[1]/span/input'

    cookies = driver.find_element(By.XPATH, cokkies_xpath)
    cookies.click()
    time.sleep(5)
    start_date = datetime(2025, 3, 1)
    end_date = datetime(2024, 8, 23)
    current_date = start_date

    while current_date >= end_date:
        date_str = current_date.strftime("%Y-%m-%d")  # Format as YYYY-MM-DD
        date_input = driver.find_element(By.ID, "raportDate")
        date_input.clear()
        date_input.send_keys(date_str)
        date_input.send_keys(Keys.RETURN)  
        current_date -= timedelta(days=1)
        i = 1
        scraped_data = []
        while True:
            try:
                current_xpath = base_xpath.format(i)

                element = driver.find_element(By.XPATH, current_xpath)

                scraped_data.append(element.text.replace(",","."))
            except:
                break

            i += 1

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_folder = os.path.join(script_dir, "../data_months")
        os.makedirs(output_folder, exist_ok=True)
        csv_file_path = os.path.join(output_folder, f"enea_{date_str}.csv")

        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Data"])
            for data in scraped_data:
                for i  in range(4):
                    writer.writerow([data])        
        time.sleep(5) 

finally:
    driver.quit()
