import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cache_reader import load_live_exchange_data

st.set_page_config(page_title="Live Exchange | Shack", page_icon="🎫", layout="wide", initial_sidebar_state="expanded")

# Hide default Streamlit elements and force dark theme
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    footer {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 800; text-shadow: 2px 2px 4px #000000; }
    h2, h3 { color: #ffffff !important; }
    .main { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #0e1117 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stApp { background-color: #0e1117 !important; }
    header { visibility: hidden; }
    [data-testid="stHeader"] { background-color: #0e1117; padding: 0; }
    /* [data-testid="stToolbar"] { visibility: hidden; } */
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






# --- NAVIGATION BAR ---

current = "Live Exchange"  # auto-detected from filename
cols = st.columns(8)
for i, (name, path, label) in enumerate([
    ("Home", r"Home.py", "Home"),
    ("Artists", r"pages/1_Artists_Unlimited.py", "Artists"),
    ("Live Exchange", r"pages/2_Live_Exchange.py", "Live Exchange"),
    ("News Network", r"pages/3_News_Network.py", "News Network"),
    ("Finance", r"pages/4_Financial_Overview.py", "Finance"),
    ("Partnerships", r"pages/5_Partnerships.py", "Partnerships"),
    ("Alerts", r"pages/6_System_Alert.py", "Alerts"),
    ("Command", r"pages/7_Command_Center.py", "Command"),
]):
    with cols[i]:
        if name == current:
            st.button(label, disabled=True, use_container_width=True, type="primary")
        else:
            if st.button(label, use_container_width=True):
                st.switch_page(path)
st.markdown("---")


# --- HEADER ---
st.title("🎫 Live Exchange")
st.markdown("*Event Management & Ticketing Dashboard* | " + datetime.now().strftime('%d %B %Y'))
st.markdown("---")

# --- LOAD LIVE DATA ---
@st.cache_data(ttl=300)
def get_data():
    return load_live_exchange_data()

import contextlib
result = None
with contextlib.redirect_stdout(None):
    try:
        result = get_data()
    except Exception:
        result = (None,)*6 + ({}, None)
if result is None:
    result = (None,)*6 + ({}, None)
if len(result) == 7:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result
else:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = result
    error_msg = None

# Show error if connection failed
if error_msg:
    st.warning(f"Sheets connection issue: {error_msg}")

# Demo data only as absolute last fallback — only when ALL sheets are empty and no error
all_empty = (
    (events_df is None or len(events_df) == 0) and
    (bookings_df is None or len(bookings_df) == 0) and
    (financials_df is None or len(financials_df) == 0) and
    (artists_df is None or len(artists_df) == 0)
)
if all_empty and not error_msg:
    st.info("No live data yet — add events, bookings, or financial records to Shack_Live_Exchange_Master")
    events_df = pd.DataFrame({
        'Event_Name': ['Summer Rooftop Jam', 'Underground Bass Night', 'Jazz & Canvas Gala', 'Neon Folk Session'],
        'Event_Date': ['2026-06-15', '2026-06-22', '2026-07-05', '2026-07-12'],
        'Status': ['On Sale', 'Planning', 'On Sale', 'Planning'],
        'Capacity_Total': [150, 80, 200, 40],
        'Capacity_Remaining': [150, 80, 200, 40]
    })
    bookings_df = pd.DataFrame({
        'Booking_ID': ['BK001', 'BK002', 'BK003', 'BK004', 'BK005', 'BK006'],
        'Event_ID': [1, 1, 2, 3, 3, 4],
        'Customer_Name': ['Alice Johnson', 'Bob Smith', 'Carol White', 'David Brown', 'Emma Davis', 'Frank Wilson'],
        'Ticket_Type': ['General Admission', 'VIP', 'General Admission', 'General Admission', 'VIP', 'General Admission'],
        'Quantity': [2, 1, 4, 1, 2, 3],
        'Total_Price': [50.00, 75.00, 80.00, 30.00, 150.00, 75.00],
        'Payment_Status': ['Paid', 'Paid', 'Pending', 'Paid', 'Paid', 'Pending']
    })
    financials_df = pd.DataFrame({
        'Transaction_ID': ['TXN001', 'TXN002', 'TXN003', 'TXN004', 'TXN005'],
        'Date': ['2026-05-01', '2026-05-05', '2026-05-10', '2026-05-15', '2026-05-20'],
        'Description': ['Ticket Sales - Rooftop Jam', 'Venue Deposit', 'Artist Fee - DJ Kemet', 'Marketing', 'Equipment Rental'],
        'Category': ['Revenue', 'Expense', 'Expense', 'Expense', 'Expense'],
        'Amount_In': [450.00, 0.00, 0.00, 0.00, 0.00],
        'Amount_Out': [0.00, 200.00, 500.00, 150.00, 300.00],
        'Event_Link': ['Summer Rooftop Jam', 'Summer Rooftop Jam', 'Summer Rooftop Jam', 'General', 'General']
    })

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
    
    st.markdown("---")
    
    # 2. Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    # Refresh Button Logic
    if st.button(" Refresh Data", use_container_width=True):
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
    "📅 Events", "🎫 Bookings", "💰 Financials", " Artists"
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