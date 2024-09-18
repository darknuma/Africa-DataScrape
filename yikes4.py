import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    
    service = Service('C:/Users/A/Desktop/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_and_parse_data(driver, url):
    extracted_data = []

    try:
        logger.info(f"Connecting to {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='ygtvc']")))
            logger.info("Table loaded successfully.")
        except TimeoutException:
            logger.error("Timeout while waiting for the table to load.")
            return []

        count = 3
        base_id = 2880
        
        while True:
            try:
                some_id = base_id + 100 * (count - 3)
                mart_name_selector = f'#ygtvlabelel{count} > span.martName'
                
                logger.debug(f"Looking for mart with selector: {mart_name_selector}")
                try:
                    mart_name_span = driver.find_element(By.CSS_SELECTOR, mart_name_selector)
                    mart_name = mart_name_span.text
                except NoSuchElementException:
                    logger.info(f"Mart with selector {mart_name_selector} not found.")
                    break

                logger.info(f"Mart found: {mart_name}")

                # parent_div_selector = f"div[id^='ygtvc{count}']"
                parent_div_selector = f".//*[@class='ygtvchildren']"
              
                try:
                    # parent_div = driver.find_element(By.CSS_SELECTOR, parent_div_selector)
                    parent_div = driver.find_element(By.XPATH, parent_div_selector)
                except NoSuchElementException:
                    logger.warning(f"Parent div with selector {parent_div_selector} not found.")
                    break
                
                # data_rows_css = parent_div.find_elements(By.CSS_SELECTOR, f"div[id^='ygt']") //*[@cass="ygtvlabel"]/span[2]/a
                # data_rows_xpath = parent_div.find_elements(By.XPATH, ".//div[starts-with(@id, 'ygtvitem')]")
                data_rows_xpath = parent_div.find_elements(By.XPATH, ".//*[@class='ygtvitem']")
                # //*[@id="ygtv11"]

                if not data_rows_xpath:
                    logger.info(f"No data rows found for mart: {mart_name} with count: {count}")
                
                for data_row in data_rows_xpath:
                    try:
                        row_id = data_row.get_attribute('id')
                        table_id = row_id.replace('ygtv', 'ygtvtableel')
                        
                        try:
                            data_table = data_row.find_element(By.ID, table_id)
                            rows = data_table.find_elements(By.CSS_SELECTOR, "tr.ygtvrow")
                            
                            for row in rows:
                                try:
                                    # data_title_span = row.find_element(By.CSS_SELECTOR, f"span.node")
                                    data = row.find_elements(By.XPATH, f".//*[@class='ygtvcell  ygtvcontent']")
                            
                                    
                                except NoSuchElementException:
                                    logger.warning("Data row not found.")
                                    continue
                                for row_id in data:
                                    try:
                                        data_title_span = row_id.find_element(By.XPATH, f".//*[@class='ygtvlabel']/span[1]")
                                        data_title = data_title_span.text
                                        # link_element = row.find_element(By.CSS_SELECTOR, "span.view > a")
                                        link_element = row_id.find_element(By.XPATH, f".//*[@class='ygtvlabel']/span[2]/a")
                                        link_url = link_element.get_attribute('href')

                                        if data_title:
                                            extracted_data.append({
                                                'Mart Name': mart_name,
                                                'Data Title': data_title,
                                                'Data Link': link_url,
                                            })
                                            logger.info(f"Extracted data - Mart: {mart_name}, Title: {data_title}, Link: {link_url}")
                                    except NoSuchElementException:
                                        logger.warning("Data title or link not found in row.")
                                        continue
                        except NoSuchElementException:
                            logger.warning(f"Data table with ID {table_id} not found in div {row_id}.")
                            continue

                    except NoSuchElementException:
                        logger.warning("Data row div not found or not in expected structure.")
                        continue

                count += 1

            except NoSuchElementException:
                logger.info("No more marts found with the current ID pattern.")
                break

        if not extracted_data:
            logger.info("No data extracted. Please check the log for more details.")
        return extracted_data

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []

def save_to_csv(data, filename):
    if not data:
        logger.warning("No data to save to CSV.")
        return

    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    logger.info(f"Data saved to {filename}")

if __name__ == "__main__":
    url = "http://data.un.org/Explorer.aspx?d=16&f=docID:337"
    driver = setup_driver()

    try:
        extracted_data = fetch_and_parse_data(driver, url)
        save_to_csv(extracted_data, 'extracted_data.csv')
    finally:
        driver.quit()
