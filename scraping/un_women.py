from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd


driver = webdriver.Chrome() 
driver.get("https://data.unwomen.org/countries")


country_data = []

for i in range(1, 61):
    try:
        country_xpath = f'//*[@id="block-unwomen-content"]/div[2]/div/div[1]/div/div[{i}]/a'
        country_element = driver.find_element(By.XPATH, country_xpath)
        
        country_name = country_element.text
        country_link = country_element.get_attribute('href')
        
        
        country_data.append({"Country Name": country_name, "Country Link": country_link})
    
    except Exception as e:
        print(f"Could not retrieve data for div[{i}]: {e}")

driver.quit()

df = pd.DataFrame(country_data)


save_file = f"un_women_country_profiles.csv"
df.to_csv(save_file, index=False)

print(f"{save_file} is saved successfully")
