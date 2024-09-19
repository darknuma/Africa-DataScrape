import pandas as pd


african_countries = [
    'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
    'Cabo Verde', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros',
    'Congo', 'Democratic Republic of the Congo', "Côte d'Ivoire", 'Djibouti',
    'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon',
    'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia',
    'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius',
    'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda',
    'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia',
    'South Africa', 'South Sudan', 'Sudan', 'Togo', 'Tunisia', 'Uganda',
    'United Republic of Tanzania', 'Zambia', 'Zimbabwe'
]

def filter_african_countries(csv_file):
    df = pd.read_csv(csv_file)
    
    df_filtered = df[df['Reference area'].isin(african_countries)]
    
    return df_filtered

def main(csv_file_path, output_file_path=None):
    filtered_df = filter_african_countries(csv_file_path)
    
    if output_file_path:
        filtered_df.to_csv(output_file_path, index=False)
    
    return filtered_df


csv_file = 'UNESCO UIS Education.csv '
output_file = 'unicef_UNESCO UIS Education.csv'

# Run the main function
filtered_african_df = main(csv_file, output_file)
print(filtered_african_df)
