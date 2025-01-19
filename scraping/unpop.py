import pandas as pd
import requests
import json


base_url = "https://population.un.org/dataportalapi/api/v1"
target = base_url + "/indicators/"

response = requests.get(target)

j = response.json()

df = pd.json_normalize(j['data']) 

while j['nextPage'] != None:
    target = j['nextPage']

    response = requests.get(target)
    j = response.json()
    df_temp = pd.json_normalize(j['data'])
    df = df.append(df_temp)
