import pandas as pd
import requests
import json

# Declares the base url for calling the API
base_url = "https://population.un.org/dataportalapi/api/v1"

# Creates the target URL, indicators, in this instance
target = base_url + "/indicators/"

# Get the response, which includes the first page of data as well as information on pagination and number of records
response = requests.get(target)

# Converts call into JSON
j = response.json()

# Converts JSON into a pandas DataFrame.
df = pd.json_normalize(j['data']) # pd.json_normalize flattens the JSON to accomodate nested lists within the JSON structure

# Loop until there are new pages with data
while j['nextPage'] != None:
    # Reset the target to the next page
    target = j['nextPage']

    #call the API for the next page
    response = requests.get(target)

    # Convert response to JSON format
    j = response.json()

    # Store the next page in a data frame
    df_temp = pd.json_normalize(j['data'])

    # Append next page to the data frame
    df = df.append(df_temp)
