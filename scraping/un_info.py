import csv
from datetime import datetime
import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_documents():
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
    base_url = "https://uninfo.org/documents"
    driver.get(base_url)
    
    logger.info("Please select the desired filters and set pagination to 100 records per page. Press Enter when done.")
    input("Press Enter to continue after completing manual input...")
    
    results = []

    while True:
        logger.info("Scraping current page")

        # Wait for the table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div/div/div[5]/div/div/table'))
        )
        
        # Find all rows in the table
        rows = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div/div/div[5]/div/div/table/tbody/tr')
        
        for row in rows:
            try:
                # Extract data from each cell in the row
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) < 5:  # Ensure there are enough cells in the row
                    continue
                
                data = {
                    'Country': cells[0].text,
                    'Data_Name': cells[1].text,
                    'Data_Description': cells[2].text,
                    'Data_Link': cells[4].text,
                    'link': cells[4].find_element(By.TAG_NAME, 'a').get_attribute('href')
                }
                
                results.append(data)
                logger.info(f"Scraped row data: {data}")
            except Exception as e:
                logger.error(f"Error extracting data from row: {e}")
                continue
        
        # Try to go to next page
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div/div/div[5]/div/div/div/div/div[3]/button[2]'))
            )
            next_button.click()
        except (NoSuchElementException, TimeoutException):
            logger.info("No more pages to scrape or error navigating to next page")
            break
    
    driver.quit()
    return results

def save_to_csv(data: List[dict], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=['Country', 'Data_Name', 'Data_Description', 'Data_Link', 'link'])
        writer.writeheader()
        for item in data:
            writer.writerow(item)
    logger.info(f"Data saved to {filename}")

# Run the scraper
logger.info("Starting the scraping process")
data = scrape_documents()

# Generate a filename with current date and time
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"un_info_{current_time}.csv"

# Save the data to CSV
save_to_csv(data, filename)

logger.info(f"Scraping completed. Total items scraped: {len(data)}")
