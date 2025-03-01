from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Set up Chrome options for headless scraping (needed for GitHub Actions)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

# Initialize the WebDriver (automatically installs the correct driver)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the webpage to scrape
url = "https://chukul.com/floorsheet"
driver.get(url)

try:
    # Initialize an empty list to hold all the data
    all_data = []

    def scrape_current_page():
        """Scrapes the table data from the current page."""
        print("Scraping current page...")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Locate the table element
        table = soup.find("div", {
            "class": "q-table__container q-table--cell-separator column no-wrap q-table__card q-table--flat q-table--bordered q-table--no-wrap table-sticky-header-column"
        })

        if not table:
            print("No table found on the current page.")
            return []

        # Extract table rows
        rows = table.find_all("tr")
        page_data = []
        for row in rows:
            cols = row.find_all("td")
            cols_data = [col.text.strip() for col in cols]  # Extract text from each column
            if cols_data:
                page_data.append(cols_data)

        return page_data

    # Scrape all pages
    current_page = 1
    while True:
        print(f"Scraping page {current_page}...")
        page_data = scrape_current_page()
        all_data.extend(page_data)

        # Check for next page button
        pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "div.q-pagination__middle button")
        next_page_button = None
        for button in pagination_buttons:
            if button.get_attribute("aria-label") == str(current_page + 1):  # Find the button for the next page
                next_page_button = button
                break

        if next_page_button:
            next_page_button.click()
            current_page += 1
            time.sleep(3)  # Wait for the next page to load
        else:
            print("No next page button found. Assuming this is the last page.")
            break

    # Create a DataFrame from all the data collected
    df = pd.DataFrame(all_data)

    # Define the header names
    header = ["Transact No.", "Symbol", "Buyer", "Seller", "Quantity", "Rate", "Amount"]

    # Adjust headers if necessary
    if df.shape[1] == len(header):  # If column count matches, set the header
        df.columns = header
    else:
        raise ValueError(f"Column count mismatch. DataFrame has {df.shape[1]} columns, but {len(header)} headers provided.")

    # Convert columns to numeric where applicable
    def parse_numeric(value):
        try:
            return float(value.replace(",", "")) if value else None
        except ValueError:
            return None

    for col in ["Quantity", "Rate", "Amount"]:
        if col in df.columns:
            df[col] = df[col].apply(parse_numeric)

    # Drop NaN values and sum the total amount
    df = df.dropna(subset=["Amount"])
    total_amount = df["Amount"].sum()
    print(f"Total rows after cleaning: {len(df)}")
    print(f"Total Amount: {total_amount:,.2f}")

    # Save to CSV instead of Excel (easier for GitHub Actions)
    output_file = "scraped_data_final.csv"
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

finally:
    driver.quit()
