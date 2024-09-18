import requests
import json
import csv

url_endpoint = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest"
dataflow_endpoint = "/dataflow/all/all/latest"
datadownload_endpoint = "/data/AgencyId,DataflowId,Version/All?format=sdmx-json"

dataflow_params = {
    "format": "sdmx-json",
    "detail": "full",
    "reference": "none",
}

# Get the response
dataflow_response = requests.get(url=url_endpoint + dataflow_endpoint, params=dataflow_params)
datadownload_response = requests.get(url=url_endpoint+datadownload_endpoint, params=dataflow_params)

# Check for successful response
if dataflow_response.status_code == 200:
    dataflows = datadownload_response.json()['data']['dataflows']
    
    # Writing to a JSON file
    with open('dataflows.json', 'w') as json_file:
        json.dump(dataflows, json_file, indent=4)

    # Writing to a CSV file
    with open('dataflows.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        
        # Write CSV header
        csv_writer.writerow(['ID', 'Name', 'Description'])  # Modify this based on your data structure
        
        # Writing data rows
        for dataflow in dataflows:
            # Adjust these fields based on the actual structure of your JSON response
            csv_writer.writerow([
                dataflow['id'], 
                dataflow['name'], 
                dataflow.get('description', 'N/A')
            ])
    
    print("Data saved successfully to dataflows.json and dataflows.csv")

else:
    print(f"Failed to retrieve data. Status code: {dataflow_response.status_code}")
