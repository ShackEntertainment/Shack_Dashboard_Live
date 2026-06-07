import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page config FIRST
st.set_page_config(
    page_title="Shack Entertainment",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 800; }
    h2 { color: #ffffff !important; font-weight: 700; }
    h3 { color: #ffffff !important; font-weight: 600; }
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
        transition: transform 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.6);
    }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #10b981; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #3b82f6; }
    .kpi-card.cyan { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #06b6d4; }
    .kpi-card.amber { background: linear-gradient(145deg, #26221e 0%, #181614 100%); border-bottom: 4px solid #f59e0b; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #8b5cf6; }
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

# --- HEADER WITH LOGO IMAGE ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    # Navigate up one directory from 'dashboards' to 'assets'
    st.image("../assets/shack_main.png", width=80)

with col_title:
    st.title("Shack Entertainment")
    st.markdown("*Executive Command Center* | 📅 " + datetime.now().strftime('%A, %d %B %Y | %I:%M %p'))

st.markdown("---")

# --- EXECUTIVE SUMMARY (KPIs) ---
st.subheader(" Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card green">
        <div style="font-size: 32px; margin-bottom: 10px;">🎨</div>
        <div class="kpi-label">ARTISTS UNLIMITED</div>
        <div class="kpi-value">£230.00</div>
        <div class="kpi-delta">↑ +4 sales • 0 artists</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div style="font-size: 32px; margin-bottom: 10px;">🎫</div>
        <div class="kpi-label">LIVE EXCHANGE</div>
        <div class="kpi-value">£1,240.00</div>
        <div class="kpi-delta">↑ +87 tickets • 2 events</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card cyan">
        <div style="font-size: 32px; margin-bottom: 10px;">📰</div>
        <div class="kpi-label">NEWS NETWORK</div>
        <div class="kpi-value">12</div>
        <div class="kpi-delta">↑ 3200 views • 48% growth</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div style="font-size: 32px; margin-bottom: 10px;">🤝</div>
        <div class="kpi-label">PARTNERSHIPS</div>
        <div class="kpi-value">£0</div>
        <div class="kpi-delta">↑ £0/mo • 0 active</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div style="font-size: 32px; margin-bottom: 10px;">💰</div>
        <div class="kpi-label">FINANCIAL OVERVIEW</div>
        <div class="kpi-value">£1,470.00</div>
        <div class="kpi-delta">↑ £441.00 Shack (30%)</div>
    </div>
    """, unsafe_allow_html=True)

# --- QUICK ACTION BUTTONS ---
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

with col_btn1:
    if st.button("🎨 View Artists", use_container_width=True):
        st.switch_page("dashboards/pages/1_Artists_Unlimited.py")

with col_btn2:
    if st.button("🎫 View Live", use_container_width=True):
        st.switch_page("dashboards/pages/2_Live_Exchange.py")

with col_btn3:
    if st.button("📰 View News", use_container_width=True):
        st.switch_page("dashboards/pages/3_News_Network.py")

with col_btn4:
    if st.button("🤝 View Partners", use_container_width=True):
        st.switch_page("dashboards/pages/5_Partnerships.py")

with col_btn5:
    if st.button(" View Financials", use_container_width=True):
        st.switch_page("dashboards/pages/4_Financial_Overview.py")

st.markdown("---")

# --- MAIN CONTENT AREA ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📋 Recent Transactions")
    # Demo data table
    data = {
        'Date': ['06/05/2026 06:43:39', '06/05/2026 23:32:21'],
        'Description': ['Artist Commission', 'Live Event Ticket'],
        'Amount': ['£30', '£200']
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("📈 Revenue Trend")
    chart_data = pd.DataFrame(
        {'Revenue': [230, 1240, 1470, 1500, 1650]},
        index=['Artists', 'Live', 'News', 'Partnerships', 'Total']
    )
    st.line_chart(chart_data)

with col_right:
    st.subheader(" Alerts & Actions")
    
    st.warning("**Low Stock:** 1 item(s)\nAlbury Downs")
    
    st.success("**Opportunity:** Feature top artist")
    
    st.markdown("---")
    st.subheader(" Quick Actions")
    
    if st.button("🔄 Sync Data from Spreadsheet", use_container_width=True):
        st.cache_data.clear()
        st.success("Data synced!")
        st.rerun()

    if st.button("📄 Export Financial Report", use_container_width=True):
        st.info("Report generation started...")

    if st.button("🧮 Calculate Artist Payouts", use_container_width=True):
        st.info("Calculating...")

    if st.button("🧾 Generate Invoices", use_container_width=True):
        st.info("Generating...")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>© 2026 Shack Entertainment</div>", unsafe_allow_html=True)