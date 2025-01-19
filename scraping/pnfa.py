import csv
import time
import logging
from pydantic import BaseModel, validator, ValidationError
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapedData(BaseModel):
    data_name: str
    data_link: str
    source: str
    domain: str

    @validator('data_link')
    def validate_link(cls, value):
        if not value.startswith("http"):
            raise ValueError("Invalid URL")
        return value

def scrape_data(driver) -> List[ScrapedData]:
    data_list = []

    for i in range(1, 21):  # Adjust range according to the number of entries you expect 
        data_name_xpath = f'#layout_221_block_2 > div > div > div > div > div.row-layout.app-root-emotion-cache-ltr-h5s9fd > div > div > div > div > div > div > div > div.widget-list.d-flex > div > div > div.widget-list-list > div > div:nth-child({i}) > li > div > div > div > div > div > div.d-flex.layout-item.is-widget.app-root-emotion-cache-ltr-1oshtin > div > div > div > div > div > div > div > p > span'
        data_link_xpath = f'//*[@id="layout_221_block_2"]/div/div/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[{i}]/li/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/p/a'
        data_source_xpath = f'//*[@id="layout_221_block_2"]/div/div/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[{i}]/li/div/div/div/div/div/div[3]/div/div/div/div/div/div/div/h5/span[2]'
        data_domain_xpath = f'//*[@id="layout_221_block_2"]/div/div/div/div/div[1]/div/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div[{i}]/li/div/div/div/div/div/div[4]/div/div/div/div/div/div/div/p/span'
        
        try:
            data_name = driver.find_element(By.CSS_SELECTOR, data_name_xpath).text
            data_link = driver.find_element(By.XPATH, data_link_xpath).get_attribute('href')
            data_source = driver.find_element(By.XPATH, data_source_xpath).text
            data_domain = driver.find_element(By.XPATH, data_domain_xpath).text

            scraped_data = ScrapedData(
                data_name=data_name,
                data_link=data_link,
                source=data_source,
                domain=data_domain
            )
            data_list.append(scraped_data)
            logger.info(f"Successfully scraped data: {scraped_data}")

        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
        except Exception as e:
            logger.error(f"Error while scraping data entry {i}: {e}")
            continue

    return data_list

def save_to_csv(data: List[ScrapedData], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=['data_name', 'data_link', 'source', 'domain'])
        writer.writeheader()
        for item in data:
            writer.writerow(item.dict())
    logger.info(f"Data saved to {filename}")

if __name__ == "__main__":
    logger.info("Starting the scraping process")
    driver = webdriver.Chrome()
    driver.get('https://pdp.unfpa.org/?data_id=dataSource_8-3%3A6%2B7%2B8%2CdataSource_8-2%3A7%2B6%2B1%2B4%2B5%2B2%2B3%2B8%2B32%2B31%2B26%2B28%2CdataSource_8-0%3A386&page=Data')
    input("Press Enter to start scraping...")
    all_data = []

    while True:
        data_on_page = scrape_data(driver)
        all_data.extend(data_on_page)
        input("Press Enter after clicking the 'Next' button to continue scraping the next page, or type 'q' to quit: ")

        if input().lower() == 'q':
            break

    driver.quit()

    current_time = time.strftime("%Y%m%d_%H%M%S")
    filename = f"population_data_portal_{current_time}.csv"
    save_to_csv(all_data, filename)

    logger.info(f"Scraping completed. Total items scraped: {len(all_data)}")
