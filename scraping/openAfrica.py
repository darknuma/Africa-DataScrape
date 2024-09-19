import csv
import time
import logging
from pydantic import BaseModel, ValidationError
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the Pydantic model for data validation
class ScrapedData(BaseModel):
    data_name: str
    data_link: str
    data_source: str
    data_source_link: str
    data_description: str
    dataset_date_sourced: str
    data_file: str

# Function to scrape the data from a single page
def scrape_page_data(driver) -> List[ScrapedData]:
    data_list = []

    for i in range(1, 6):  # Adjust range according to the number of entries per page
        try:
            # XPath patterns
            data_name_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[1]/h5/a'
            # //*[@id="primary-datasetId"]/div/ul/li[2]/div/div[1]/h5/a
            # //*[@id="primary-datasetId"]/div/ul/li[3]/div/div[1]/h5/a
            data_link_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[1]/h5/a'
            data_source_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[1]/h5/div[2]/a'
            data_source_link_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[1]/h5/div[2]/a'
            data_description_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[2]/div[1]/p'
            dataset_date_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[1]/h5/div[1]'
            data_file_xpath = f'//*[@id="primary-datasetId"]/div/ul/li[{i}]/div/div[2]/div[2]/ul/li/a'

            # Extract the data
            data_name = driver.find_element(By.XPATH, data_name_xpath).text
            data_link = driver.find_element(By.XPATH, data_link_xpath).get_attribute('href')
            data_source = driver.find_element(By.XPATH, data_source_xpath).text
            data_source_link = driver.find_element(By.XPATH, data_source_link_xpath).get_attribute('href')
            data_description = driver.find_element(By.XPATH, data_description_xpath).text
            dataset_date_sourced = driver.find_element(By.XPATH, dataset_date_xpath).text
            data_file = driver.find_element(By.XPATH, data_file_xpath).get_attribute('href')

            # Validate and store the data
            scraped_data = ScrapedData(
                data_name=data_name,
                data_link=data_link,
                data_source=data_source,
                data_source_link=data_source_link,
                data_description=data_description,
                dataset_date_sourced=dataset_date_sourced,
                data_file=data_file
            )
            data_list.append(scraped_data)
            logger.info(f"Scraped data: {scraped_data}")

        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
        except Exception as e:
            logger.error(f"Error while scraping data entry {i}: {e}")
            continue

    return data_list

# Function to click the next page button
def click_next_page(driver):
    try:
        next_page_xpath = '//*[@id="primary-datasetId"]/div/div/ul/li[2]/a'  # Adjust if necessary
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, next_page_xpath))
        )
        next_button.click()
        time.sleep(3)  # Wait for the next page to load
        logger.info("Navigated to the next page")
    except Exception as e:
        logger.error("Error clicking next page:", e)

# Function to save data to CSV
def save_to_csv(data: List[ScrapedData], filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=[
            'data_name', 'data_link', 'data_source', 'data_source_link',
            'data_description', 'dataset_date_sourced', 'data_file'
        ])
        writer.writeheader()
        for item in data:
            writer.writerow(item.dict())
    logger.info(f"Data saved to {filename}")

# Main script
if __name__ == "__main__":
    logger.info("Starting the scraping process")
    
    driver = webdriver.Chrome()
    driver.get('https://open.africa/dataset?q=&sort=score+desc%2C+metadata_modified+desc')

    # Wait for user confirmation to start scraping
    input("Press Enter to start scraping...")

    all_data = []

    for _ in range(5):  # Adjust the range for the number of pages
        data_on_page = scrape_page_data(driver)
        all_data.extend(data_on_page)
        click_next_page(driver)

    driver.quit()

    # Save the scraped data to a CSV file
    current_time = time.strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_open_africa_{current_time}.csv"
    save_to_csv(all_data, filename)

    logger.info(f"Scraping completed. Total items scraped: {len(all_data)}")
