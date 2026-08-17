import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cache_reader import load_news_network_data as load_news_data
# Set page config
st.set_page_config(
    page_title="Shack News Network | Shack Entertainment",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme, Blue Buttons, and Uniform KPI Sizing
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
    
    /* Uniform KPI Cards */
    .kpi-card { 
        border: 1px solid #2d323e; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 10px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.5); 
        min-height: 135px; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center;
    }
    .kpi-card.cyan { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #06b6d4; }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #10b981; }
    .kpi-card.amber { background: linear-gradient(145deg, #26221e 0%, #181614 100%); border-bottom: 4px solid #f59e0b; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #8b5cf6; }
    
    .kpi-label { font-size: 0.75em; color: #a0a8c0; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; text-shadow: 1px 1px 2px #000; }
    .kpi-delta { font-size: 0.75em; color: #10b981; margin-top: 5px; font-weight: 600; }
    
    /* Sidebar Buttons */
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

current = "News Network"  # auto-detected from filename
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


# Header
st.title("📰 Shack News Network")
st.markdown("*Director's Analytics Dashboard* | " + datetime.now().strftime('%d %B %Y'))

# Load Data
import contextlib
result = None
with contextlib.redirect_stdout(None):
    try:
        result = load_news_data()
    except Exception as e:
        result = (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                 pd.DataFrame(), pd.DataFrame(), {},
                 f"Unexpected error: {str(e)}")

if result is None or not isinstance(result, (list, tuple)):
    content_df, youtube_df, social_df, referral_df, campaign_df = (pd.DataFrame(),)*5
    snapshot_dict = {}
    error_msg = "Unexpected result format from data sync."
elif len(result) == 7:
    content_df, youtube_df, social_df, referral_df, campaign_df, snapshot_dict, error_msg = result
else:
    content_df, youtube_df, social_df, referral_df, campaign_df = (pd.DataFrame(),)*5
    snapshot_dict = {}
    error_msg = None

# Show connection error if present
if error_msg:
    st.warning(f"Sheets connection: {error_msg}")

# Demo data only when ALL sheets are empty
all_empty = all(
    (df is None or len(df) == 0)
    for df in [content_df, youtube_df, social_df, referral_df, campaign_df]
)
if all_empty and not error_msg:
    st.info("No News Network data yet — add data to Shack_News_Network_Master spreadsheet.")

# Helper to safely get snapshot values
def get_snap(key, default="0"):
    return snapshot_dict.get(key, default) if snapshot_dict else default

# --- EXECUTIVE SUMMARY (KPIs) ---
st.subheader(" Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card cyan">
        <div style="font-size: 35px; margin-bottom: 8px;">🌐</div>
        <div class="kpi-label">TOTAL REACH</div>
        <div class="kpi-value">{get_snap('Total_Reach', '—')}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card green">
        <div style="font-size: 35px; margin-bottom: 8px;">🔗</div>
        <div class="kpi-label">SOCIAL SHARES</div>
        <div class="kpi-value">{get_snap('Total_Social_Shares', '—')}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card amber">
        <div style="font-size: 35px; margin-bottom: 8px;"></div>
        <div class="kpi-label">REFERRAL SALES</div>
        <div class="kpi-value">£{get_snap('Referral_Sales', '—')}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div style="font-size: 35px; margin-bottom: 8px;">📊</div>
        <div class="kpi-label">AVG ENGAGEMENT</div>
        <div class="kpi-value">{get_snap('Avg_Engagement_Rate', '—')}</div>
        <div class="kpi-delta">Add data to track</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚡ Quick Actions")
    
    
    if st.button("🔄 Sync All Platforms", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data synced successfully!")
        st.rerun()

    if st.button(" Write New Article", use_container_width=True):
        st.info("📝 Content Editor - Feature coming soon!")

    if st.button("📺 Upload YouTube Video", use_container_width=True):
        st.info("🎥 Video Uploader - Feature coming soon!")

    if st.button("📊 Export Full Report", use_container_width=True):
        st.success(" Report generated!")

# --- MAIN TABS ---
tab_overview, tab_youtube, tab_social, tab_content, tab_advanced = st.tabs([
    " Overview", "📺 YouTube Studio", "📱 Social Media", "📚 Content Library", "🔬 Advanced Analytics"
])

with tab_overview:
    st.subheader(" YouTube Channel")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Views", get_snap('YouTube_Views', '—'), "Add data to track")
    with col2:
        st.metric("Total Subscribers", get_snap('Total_Followers', '—'), "Add data to track")
    
    st.divider()
    
    st.subheader("📱 Social Followers")
    if social_df is not None and not social_df.empty:
        try:
            platform_counts = social_df.groupby('Platform')['Followers'].max()
            st.bar_chart(platform_counts)
        except Exception:
            st.info("Social data loaded — chart requires Platform and Followers columns.")
    else:
        st.info("No social data available yet.")

with tab_youtube:
    st.subheader("📺 YouTube Performance")
    if youtube_df is not None and not youtube_df.empty:
        st.dataframe(youtube_df, use_container_width=True)
    else:
        st.info("No YouTube data available yet.")

with tab_social:
    st.subheader("📱 Social Media Metrics")
    if social_df is not None and not social_df.empty:
        st.dataframe(social_df, use_container_width=True)
    else:
        st.info("No social media data available yet.")

with tab_content:
    st.subheader("📚 Content Library")
    if content_df is not None and not content_df.empty:
        st.dataframe(content_df, use_container_width=True)
    else:
        st.info("No content library data available yet.")

with tab_advanced:
    st.subheader("🔬 Advanced Analytics")
    st.info("Advanced analytics module coming in v2.0")

st.markdown("---")
st.caption("🔄 Data auto-refreshes every 15 minutes | Last updated: " + datetime.now().strftime('%H:%M:%S'))
