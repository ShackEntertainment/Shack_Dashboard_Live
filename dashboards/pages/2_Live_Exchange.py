# 2_Live_Exchange.py - LIVE EXCHANGE DASHBOARD (LIVE DATA VERSION)
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import sys

# Add parent directory to path to import data_sync
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_sync import load_live_exchange_data

st.set_page_config(page_title="Live Exchange | Shack", page_icon="🎫", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #4CAF50; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #F44336; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    .kpi-label { font-size: 0.75em; color: #8b92a8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🎫 Live Exchange")
st.markdown("*Event Management & Ticketing Dashboard* | " + datetime.now().strftime('%d %B %Y'))
st.markdown("---")

# --- LOAD LIVE DATA ---
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_data():
    return load_live_exchange_data()

with st.spinner("🔄 Loading live data from Google Sheets..."):
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = get_data()

if events_df is None:
    st.error("❌ Failed to load data. Check your Google Sheets connection.")
    st.stop()

# --- CALCULATE METRICS (FIXED DATA TYPES) ---
total_events = len(events_df)
total_bookings = len(bookings_df) if bookings_df is not None else 0

# Convert to numeric before summing (fixes string/number mix)
if financials_df is not None and 'Amount_In' in financials_df.columns:
    financials_df['Amount_In'] = pd.to_numeric(financials_df['Amount_In'], errors='coerce').fillna(0)
    total_revenue = financials_df['Amount_In'].sum()
else:
    total_revenue = 0

if financials_df is not None and 'Amount_Out' in financials_df.columns:
    financials_df['Amount_Out'] = pd.to_numeric(financials_df['Amount_Out'], errors='coerce').fillna(0)
    total_expenses = financials_df['Amount_Out'].sum()
else:
    total_expenses = 0

net_profit = total_revenue - total_expenses

if bookings_df is not None and 'Quantity' in bookings_df.columns:
    bookings_df['Quantity'] = pd.to_numeric(bookings_df['Quantity'], errors='coerce').fillna(0)
    tickets_sold = int(bookings_df['Quantity'].sum())
else:
    tickets_sold = 0

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data refreshed!")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Filters")
    if 'Event_Name' in events_df.columns:
        event_filter = st.selectbox("Filter by Event", ["All"] + list(events_df['Event_Name'].unique()))
    else:
        event_filter = st.selectbox("Filter by Event", ["All"])
    
    st.markdown("---")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")

# --- MAIN DASHBOARD ---
st.markdown("### 📊 Live Performance Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div style="font-size: 35px; margin-bottom: 8px;">🎫</div>
        <div class="kpi-label">TOTAL EVENTS</div>
        <div class="kpi-value">{total_events}</div>
        <div class="kpi-delta">Active events</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card green">
        <div style="font-size: 35px; margin-bottom: 8px;">💷</div>
        <div class="kpi-label">TOTAL REVENUE</div>
        <div class="kpi-value">£{total_revenue:,.2f}</div>
        <div class="kpi-delta">All time</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div style="font-size: 35px; margin-bottom: 8px;">📈</div>
        <div class="kpi-label">TICKETS SOLD</div>
        <div class="kpi-value">{tickets_sold}</div>
        <div class="kpi-delta">Total bookings</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    profit_color = "green" if net_profit >= 0 else "red"
    st.markdown(f"""
    <div class="kpi-card {profit_color}">
        <div style="font-size: 35px; margin-bottom: 8px;">💰</div>
        <div class="kpi-label">NET PROFIT</div>
        <div class="kpi-value">£{net_profit:,.2f}</div>
        <div class="kpi-delta">Revenue - Expenses</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- TABS ---
tab_events, tab_bookings, tab_financials, tab_artists = st.tabs([
    "📅 Events", "🎫 Bookings", "💰 Financials", "🎤 Artists"
])

with tab_events:
    st.markdown("### 📅 Events Overview")
    if events_df is not None and not events_df.empty:
        display_cols = [col for col in ['Event_Name', 'Event_Date', 'Status', 'Capacity_Total', 'Capacity_Remaining'] if col in events_df.columns]
        if display_cols:
            st.dataframe(events_df[display_cols], use_container_width=True)
        else:
            st.write("No event data available")
    else:
        st.write("No event data available")

with tab_bookings:
    st.markdown("### 🎫 Recent Bookings")
    if bookings_df is not None and not bookings_df.empty:
        display_cols = [col for col in ['Booking_ID', 'Event_ID', 'Customer_Name', 'Ticket_Type', 'Quantity', 'Total_Price', 'Payment_Status'] if col in bookings_df.columns]
        if display_cols:
            st.dataframe(bookings_df[display_cols], use_container_width=True)
        else:
            st.write("No bookings data available")
    else:
        st.write("No bookings yet")

with tab_financials:
    st.markdown("### 💰 Revenue Breakdown")
    if financials_df is not None and not financials_df.empty:
        st.dataframe(financials_df, use_container_width=True)
    else:
        st.write("No financial data available")

with tab_artists:
    st.markdown("### 🎤 Artist Roster")
    if artists_df is not None and not artists_df.empty:
        display_cols = [col for col in ['Artist_Name', 'Discipline', 'Fee_Type', 'Fee_Amount', 'Payment_Status'] if col in artists_df.columns]
        if display_cols:
            st.dataframe(artists_df[display_cols], use_container_width=True)
        else:
            st.write("No artist data available")
    else:
        st.write("No artist data available")

st.markdown("---")
st.caption("🔄 Data auto-refreshes every 5 minutes | Last updated: " + datetime.now().strftime('%H:%M:%S'))