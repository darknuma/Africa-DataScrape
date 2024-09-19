import requests
import json
import os
import pandas as pd
from tqdm import tqdm

base_path = 'https://population.un.org/dataportalapi/api/v1/'
relative_path = "indicators"

def fetch_data(page, page_size=100):
    params = {
        'pageNumber': page,
        'pageSize': page_size
    }
    response = requests.get(base_path + relative_path, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching page {page}: Status code {response.status_code}")
        return None

os.makedirs('output', exist_ok=True)

all_data = []
max_pages = 100

for page in tqdm(range(1, max_pages + 1), desc="Fetching pages"):
    page_data = fetch_data(page)
    if page_data is None or not page_data['data']:
        break
    all_data.extend(page_data['data'])
    
    if page_data['nextPage'] is None:
        print(f"Reached last page at {page}")
        break


with open('output/un_population_data_all.json', 'w') as f:
    json.dump(all_data, f, indent=4)

print("Complete JSON data saved to output/un_population_data_all.json")


df = pd.json_normalize(all_data)

csv_file_path = 'output/un_population_data_all.csv'
df.to_csv(csv_file_path, index=False)

print(f"Complete CSV data saved to {csv_file_path}")

print(f"Total records fetched: {len(all_data)}")