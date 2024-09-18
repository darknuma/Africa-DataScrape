import csv
from datetime import datetime
import logging
from typing import List
from urllib.parse import urljoin
from pydantic import BaseModel, AnyUrl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Pydantic model for data validation
class DataItem(BaseModel):
    data_name: str
    data_name_link: AnyUrl
    data_source: str
    data_source_link: str
    data_site: str
    data_site_link: str


def convert_to_absolute_url(base_url: str, relative_url: str) -> str:
    return urljoin(base_url, relative_url)


def scrape_un_data():
    driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
    base_url = "https://data.un.org/Search.aspx?q=africa&t=Data"
    driver.get(base_url)

    results = []
    page_number = 1

    while True:
        logger.info(f"Scraping page {page_number}")

        # Wait for the results to load //*[@id="ctl00_main_pnlResults"]/div[2]/div[4]/div[16]/div[1]/a //*[@id="ctl00_main_pnlResults"]/div[2]/div[4]/div[18]/div[1]/a
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="ctl00_main_pnlResults"]/div[2]/div[4]')
            )
        )

        # Find all div elements that contain data items
        elements = driver.find_elements(
            By.XPATH, '//*[@id="ctl00_main_pnlResults"]/div[2]/div[4]/div'
        )

        for index, element in enumerate(elements, start=1):
            try:
                # Use dynamic XPaths based on the current index
                data_name = element.find_element(By.XPATH, ".//h2/a")
                # Dynamically construct the XPath for data_source
                data_source_xpath = f'//*[@id="ctl00_main_pnlResults"]/div[2]/div[4]/div[{index}]/div[1]/a'
                try:
                    data_source = driver.find_element(By.XPATH, data_source_xpath)
                    data_source_text = data_source.text
                    data_source_href = data_source.get_attribute("href")
                    logger.debug(f"data_source_href: {data_source_href}")
                    data_source_link = (
                        convert_to_absolute_url(base_url, data_source_href)
                        if data_source_href
                        else "N/A"
                    )
                except NoSuchElementException:
                    data_source_text = "N/A"
                    data_source_link = "N/A"

                # Dynamically construct the XPath for data_site
                data_site_xpath = f'//*[@id="ctl00_main_pnlResults"]/div[2]/div[4]/div[{index}]/div[1]/span/a'
                try:
                    data_site = driver.find_element(By.XPATH, data_site_xpath)
                    data_site_text = data_site.text
                    data_site_href = data_site.get_attribute("href")
                    logger.debug(f"data_site_href: {data_site_href}")
                    data_site_link = (
                        convert_to_absolute_url(base_url, data_site_href)
                        if data_site_href
                        else "N/A"
                    )

                except NoSuchElementException:
                    data_site_text = "N/A"
                    data_site_link = "N/A"

                item = DataItem(
                    data_name=data_name.text,
                    data_name_link=convert_to_absolute_url(
                        base_url, data_name.get_attribute("href")
                    ),
                    data_source=data_source_text,
                    data_source_link=data_source_link,
                    data_site=data_site_text,
                    data_site_link=data_site_link,
                )
                results.append(item)
                logger.info(
                    f"Scraped item {index} on page {page_number}: {item.data_name}"
                )
            except NoSuchElementException:
                logger.warning(
                    f"Failed to scrape item {index} on page {page_number}, skipping"
                )
                continue
            except ValueError as e:
                logger.error(
                    f"Data validation error for item {index} on page {page_number}: {e}"
                )
                continue

        # Try to go to next page
        try:
            if page_number < 10:
                # For pages 1-9, use the numbered page links
                next_page_xpath = (
                    f'//*[@id="ctl00_main_results_rptNav_ctl{page_number:02d}_linkNav"]'
                )
            else:
                # For page 10 and beyond, use the "Next" button
                next_page_xpath = '//*[@id="ctl00_main_results_linkNext"]'

            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, next_page_xpath))
            )
            next_button.click()
            page_number += 1

            # Wait for the page to load after clicking
            WebDriverWait(driver, 10).until(EC.staleness_of(elements[0]))
        except (NoSuchElementException, TimeoutException):
            logger.info("No more pages to scrape")
            break

    driver.quit()
    return results


def save_to_csv(data: List[DataItem], filename: str):
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        # writer.writerow(['Data Name', 'Data Name Link', 'Data Source', 'Data Source Link', 'Data Site', 'Data Site Link'])
        writer.writerow(
            ["Data Name", "Data Name Link", "Data Source", "Data Source Link"]
        )
        for item in data:
            writer.writerow(
                [
                    item.data_name,
                    item.data_name_link,
                    item.data_source,
                    item.data_source_link,
                ]
            )
            # writer.writerow([item.data_name, item.data_name_link, item.data_source, item.data_source_link, item.data_site, item.data_site_link])
    logger.info(f"Data saved to {filename}")


# Run the scraper
logger.info("Starting the scraping process")
data = scrape_un_data()

# Generate a filename with current date and time
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"un_data_africa_{current_time}.csv"

# Save the data to CSV
save_to_csv(data, filename)

logger.info(f"Scraping completed. Total items scraped: {len(data)}")
