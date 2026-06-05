import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_sync import load_live_exchange_data

st.set_page_config(page_title="Live Exchange | Shack", page_icon="", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    h1 { color: #ffffff !important; font-weight: 800; }
    h2, h3 { color: #ffffff !important; }
    .main { background-color: #0e1117; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; text-align: center; }
    .kpi-card.green { background: #1e261e; border-bottom: 4px solid #4CAF50; }
    .kpi-card.red { background: #261e1e; border-bottom: 4px solid #F44336; }
    .kpi-card.blue { background: #1e2026; border-bottom: 4px solid #2196F3; }
    .kpi-card.purple { background: #261e26; border-bottom: 4px solid #9C27B0; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; }
    .kpi-label { color: #a0a8c0; text-transform: uppercase; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🎫 Live Exchange")
st.markdown("*Event Management & Ticketing Dashboard* | " + datetime.now().strftime('%d %B %Y'))
st.markdown("---")

# --- SIDEBAR (FIXED ORDER) ---
with st.sidebar:
    # 1. Back to Home (Top)
    if st.button(" Back to Home", use_container_width=True, type="primary"):
        st.switch_page("dashboards/Home.py")
    
    st.markdown("---")
    
    # 2. Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    # Refresh Button Logic
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data refreshed!")
        st.rerun()
    
    st.markdown("---")
    
    # 3. Filters
    st.markdown("###  Filters")
    # (Filters logic would go here)

# --- LOAD DATA ---
@st.cache_data(ttl=300)
def get_data():
    return load_live_exchange_data()

with st.spinner("🔄 Loading live data..."):
    result = get_data()

# Handle result (which is now a tuple of (data, error_message))
if result is None:
    st.error("❌ Failed to load data.")
    st.stop()

events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result

# If there was an error connecting to sheets, show it prominently
if error_msg:
    st.error(f"️ Connection Issue: {error_msg}")
    st.info("Switching to demo data for display.")
    # Fallback to demo data logic here if needed, or just show what we have

# --- DASHBOARD CONTENT ---
# (Keep your existing KPI and Tab code here, just ensure it uses the loaded data)
# ...