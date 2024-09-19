import requests
import pandas as pd
import io
import time

base_url = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/"

target_url_list = [
                "UNICEF,PT,1.0/all?format=csv&labels=both",
                "UNICEF,CHILD_RELATED_SDG,1.0/all?format=csv&labels=both",
                "UNICEF,CME,1.0/all?format=csv&labels=both",
                "UNICEF,CME_CAUSE_OF_DEATH,1.0/all?format=csv&labels=both",
                "UNICEF,CME_COUNTRY_PROFILES_DATA,1.0/all?format=csv&labels=both",
                "UNICEF,COVID,1.0/all?format=csv&labels=both",
                "UNICEF,COVID_CASES,1.0/all?format=csv&labels=both",
                "UNICEF,DM,1.0/all?format=csv&labels=both",
                "UNICEF,DM_PROJECTIONS,1.0/all?format=csv&labels=both",
                "UNICEF,ECD,1.0/all?format=csv&labels=both",
                "UNICEF,ECONOMIC,1.0/all?format=csv&labels=both",
                "UNICEF,EDUCATION,1.0/all?format=csv&labels=both",
                "UNICEF,FUNCTIONAL_DIFF,1.0/all?format=csv&labels=both",
                "UNICEF,GENDER,1.0/all?format=csv&labels=both",
                "UNICEF,HIV_AIDS,1.0/all?format=csv&labels=both",
                "UNICEF,IMMUNISATION,1.0/all?format=csv&labels=both",
                "UNICEF,MG,1.0/all?format=csv&labels=both",
                "UNICEF,MNCH,1.0/all?format=csv&labels=both",
                "UNICEF,PT_CM,1.0/all?format=csv&labels=both",
                "UNICEF,PT_CONFLICT,1.0/all?format=csv&labels=both",
                "UNICEF,PT_FGM,1.0/all?format=csv&labels=both",
                "UNICEF,SDG_PROG_ASSESSMENT,1.0/all?format=csv&labels=both",
                "UNICEF,SOC_PROTECTION,1.0/all?format=csv&labels=both",
                "UNICEF,WASH_HEALTHCARE_FACILITY,1.0/all?format=csv&labels=both",
                "UNICEF,WASH_HOUSEHOLD_MH,1.0/all?format=csv&labels=both",
                "UNICEF,WASH_HOUSEHOLD_SUBNAT,1.0/all?format=csv&labels=both",
                "UNICEF,WASH_HOUSEHOLDS,1.0/all?format=csv&labels=both",
                "UNICEF,WASH_SCHOOLS,1.0/all?format=csv&labels=both",
                "UNICEF,WT,1.0/all?format=csv&labels=both"
                   ]

african_countries = [
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon',
    'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo',
    'Democratic Republic of the Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea',
    'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau',
    'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
    'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
    'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles',
    'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Swaziland',
    'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'
]

for target_url in target_url_list:
    file_name = target_url.split(',')[1].split('/')[0]
    print(f"Processing: {file_name}")
    
    response = requests.get(base_url + target_url)
    if response.status_code == 200:
        print("Request successful")
        
        df = pd.read_csv(io.StringIO(response.text))
        
    
        if 'Geographic area' in df.columns:
            column_name = 'Geographic area'
        elif 'Country' in df.columns:
            column_name = 'Country'
        else:
            print(f"Warning: Neither 'Geographic area' nor 'Country' column found in {file_name}")
            continue
        
        df_africa = df[df[column_name].isin(african_countries)]
        
        print(f"Number of rows for African countries: {len(df_africa)}")
        
        output_file = f"unicef_{file_name}.csv"
        df_africa.to_csv(output_file, index=False)
        print(f"Saved {output_file} successfully")
        
    else:
        print(f"Request failed with status code: {response.status_code}")
    time.sleep(1)

print("All processing completed.")