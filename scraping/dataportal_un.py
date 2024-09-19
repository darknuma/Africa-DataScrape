import pandas as pd 
import csv
import requests 


# url = '/api/v1/data/indicators/{indicators}/locations/{locations}'

# relative_path = 

# Define a function that will take a relative path as an input, call the API, and return a dataframe
def callAPI(relative_path:str, topic_list:bool = False) -> pd.DataFrame:
    base_url = "https://population.un.org/dataportalapi/api/v1" 
    target = base_url + relative_path # Query string parameters may be appended here or directly in the provided relative path
    # Calls the API
    response = requests.get(target)
    # Reformats response into a JSON object
    j = response.json()
    # The block below will deal with paginated results.
    # If results not paginated, this will be skipped.
    try:
        # If results are paginated, they are transformed into a python dictionary.
        # The data may be accessed using the 'data' key of the dictionary.
        df = pd.json_normalize(j['data'])
        # As long as the nextPage key of the dictionary contains an address for the next API call, the function will continue to call the API and append the results to the dataframe.
        while j['nextPage'] is not None:
            response = requests.get(j['nextPage'])
            j = response.json()
            df_temp = pd.json_normalize(j['data'])
            df = df.append(df_temp)
    except:
        if topic_list:
            df = pd.json_normalize(j, 'indicators')
        else:
            df = pd.DataFrame(j)
    return(df)

# Uses callAPI function to get a list of locations
df_locations = callAPI("/locations/")
df_normalized = pd.json_normalize(df_locations['data']) 
df_locations = pd.concat([df_locations, df_normalized], axis=1)

# Identifies ID code for Western Africa
western_africa_id = df_locations.loc[df_locations["name"]=="Western Africa", "id"].iloc[0]

# Restricts the dataframe to only include geographies from Western Africa
df_locations = df_locations[df_locations['parentId']==western_africa_id]

# Stores country codes in a list
country_codes = [str(code) for code in df_locations["id"].values]

# Converts country code list into a string to be used in later API call
country_selection_string = ",".join(country_codes)

# Uses callAPI function to get a list of Family Planning indicators
df_topics = callAPI("/topics/FP/indicators", topic_list=True)

# Stores indicator codes in a list
indicator_codes = [str(code) for code in df_topics["id"].values]

# Converts indicator code list into string to be used in later API call
indicator_selection_string = ",".join(indicator_codes)

# Calls the API to return the indicator values for the selected indicators and countries.
df = callAPI(f"/data/indicators/{indicator_selection_string}/locations/{country_selection_string}/start/2000/end/2023")

# Finally, filters the returned results to only include median values for All Women, and limits the number of columns retained in the new dataframe.
df2 = df.loc[(df['variant']=="Median") & (df['category']=="All women"), ['location', "indicator", "variant","category","value"]]


# Save the DataFrame to a CSV file
df2.to_csv('output.csv', index=False)




