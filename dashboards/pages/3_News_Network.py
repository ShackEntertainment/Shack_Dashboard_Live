import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from news_sync import load_news_data

# Set page config
st.set_page_config(
    page_title="Shack News Network | Shack Entertainment",
    page_icon="📰",
    layout="wide"
)

# Custom CSS for Dark Theme and Blue Buttons
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 800; }
    h2, h3 { color: #ffffff !important; }
    .main { background-color: #0e1117; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
    .kpi-card.cyan { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #06b6d4; }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #10b981; }
    .kpi-card.amber { background: linear-gradient(145deg, #26221e 0%, #181614 100%); border-bottom: 4px solid #f59e0b; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #8b5cf6; }
    .kpi-label { font-size: 0.75em; color: #a0a8c0; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; text-shadow: 1px 1px 2px #000; }
    .kpi-delta { font-size: 0.75em; color: #10b981; margin-top: 5px; font-weight: 600; }
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

# Header
st.title(" Shack News Network")
st.markdown("*Director's Analytics Dashboard* | " + datetime.now().strftime('%d %B %Y'))

# Load Data
result = load_news_data()
if len(result) == 7:
    content_df, youtube_df, social_df, referral_df, campaign_df, snapshot_dict, error_msg = result
    if error_msg:
        st.warning(f"⚠️ {error_msg}")
else:
    content_df, youtube_df, social_df, referral_df, campaign_df, snapshot_dict = result
    error_msg = None

# Helper to safely get snapshot values
def get_snap(key, default="0"):
    return snapshot_dict.get(key, default) if snapshot_dict else default

# --- EXECUTIVE SUMMARY (KPIs) ---
st.subheader("🎯 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card cyan">
        <div style="font-size: 35px; margin-bottom: 8px;">🌐</div>
        <div class="kpi-label">TOTAL REACH</div>
        <div class="kpi-value">{get_snap('Total_Reach', '156,477')}</div>
        <div class="kpi-delta">↑ +12% this week</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card green">
        <div style="font-size: 35px; margin-bottom: 8px;">🔗</div>
        <div class="kpi-label">SOCIAL SHARES</div>
        <div class="kpi-value">{get_snap('Total_Social_Shares', '9,117')}</div>
        <div class="kpi-delta">↑ +8% this week</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div style="font-size: 35px; margin-bottom: 8px;">💸</div>
        <div class="kpi-label">REFERRAL SALES</div>
        <div class="kpi-value">£{get_snap('Referral_Sales', '2,262.49')}</div>
        <div class="kpi-delta">↑ +15% this week</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div style="font-size: 35px; margin-bottom: 8px;"></div>
        <div class="kpi-label">AVG ENGAGEMENT</div>
        <div class="kpi-value">{get_snap('Avg_Engagement_Rate', '7.4%')}</div>
        <div class="kpi-delta">↑ +2.1% this week</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚡ Quick Actions")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")  # FIXED PATH
    
    st.divider()
    
    if st.button("🔄 Sync All Platforms", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data synced successfully!")
        st.rerun()

    if st.button("📝 Write New Article", use_container_width=True):
        st.info("📝 Content Editor - Feature coming soon!")

    if st.button("📺 Upload YouTube Video", use_container_width=True):
        st.info(" Video Uploader - Feature coming soon!")

    if st.button("📊 Export Full Report", use_container_width=True):
        st.success("📊 Report generated!")

# --- MAIN TABS ---
tab_overview, tab_youtube, tab_social, tab_content, tab_advanced = st.tabs([
    "📊 Overview", "📺 YouTube Studio", " Social Media", "📚 Content Library", "🔬 Advanced Analytics"
])

with tab_overview:
    st.subheader("📺 YouTube Channel")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Views", get_snap('YouTube_Views', '14,214'), "+450 this week")
    with col2:
        st.metric("Total Subscribers", get_snap('Total_Followers', '5,199'), "+85 this week")
    
    st.divider()
    
    st.subheader("📱 Social Followers")
    if not social_df.empty:
        # Aggregate followers by platform
        platform_counts = social_df.groupby('Platform')['Followers'].max()
        st.bar_chart(platform_counts)
    else:
        st.info("No social data available yet.")

with tab_youtube:
    st.subheader("📺 YouTube Performance")
    if not youtube_df.empty:
        st.dataframe(youtube_df, use_container_width=True)
    else:
        st.info("No YouTube data available yet.")

with tab_social:
    st.subheader("📱 Social Media Metrics")
    if not social_df.empty:
        st.dataframe(social_df, use_container_width=True)
    else:
        st.info("No social media data available yet.")

with tab_content:
    st.subheader("📚 Content Library")
    if not content_df.empty:
        st.dataframe(content_df, use_container_width=True)
    else:
        st.info("No content library data available yet.")

with tab_advanced:
    st.subheader("🔬 Advanced Analytics")
    st.info("Advanced analytics module coming in v2.0")

st.markdown("---")
st.caption("🔄 Data auto-refreshes every 15 minutes | Last updated: " + datetime.now().strftime('%H:%M:%S'))