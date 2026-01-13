import time
import requests
import streamlit as st
import pandas as pd

# Your API service URL (change if different)
API_BASE = "https://smart-nyuki-api.onrender.com"

st.set_page_config(page_title="SMART NYUKI", layout="wide")
st.title("🐝 SMART NYUKI - Live Dashboard")

# Fetch all hives from the API service
try:
    response = requests.get(f"{API_BASE}/hives")
    if response.status_code == 200:
        hives_data = response.json()
        df = pd.DataFrame(hives_data)
    else:
        st.error(f"API error: {response.status_code} - {response.text}")
        df = pd.DataFrame()
except Exception as e:
    st.error(f"Failed to connect to API: {e}")
    df = pd.DataFrame()

if df.empty:
    st.info("Waiting for data from hives... (ESP32 should send data every 10s)")
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
                st.caption(f"{level}% full • Last update: {row.get('last_update', 'N/A')}")
            with col2:
                if level >= 50 and not extracting:
                    if st.button("HARVEST HONEY", key=f"btn_{hive_id}", type="primary"):
                        # Send harvest command to API
                        harvest_response = requests.post(f"{API_BASE}/beehive/{hive_id}/harvest")
                        if harvest_response.status_code == 200:
                            st.success(f"Harvest command sent to Hive {hive_id}!")
                        else:
                            st.error(f"Failed to send command: {harvest_response.text}")
                elif extracting:
                    st.button("Harvesting...", disabled=True)
                else:
                    st.button("Not Ready", disabled=True)

# Auto-refresh every 10 seconds
time.sleep(10)
st.rerun()
