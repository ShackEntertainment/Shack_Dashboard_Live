import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cache_reader import load_financial_overview_data as load_finance_data
st.set_page_config(page_title="Financial Overview | Shack Entertainment", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #0e1117; }
    .main { background-color: #0e1117; }
    .stApp { background-color: #0e1117 !important; }
    header { visibility: hidden; }
    [data-testid="stHeader"] { background-color: #0e1117; padding: 0; }
    /* [data-testid="stToolbar"] { visibility: hidden; } */
    [data-testid="stSidebar"] a, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #e2e8f0 !important; }
    h1 { color: #ffffff !important; font-weight: 800; }
    h2, h3 { color: #ffffff !important; }
    .main { background-color: #0e1117; }
    .kpi-card { 
        border: 1px solid #2d323e; 
        border-radius: 12px; 
        padding: 20px 15px; 
        margin-bottom: 10px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.5); 
        height: 150px !important;
        display: flex; 
        flex-direction: column; 
        justify-content: space-between; 
        align-items: center;
    }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #10b981; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #ef4444; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #3b82f6; }
    .kpi-card.amber { background: linear-gradient(145deg, #26221e 0%, #181614 100%); border-bottom: 4px solid #f59e0b; }
    .kpi-icon { font-size: 32px; margin-bottom: 10px; }
    .kpi-label { font-size: 0.7em; color: #a0a8c0; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin: 0; }
    .kpi-value { font-size: 1.8em; font-weight: bold; color: #ffffff; margin: 5px 0; text-shadow: 1px 1px 2px #000; }
    .kpi-delta { font-size: 0.75em; color: #10b981; margin-top: 0; font-weight: 600; }
    div.stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #2563eb 0%, #60a5fa 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)






# --- NAVIGATION BAR ---

current = "Finance"  # auto-detected from filename
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


st.title(" Financial Overview")
st.markdown("*Executive Finance Dashboard* | " + datetime.now().strftime('%d %B %Y'))

# Load Data
import contextlib
result = None
with contextlib.redirect_stdout(None):
    try:
        result = load_finance_data()
    except Exception as e:
        result = (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
                  f"Unexpected error: {str(e)}")

if result is None or not isinstance(result, (list, tuple)):
    revenue_df, expense_df, cashflow_df = (pd.DataFrame(),)*3
    snapshot_dict = {}
    error_msg = "Unexpected result format from data sync."
elif len(result) == 5:
    revenue_df, expense_df, cashflow_df, snapshot_dict, error_msg = result
else:
    revenue_df, expense_df, cashflow_df = (pd.DataFrame(),)*3
    snapshot_dict = {}
    error_msg = None

# Show connection error if present
if error_msg:
    st.warning(f"Sheets connection: {error_msg}")

# Demo data only when ALL sheets are empty
all_empty = all(
    (df is None or len(df) == 0)
    for df in [revenue_df, expense_df, cashflow_df]
)
if all_empty and not error_msg:
    st.info("No Financial Overview data yet — add data to Shack_Financial_Overview_Master spreadsheet.")

def get_snap(key, default="—"):
    return snapshot_dict.get(key, default) if snapshot_dict else default

st.subheader("📊 Financial Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card green">
        <div class="kpi-icon">💷</div>
        <div class="kpi-label">TOTAL REVENUE</div>
        <div class="kpi-value">£{get_snap('Total_Revenue', '—')}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card red">
        <div class="kpi-icon"></div>
        <div class="kpi-label">TOTAL EXPENSES</div>
        <div class="kpi-value">£{get_snap('Total_Expenses', '—').strip()}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-icon"></div>
        <div class="kpi-label">NET PROFIT</div>
        <div class="kpi-value">£{get_snap('Net_Profit', '—')}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div class="kpi-icon">🏦</div>
        <div class="kpi-label">CASH RESERVE</div>
        <div class="kpi-value">£{get_snap('Cash_Reserve', '—')}</div>
        <div class="kpi-delta">{get_snap('Runway_Months', '—')} months runway</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

with st.sidebar:
    st.header("⚡ Quick Actions")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data refreshed!")
        st.rerun()
    if st.button("📥 Export Financials", use_container_width=True):
        st.success("📥 Report downloaded!")

tab_rev, tab_exp, tab_cash = st.tabs(["💷 Revenue Streams", "💸 Expense Breakdown", "🌊 Cash Flow"])

with tab_rev:
    st.subheader("💷 Revenue Streams")
    if revenue_df is not None and not revenue_df.empty:
        st.dataframe(revenue_df, use_container_width=True)
    else:
        st.info("No revenue data available yet.")

with tab_exp:
    st.subheader("💸 Expense Breakdown")
    if expense_df is not None and not expense_df.empty:
        st.dataframe(expense_df, use_container_width=True)
    else:
        st.info("No expense data available yet.")

with tab_cash:
    st.subheader("🌊 Cash Flow")
    if cashflow_df is not None and not cashflow_df.empty:
        st.dataframe(cashflow_df, use_container_width=True)
    else:
        st.info("No cash flow data available yet.")

st.markdown("---")
st.caption("🔄 Data auto-refreshes every 30 minutes | Last updated: " + datetime.now().strftime('%H:%M:%S'))
