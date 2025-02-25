from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

options = Options()
# options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.tge.pl/energia-elektryczna-rdn"

try:
    driver.get(url)
    time.sleep(3)  

    base_xpath = '//*[@id="footable_kontrakty_godzinowe"]/tbody/tr[{}]/td[2]'
    button_xpath = '/html/body/section[3]/div/div/div[1]/a[1]'


    days = 30
    for day in range(days):
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
        csv_file_path = os.path.join(output_folder, f"day_{day:02d}.csv")

        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Data"])
            for data in scraped_data:
                for i  in range(4):
                    writer.writerow([data])

        button = driver.find_element(By.XPATH, button_xpath)
        button.click()
        time.sleep(5)

finally:
    driver.quit()
