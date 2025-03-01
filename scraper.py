from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Set up Selenium options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the target website
driver.get("https://chukul.com/floorsheet")
time.sleep(5)  # Wait for the page to load

# Open CSV file to store scraped data
with open("floorsheet_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Stock Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"])

    # Scrape data from the current page
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) == 6:  # Ensure correct number of columns
            writer.writerow([col.text.strip() for col in cols])

print("Scraping completed! Data saved to floorsheet_data.csv")

# Close the WebDriver
driver.quit()
