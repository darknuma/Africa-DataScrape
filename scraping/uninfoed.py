import csv
import time
from datetime import datetime
import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def setup_filters_and_pagination(driver):
    base_url = "https://uninfo.org/documents"
    driver.get(base_url)
    
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'normal'  # 'normal', 'eager', 'none'
    driver = webdriver.Chrome(options=options)

    time.sleep(5)

    driver.save_screenshot('before_wait.png')

    try:
        africa_filter = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div/div/div[2]/div[1]/div/div/div/div[1]/span'))
        )
        if africa_filter.text != "Africa":
            logger.error("Filter 'Africa' is not selected. Exiting.")
            driver.quit()
            exit(1)
    except NoSuchElementException:
        logger.error("Unable to find the 'Africa' filter.")
        driver.quit()
        exit(1)

    categories = {
        "Cooperation Framework": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[1]/span',
        "Country plans for MCO settings": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[2]/span',
        "Management response for UNDAF/Cooperation Framework Evaluation": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[3]/span',
        "UN Country Results Report": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[4]/span',
        "UNDAF/Cooperation Framework Evaluation": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[5]/span',
        "Regional CF": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[6]/span',
        "Multiyear funding framework": '//*[@id="app"]/div[1]/div/div/div[3]/div/div/div/div[7]/span'
    }

    for category, xpath in categories.items():
        try:
            category_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if category_element.text != category:
                logger.error(f"Expected category '{category}' not found. Exiting.")
                driver.quit()
                exit(1)
        except NoSuchElementException:
            logger.error(f"Category '{category}' not found.")
            driver.quit()
            exit(1)

    # Set pagination to 100 records per page
    try:
        pagination_select = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="P0-31"]'))
        )
        pagination_select.click()
        
        # Select the 100 records per page option
        option_100 = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="listbox"]//li[text()="100"]'))
        )
        option_100.click()
    except NoSuchElementException:
        logger.error("Unable to set pagination to 100 records per page.")
        driver.quit()
        exit(1)

def scrape_documents():
    driver = webdriver.Chrome()  
    setup_filters_and_pagination(driver)
    
    results = []
    
    while True:
        logger.info("Scraping current page")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div/div/div[5]/div/div/table'))
        )
        
        rows = driver.find_elements(By.XPATH, '//*[@id="app"]/div[1]/div/div/div[5]/div/div/table/tbody/tr')
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) < 5:
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

logger.info("Starting the scraping process")
data = scrape_documents()

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"un_documents_{current_time}.csv"

save_to_csv(data, filename)

logger.info(f"Scraping completed. Total items scraped: {len(data)}")
