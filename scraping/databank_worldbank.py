import csv
import requests
import time
import logging
from pydantic import BaseModel, ValidationError
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapedData(BaseModel):
    database_name: str
    data_link: str
    data_description: str 
    last_updated: str 

def scrape_page_data(driver) -> List[ScrapedData]:
    data_list = []

    for i in range(1, 10):  # Adjust range according to the number of entries per page 
        try:
            database_name_xpath = f'//*[@id="DatabaseList"]/ul/li[{i}]/div/div/h4' 
            data_link_xpath = f'//*[@id="DatabaseList"]/ul/li[{i}]/div/div/h4/a'
            data_description_xpath = f'//*[@id="MainContent_grdDatabases_divDescription_{i}"]'
            last_updated_xpath = f'//*[@id="DatabaseList"]/ul/li[{i}]/div/div/div[3]/span/em'
            
            # Extract the data
            data_name = driver.find_element(By.XPATH, database_name_xpath).text 
            data_link = driver.find_element(By.XPATH, data_link_xpath).get_attribute('href')
            data_description = driver.find_element(By.XPATH, data_description_xpath).text
            last_updated = driver.find_element(By.XPATH, last_updated_xpath).text
           

            # Validate and store the data
            scraped_data = ScrapedData(
                database_name=data_name,
                data_link=data_link,
                data_description=data_description,
                last_updated=last_updated,
            )
            data_list.append(scraped_data)
            logger.info(f"Scraped data: {scraped_data}")

        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
        except Exception as e:
            logger.error(f"Error while scraping data entry {i}: {e}")
            continue

    return data_list


def go_to_next_page(driver, page_num: int):
    base_url = 'https://databank.worldbank.org/databases/page/'
    next_page_url = base_url + str(page_num)
    driver.get(next_page_url)
    time.sleep(4)
    logger.info(f"Navigated to page {page_num}")


def save_to_csv(data: List[ScrapedData], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=[
            'database_name', 'data_link', 'data_description', 'last_updated'
        ])
        writer.writeheader()
        for item in data:
            writer.writerow(item.dict())
    logger.info(f"Data saved to {filename}")


if __name__ == "__main__":

    logging.info("Starting the Scraping Process")
    driver = webdriver.Chrome()
    driver.get('https://databank.worldbank.org/databases/page/1')

    # Wait for user confirmation to start scraping
    input("Press Enter to start scraping...")

    all_data = []
    total_pages = 9 # Define the number of pages you want to scrape

    for page in range(1, total_pages + 1):  # Iterate through the pages
        data_on_page = scrape_page_data(driver)
        all_data.extend(data_on_page)
        go_to_next_page(driver, page + 1)

    driver.quit()

    # Save the scraped data to a CSV file
    current_time = time.strftime("%Y%m%d_%H%M%S")
    filename = f"data_bank_worldbank_{current_time}.csv"
    save_to_csv(all_data, filename)

    logger.info(f"Scraping completed. Total items scraped: {len(all_data)}")
