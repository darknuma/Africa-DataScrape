import csv
import time
import logging
from pydantic import BaseModel, ValidationError
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapedData(BaseModel):
    data_name: str
    data_link: str
    data_source: str 
    created_at: str
    last_updated: str 

def scrape_page_data(driver) -> List[ScrapedData]:
    data_list = []

    for i in range(3, 72):  # Adjust range according to the number of entries per page 
        try:
            catalog_name_xpath = f'//*[@id="surveys"]/div[{i}]/h2'   
            data_link_xpath = f'//*[@id="surveys"]/div[{i}]/h2/a'
            data_source_xpath = f'//*[@id="surveys"]/div[{i}]/div[3]/div' 
            created_at_xpath = f'//*[@id="surveys"]/div[{i}]/div[4]/span[1]'
            last_updated_xpath = f'//*[@id="surveys"]/div[{i}]/div[4]/span[2]'
            
            # Extract the data
            data_name = driver.find_element(By.XPATH, catalog_name_xpath).text 
            data_link = driver.find_element(By.XPATH, data_link_xpath).get_attribute('href')
            data_source = driver.find_element(By.XPATH, data_source_xpath).text
            created_at = driver.find_element(By.XPATH, created_at_xpath).text 
            last_updated = driver.find_element(By.XPATH, last_updated_xpath).text
           

            # Validate and store the data
            scraped_data = ScrapedData(
                data_name=data_name,
                data_link=data_link,
                data_source=data_source,
                created_at = created_at,
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


def save_to_csv(data: List[ScrapedData], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=[
            'data_name', 'data_link', 'data_source', 'created_at','last_updated'
        ])
        writer.writeheader()
        for item in data:
            writer.writerow(item.dict())
    logger.info(f"Data saved to {filename}")


if __name__ == "__main__":

    logging.info("Starting the Scraping Process")
    driver = webdriver.Chrome()
    driver.get('https://nigerianstat.gov.ng/nada/index.php/catalog#_r=&collection=&country=&dtype=&from=1999&page=1&ps=100&sk=&sort_by=titl&sort_order=&to=2023&topic=&view=s&vk=')

    input("Press Enter to start scraping...")

    all_data = []
    total_pages = 1 # Define the number of pages you want to scrape

    for page in range(1, total_pages + 1):  # Iterate through the pages
        data_on_page = scrape_page_data(driver)
        all_data.extend(data_on_page)
        # go_to_next_page(driver, page + 1)

    driver.quit()

    # Save the scraped data to a CSV file
    current_time = time.strftime("%Y%m%d_%H%M%S")
    filename = f"nigeria_bureau_statistics_{current_time}.csv"
    save_to_csv(all_data, filename)

    logger.info(f"Scraping completed. Total items scraped: {len(all_data)}")
