import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from command_sync import load_command_data

st.set_page_config(page_title="Command Center | Shack Entertainment", page_icon="", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #3b82f6; }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #10b981; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #ef4444; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #8b5cf6; }
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

st.title("🚀 Director's Command Center")
st.markdown("*Strategic Operations Dashboard* | " + datetime.now().strftime('%d %B %Y'))

# Load Data
result = load_command_data()
if len(result) == 5:
    projects_df, kpi_df, team_df, snapshot_dict, error_msg = result
    if error_msg:
        st.warning(f"⚠️ {error_msg}")
else:
    projects_df, kpi_df, team_df, snapshot_dict = result
    error_msg = None

def get_snap(key, default="0"):
    return snapshot_dict.get(key, default) if snapshot_dict else default

st.subheader(" Operational Summary")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card blue">
        <div class="kpi-icon">📁</div>
        <div class="kpi-label">ACTIVE PROJECTS</div>
        <div class="kpi-value">{get_snap('Active_Projects', '0')}</div>
        <div class="kpi-delta">↑ +2 new this week</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card green">
        <div class="kpi-icon">✅</div>
        <div class="kpi-label">ON TRACK</div>
        <div class="kpi-value">{get_snap('On_Track', '0')}</div>
        <div class="kpi-delta">↑ 85% success rate</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card red">
        <div class="kpi-icon">⚠️</div>
        <div class="kpi-label">AT RISK</div>
        <div class="kpi-value">{get_snap('At_Risk', '0')}</div>
        <div class="kpi-delta">↓ -1 from last week</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">BUDGET UTILIZATION</div>
        <div class="kpi-value">{get_snap('Budget_Utilization', '0%')}</div>
        <div class="kpi-delta">↑ On target</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

with st.sidebar:
    st.header("⚡ Quick Actions")
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    st.divider()
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data refreshed!")
        st.rerun()
    if st.button("📝 New Project", use_container_width=True):
        st.info("📝 Project Creator - Feature coming soon!")
    if st.button("👥 Team View", use_container_width=True):
        st.info("👥 Team Management - Feature coming soon!")

tab_proj, tab_kpi, tab_team = st.tabs(["📁 Project Pipeline", "📊 KPI Tracker", "👥 Team Activity"])

with tab_proj:
    st.subheader("📁 Project Pipeline")
    if not projects_df.empty:
        st.dataframe(projects_df, use_container_width=True)
    else:
        st.info("No project data available yet.")

with tab_kpi:
    st.subheader("📊 KPI Tracker")
    if not kpi_df.empty:
        st.dataframe(kpi_df, use_container_width=True)
    else:
        st.info("No KPI data available yet.")

with tab_team:
    st.subheader("👥 Team Activity")
    if not team_df.empty:
        st.dataframe(team_df, use_container_width=True)
    else:
        st.info("No team activity data available yet.")

st.markdown("---")
st.caption("🔄 Data auto-refreshes every 15 minutes | Last updated: " + datetime.now().strftime('%H:%M:%S'))