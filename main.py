import streamlit as st
import pandas as pd
import requests
import io
import time
from pathlib import Path
import json
from APIs.unicef import african_countries
from APIs.clean import filter_african_countries, main as clean_main
from APIs.unations import fetch_data
from APIs.unicef_big_data import base_url as unicef_base_url


st.set_page_config(page_title="Africa Data Scraper", page_icon="🌍", layout="wide")

def create_download_folder():
    Path("downloads").mkdir(exist_ok=True)

def fetch_unicef_data(dataset_name):
    """Fetch data from UNICEF API for a specific dataset"""
    target_url = f"UNICEF,{dataset_name},1.0/all?format=csv&labels=both"
    response = requests.get(unicef_base_url + target_url)
    
    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        return df
    return None

def main():
    st.title("🌍 Africa Data Scraper")
    st.markdown("""
    Extract and download data related to Africa from various sources including:
    - UNICEF
    - United Nations
    - World Bank
    - And more...
    """)

    # Create tabs for different data sources
    tab1, tab2, tab3 = st.tabs(["UNICEF Data", "UN Population Data", "Custom Data"])

    with tab1:
        st.header("UNICEF Data")
        
        unicef_datasets = [
            "PT", "CHILD_RELATED_SDG", "CME", "COVID", "EDUCATION", 
            "HIV_AIDS", "IMMUNISATION", "NUTRITION", "WASH_HOUSEHOLDS"
        ]
        
        selected_dataset = st.selectbox(
            "Select UNICEF Dataset",
            unicef_datasets
        )
        
        if st.button("Fetch UNICEF Data"):
            with st.spinner("Fetching data..."):
                df = fetch_unicef_data(selected_dataset)
                if df is not None:
                    # Filter for African countries
                    df_africa = df[df['Geographic area'].isin(african_countries)]
                    
                    # Show preview
                    st.dataframe(df_africa.head())
                    
                    # Save and provide download link
                    csv_path = f"downloads/unicef_{selected_dataset}.csv"
                    df_africa.to_csv(csv_path, index=False)
                    
                    with open(csv_path, 'rb') as f:
                        st.download_button(
                            label="Download CSV",
                            data=f,
                            file_name=f"unicef_{selected_dataset}.csv",
                            mime="text/csv"
                        )

    with tab2:
        st.header("UN Population Data")
        
        page_size = st.slider("Number of records per page", 50, 500, 100)
        max_pages = st.slider("Maximum number of pages to fetch", 1, 10, 3)
        
        if st.button("Fetch UN Population Data"):
            progress_bar = st.progress(0)
            all_data = []
            
            for page in range(1, max_pages + 1):
                progress_bar.progress(page / max_pages)
                page_data = fetch_data(page, page_size)
                
                if page_data is None or not page_data['data']:
                    break
                    
                all_data.extend(page_data['data'])
            
            if all_data:
                df = pd.json_normalize(all_data)
                st.dataframe(df.head())
                
                # Save and provide download link
                csv_path = "downloads/un_population_data.csv"
                df.to_csv(csv_path, index=False)
                
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        label="Download CSV",
                        data=f,
                        file_name="un_population_data.csv",
                        mime="text/csv"
                    )

    with tab3:
        st.header("Custom Data Upload & Processing")
        
        uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head())
            
            if st.button("Filter for African Countries"):
                filtered_df = df[df['Geographic area'].isin(african_countries)]
                st.write("Preview of filtered data:")
                st.dataframe(filtered_df.head())
                
                # Provide download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download Filtered Data",
                    data=csv,
                    file_name="filtered_africa_data.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    create_download_folder()
    main() 