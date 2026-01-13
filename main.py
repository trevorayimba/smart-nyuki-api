import time
import requests
import streamlit as st
import pandas as pd

# Point to your API service (change if your API Render URL is different)
API_URL = "https://smart-nyuki-api.onrender.com"

st.set_page_config(page_title="SMART NYUKI", layout="wide")
st.title("🐝 SMART NYUKI - Live Dashboard")

# Fetch data from API
try:
    response = requests.get(f"{API_URL}/hives")  # Add this endpoint in API if needed
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
    else:
        df = pd.DataFrame()
except:
    df = pd.DataFrame()

if df.empty:
    st.info("Waiting for data from hives...")
else:
    for _, row in df.iterrows():
        hive_id = row['hive_id']
        weight = row['weight_kg']
        level = row['level']
        extracting = row['extracting']

        with st.container(border=True):
            st.subheader(f"Hive {hive_id}")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.metric("Weight", f"{weight:.2f} kg")
                st.progress(level / 100)
                st.caption(f"{level}% full")
            with col2:
                if level >= 50:
                    if st.button("HARVEST HONEY", key=f"btn_{hive_id}", type="primary"):
                        # Send harvest command to API
                        harvest_response = requests.post(f"{API_URL}/beehive/{hive_id}/harvest")
                        if harvest_response.status_code == 200:
                            st.success(f"Harvest command sent to Hive {hive_id}!")
                        else:
                            st.error("Failed to send harvest command")
                else:
                    st.button("Not Ready", disabled=True)

# Auto-refresh every 10 seconds
time.sleep(10)
st.rerun()
