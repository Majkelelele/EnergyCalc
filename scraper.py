from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode if you don't need a UI
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())

# driver = webdriver.Chrome(service=service, options=chrome_options)
driver = webdriver.Chrome(service=service)

url = 'https://www.gkpge.pl/dla-domu/oferta/dynamiczna-energia-z-pge'
driver.get(url)

time.sleep(5)

try:
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cookieAccept"]'))).click()
    print("Cookies button clicked.")
except Exception as e:
    print(f"Error while clicking cookies button: {e}")

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="pane-table"]/div/div/ul')))

    list_items = driver.find_elements(By.XPATH, '//*[@id="pane-table"]/div/div/ul/li')
    print(f"Found {len(list_items)} list items.")
    
    time_price = []
    for li in list_items[1:]:
        date_time = li.find_element(By.XPATH, './/div[@class="date_time"]/div').text
        price = float(li.find_element(By.XPATH, './/div[@class="price"]/div').text)
        price_k = price / 1000
        time_price.append((date_time, price))



    data = pd.DataFrame(time_price, columns = ["time", "price"])
    data["price"].to_csv("prices.csv", index=False)
    
    data.sort_values(by="price", inplace=True)
    data.reset_index(drop=True, inplace=True)
    print(data)

except Exception as e:
    print(f"Error while extracting data from table: {e}")

time.sleep(3)

driver.quit()
