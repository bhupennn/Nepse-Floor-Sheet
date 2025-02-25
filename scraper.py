import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options for headless scraping
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL
url = "https://chukul.com/floorsheet"
driver.get(url)
time.sleep(3)  # Allow time for the page to load

# Extract total pages from pagination
pagination = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li")
total_pages = int(pagination[-2].text)  # Get the second last item as total pages

# Store data
all_data = []

# Loop through all pages
for page in range(1, total_pages + 1):
    print(f"Scraping Page {page}/{total_pages}")
    
    # Find table rows
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
    
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) == 7:  # Ensure correct column count
            transaction, symbol, buyer, seller, quantity, rate, amount = [col.text.strip() for col in cols]
            all_data.append([transaction, symbol, buyer, seller, quantity, rate, amount])
    
    # Go to the next page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "ul.pagination li a[rel='next']")
        next_button.click()
        time.sleep(3)
    except:
        break  # Stop if there is no next button

# Close the driver
driver.quit()

# Convert to DataFrame
df = pd.DataFrame(all_data, columns=["Transaction", "Stock Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"])

# Save to CSV
csv_filename = "floorsheet_data.csv"
df.to_csv(csv_filename, index=False)
print(f"Data saved to {csv_filename}")
