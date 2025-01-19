import streamlit as st
import pandas as pd
import requests
import io
import time
from pathlib import Path
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from APIs.unicef import african_countries
from APIs.unicef_big_data import base_url as unicef_base_url
from scraping.openAfrica2 import scrape_page_data as scrape_open_africa
from scraping.nbs import scrape_page_data as scrape_nbs
from scraping.pnfa import scrape_data as scrape_pnfa
from scraping.un_women import country_data as scrape_un_women
from scraping.un_info import scrape_documents as scrape_un_info
from scraping.databank_worldbank import scrape_page_data as scrape_worldbank
from scraping.uninfoed import scrape_documents as scrape_uninfo_ed
from scraping.africaed import scrape_un_data
from scraping.unpop import base_url as unpop_base_url

st.set_page_config(page_title="Africa Data Scraper", page_icon="🌍", layout="wide")

def create_download_folder():
    Path("downloads").mkdir(exist_ok=True)

def setup_selenium_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    return webdriver.Chrome(options=options)

def main():
    st.title("🌍 Africa Data Scraper")
    st.markdown("""
    Extract and download data related to Africa from various sources including:
    - Open Africa
    - Nigerian Bureau of Statistics
    - UN Women
    - World Bank
    - UN Population
    - And more...
    """)

    # Create tabs for different data sources
    tabs = st.tabs([
        "Open Africa", 
        "NBS", 
        "UN Women", 
        "UN Info",
        "World Bank",
        "UN Population",
        "UN Education",
        "Custom Data"
    ])

    with tabs[0]:  # Open Africa
        st.header("Open Africa Data")
        if st.button("Scrape Open Africa Data"):
            with st.spinner("Scraping data from Open Africa..."):
                driver = setup_selenium_driver()
                data = scrape_open_africa(driver)
                driver.quit()
                
                if data:
                    df = pd.DataFrame([item.dict() for item in data])
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download Open Africa Data",
                        csv,
                        f"open_africa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[1]:  # NBS
        st.header("Nigerian Bureau of Statistics")
        if st.button("Scrape NBS Data"):
            with st.spinner("Scraping data from NBS..."):
                driver = setup_selenium_driver()
                data = scrape_nbs(driver)
                driver.quit()
                
                if data:
                    df = pd.DataFrame([item.dict() for item in data])
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download NBS Data",
                        csv,
                        f"nbs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[2]:  # UN Women
        st.header("UN Women Data")
        if st.button("Scrape UN Women Data"):
            with st.spinner("Scraping data from UN Women..."):
                driver = setup_selenium_driver()
                data = scrape_un_women(driver)
                driver.quit()
                
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download UN Women Data",
                        csv,
                        f"un_women_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[3]:  # UN Info
        st.header("UN Info Documents")
        if st.button("Scrape UN Info Data"):
            with st.spinner("Scraping data from UN Info..."):
                data = scrape_un_info()
                
                if data:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download UN Info Data",
                        csv,
                        f"un_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[4]:  # World Bank
        st.header("World Bank Data")
        if st.button("Scrape World Bank Data"):
            with st.spinner("Scraping data from World Bank..."):
                driver = setup_selenium_driver()
                data = scrape_worldbank(driver)
                driver.quit()
                
                if data:
                    df = pd.DataFrame([item.dict() for item in data])
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download World Bank Data",
                        csv,
                        f"worldbank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[5]:  # UN Population
        st.header("UN Population Data")
        if st.button("Fetch UN Population Data"):
            with st.spinner("Fetching UN Population data..."):
                response = requests.get(unpop_base_url + "/indicators/")
                if response.status_code == 200:
                    data = response.json()
                    df = pd.json_normalize(data['data'])
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download UN Population Data",
                        csv,
                        f"un_population_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[6]:  # UN Education
        st.header("UN Education Data")
        if st.button("Scrape UN Education Data"):
            with st.spinner("Scraping UN Education data..."):
                data = scrape_un_data()
                
                if data:
                    df = pd.DataFrame([item.dict() for item in data])
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download UN Education Data",
                        csv,
                        f"un_education_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv"
                    )

    with tabs[7]:  # Custom Data
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
                
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "Download Filtered Data",
                    csv,
                    f"filtered_africa_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )

if __name__ == "__main__":
    create_download_folder()
    main()