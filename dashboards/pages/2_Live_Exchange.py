import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_sync import load_live_exchange_data

st.set_page_config(page_title="Live Exchange | Shack", page_icon="🎫", layout="wide")

# Hide default Streamlit elements and force dark theme
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 800; text-shadow: 2px 2px 4px #000000; }
    h2, h3 { color: #ffffff !important; }
    .main { background-color: #0e1117; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #4CAF50; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #F44336; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    .kpi-label { font-size: 0.75em; color: #a0a8c0; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; text-shadow: 1px 1px 2px #000; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; }
    .stButton>button:hover { background: linear-gradient(90deg, #2563eb 0%, #60a5fa 100%); }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🎫 Live Exchange")
st.markdown("*Event Management & Ticketing Dashboard* | " + datetime.now().strftime('%d %B %Y'))
st.markdown("---")

# --- LOAD LIVE DATA - Handle 7-value return ---
@st.cache_data(ttl=300)
def get_data():
    return load_live_exchange_data()

result = get_data()
if len(result) == 7:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result
else:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = result
    error_msg = None

# Show error if connection failed
if error_msg:
    st.error(f"🔌 Connection Issue: {error_msg}")
    st.info("Switching to demo data for display.")

# Handle case where data loading fails completely
if events_df is None and bookings_df is None:
    st.error("❌ Failed to load any data.")
    st.stop()

# --- CALCULATE METRICS ---
total_events = len(events_df) if events_df is not None else 0
total_bookings = len(bookings_df) if bookings_df is not None else 0

# Safe numeric conversion
total_revenue = 0
if financials_df is not None and 'Amount_In' in financials_df.columns:
    total_revenue = pd.to_numeric(financials_df['Amount_In'], errors='coerce').fillna(0).sum()

total_expenses = 0
if financials_df is not None and 'Amount_Out' in financials_df.columns:
    total_expenses = pd.to_numeric(financials_df['Amount_Out'], errors='coerce').fillna(0).sum()

net_profit = total_revenue - total_expenses

tickets_sold = 0
if bookings_df is not None and 'Quantity' in bookings_df.columns:
    tickets_sold = int(pd.to_numeric(bookings_df['Quantity'], errors='coerce').fillna(0).sum())

# --- SIDEBAR ---
with st.sidebar:
    # 1. Back to Home (Top)
    if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
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
    st.markdown("### 📊 Filters")
    event_filter = "All"
    if events_df is not None and 'Event_Name' in events_df.columns:
        event_filter = st.selectbox("Filter by Event", ["All"] + list(events_df['Event_Name'].unique()))

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
            st.info("No event data available")
    else:
        st.info("No event data available")

with tab_bookings:
    st.markdown("### 🎫 Recent Bookings")
    if bookings_df is not None and not bookings_df.empty:
        display_cols = [col for col in ['Booking_ID', 'Event_ID', 'Customer_Name', 'Ticket_Type', 'Quantity', 'Total_Price', 'Payment_Status'] if col in bookings_df.columns]
        if display_cols:
            st.dataframe(bookings_df[display_cols], use_container_width=True)
        else:
            st.info("No bookings data available")
    else:
        st.info("No bookings yet")

with tab_financials:
    st.markdown("### 💰 Revenue Breakdown")
    if financials_df is not None and not financials_df.empty:
        st.dataframe(financials_df, use_container_width=True)
    else:
        st.info("No financial data available")

with tab_artists:
    st.markdown("### 🎤 Artist Roster")
    if artists_df is not None and not artists_df.empty:
        display_cols = [col for col in ['Artist_Name', 'Discipline', 'Fee_Type', 'Fee_Amount', 'Payment_Status'] if col in artists_df.columns]
        if display_cols:
            st.dataframe(artists_df[display_cols], use_container_width=True)
        else:
            st.info("No artist data available")
    else:
        st.info("No artist data available")

st.markdown("---")
st.caption("🔄 Data auto-refreshes every 5 minutes | Last updated: " + datetime.now().strftime('%H:%M:%S'))