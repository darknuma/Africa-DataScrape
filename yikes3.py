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
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (without a GUI)
    options.add_argument("--disable-gpu")  # Disable GPU acceleration
    options.add_argument("--no-sandbox")  # Bypass OS security model

    # Initialize the WebDriver
    service = Service('C:/Users/A/Desktop/chromedriver.exe')  # Replace with your chromedriver path
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_and_parse_data(driver, url):
    extracted_data = []

    try:
        logger.info(f"Connecting to {url}")
        driver.get(url)

        # Wait for the table to load
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'ygtvtableel3')))
            logger.info("Table loaded successfully.")
        except TimeoutException:
            logger.error("Timeout while waiting for the table to load.")
            return []

        # Start counter for dynamic IDs
        count = 3  # Starting ID or count
        base_id = 2880  # Base ID for dynamic elements
        
        while True:
            try:
                # Calculate the dynamic ID //*[@id="ygtv144"]
                some_id = base_id + 100 * (count - 3)
                
                # Construct the selector for mart rows
                mart_name_selector = f'#ygtvlabelel{count} > span.martName'
                
                # Debugging: print the selector to verify
                print(f"Looking for mart with selector: {mart_name_selector}")
                
                mart_name_span = driver.find_element(By.CSS_SELECTOR, mart_name_selector)
                mart_name = mart_name_span.text if mart_name_span else None

                if mart_name:
                    logger.info(f"Mart found: {mart_name}")
                
                
                # Check for presence of the children div #ygtvc3
                parent_div_selector = f'#ygtvc{count}'
                parent_div = driver.find_element(By.CSS_SELECTOR, parent_div_selector)

                # Locate child elements within the parent div
                data_rows = parent_div.find_elements(By.CSS_SELECTOR, f'#ygtv{some_id}')

                # Print the outer HTML of each data row for debugging
                for index, data_row in enumerate(data_rows):
                    logger.info(f"Data row {index} HTML: {data_row.get_attribute('outerHTML')}")

                if not data_rows:
                    logger.info(f"No data rows found for mart: {mart_name} with count: {count}")
                
                for data_row in data_rows:
                    try:
                        # Extract data from the nested table within this div
                        row_id = data_row.get_attribute('id')  # 'ygtv144', 'ygtv145', etc.
                        table_id = row_id.replace('ygtv', 'ygtvtableel')  # 'ygtvtableel144', 'ygtvtableel145', etc.

                        try:
                            data_table = data_row.find_element(By.ID, table_id)
                            
                            # Find all rows within the nested table
                            rows = data_table.find_elements(By.CSS_SELECTOR, "tr.ygtvrow")
                            
                            for row in rows:
                                try:
                                    data_title_span = row.find_element(By.CSS_SELECTOR, f"#ygtvlabelel{some_id} > span.node")
                                    data_title = data_title_span.text if data_title_span else None

                                    if data_title:
                                        extracted_data.append({
                                            'Mart Name': mart_name,
                                            'Data Title': data_title,
                                        })
                                        logger.info(f"Extracted data - Mart: {mart_name}, Title: {data_title}")
                                except NoSuchElementException:
                                    logger.warning("Data title not found in row.")
                                    continue
                        except NoSuchElementException:
                            logger.warning(f"Data table with ID {table_id} not found in div {row_id}.")
                            continue

                    except NoSuchElementException:
                        logger.warning("Data row div not found or not in expected structure.")
                        continue

                # Increment the count to check the next dynamic ID
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
