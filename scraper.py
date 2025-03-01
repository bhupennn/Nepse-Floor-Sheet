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

# Try to locate pagination elements
pagination = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a")

# Debug: Print pagination elements found
print("Pagination elements found:", [p.text for p in pagination])

# Determine the total number of pages
if len(pagination) < 2:
    print("Error: Pagination elements not found or insufficient!")
    total_pages = 1  # Set a default value
else:
    try:
        total_pages = int(pagination[-2].text)
    except ValueError:
        print("Error: Unable to extract total pages. Setting to 1.")
        total_pages = 1

print(f"Total pages detected: {total_pages}")

# Open CSV file to store scraped data
with open("floorsheet_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Stock Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"])

    # Loop through pages and scrape data
    for page in range(1, total_pages + 1):
        print(f"Scraping page {page}...")
        driver.get(f"https://chukul.com/floorsheet?page={page}")
        time.sleep(5)  # Allow page to load
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) == 6:  # Ensure correct number of columns
                writer.writerow([col.text.strip() for col in cols])

print("Scraping completed! Data saved to floorsheet_data.csv")

# Close the WebDriver
driver.quit()
