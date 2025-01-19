import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb
import json
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

base_url = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/"
target_url_list = ["UNICEF,NUTRITION,1.0/all?format=csv&labels=both", 
                   "UNICEF,GLOBAL_DATAFLOW,1.0/all?format=csv&labels=both"
                  ]

#  "UNICEF,CME_DF_2021_WQ,1.0/all?format=csv&labels=both"
# def fetch_and_save_parquet(target_url):
#     file_name = target_url.split(',')[1].split('/')[0]
#     response = requests.get(base_url + target_url)
    
#     if response.status_code == 200:
#         # Convert CSV to DataFrame
#         df = pd.read_csv(io.StringIO(response.text))
        
#         # Convert DataFrame to PyArrow Table
#         table = pa.Table.from_pandas(df)
        
#         # Write to Parquet file
#         pq.write_table(table, f"unicef_{file_name}.parquet")
        
#         print(f"Saved {file_name} as Parquet")
#     else:
#         print(f"Request failed for {file_name}: {response.status_code}")


def fetch_and_save_parquet(target_url):
    file_name = target_url.split(',')[1].split('/')[0]
    response = requests.get(base_url + target_url)
    
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text), low_memory=False)
        
        # # Convert 'SERIES_YEAR' to string to avoid type conflicts
        # df['SERIES_YEAR'] = df['SERIES_YEAR'].astype(str)
        
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str)
        
        table = pa.Table.from_pandas(df)
        
        pq.write_table(table, f"unicef_{file_name}.parquet")
        
        print(f"Saved {file_name} as Parquet")
    else:
        print(f"Request failed for {file_name}: {response.status_code}")

def process_with_duckdb():
    con = duckdb.connect('unicef_data.db')
    
    for target_url in target_url_list:
        file_name = target_url.split(',')[1].split('/')[0]
        parquet_file = f"unicef_{file_name}.parquet"
        
        con.execute(f"CREATE OR REPLACE TABLE {file_name} AS SELECT * FROM parquet_scan('{parquet_file}')")
        
        con.execute(f"""
            CREATE OR REPLACE TABLE {file_name}_africa AS
            SELECT * FROM {file_name}
            WHERE "Geographic area" IN (
                'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
                'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo',
                'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea',
                'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau',
                'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
                'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
                'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles',
                'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland',
                'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
            )
        """)
        
        print(f"Processed {file_name}")

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(fetch_and_save_parquet, url) for url in target_url_list]
    for future in as_completed(futures):
        future.result()


process_with_duckdb()

print("All processing completed.")