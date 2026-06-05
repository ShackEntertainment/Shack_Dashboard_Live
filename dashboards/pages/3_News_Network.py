# 3_News_Network.py - SHACK NEWS NETWORK (DIRECTOR'S EDITION)
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import io
import base64
import random

st.set_page_config(page_title="Shack News Network | Director", page_icon="📰", layout="wide", initial_sidebar_state="expanded")

# --- ASSET LOADER ---
def get_base64_image_safe(filename):
    try:
        paths = [os.path.join(os.path.dirname(__file__), '..', 'assets', filename), os.path.join(os.getcwd(), 'assets', filename)]
        for path in paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except: pass
    return None

logo_b64 = get_base64_image_safe('shack_main.png')

# --- COMPREHENSIVE CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .kpi-card { border: 1px solid #2d323e; border-radius: 12px; padding: 15px; margin-bottom: 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: transform 0.2s; }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-card.cyan { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #00ACC1; }
    .kpi-card.green { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #4CAF50; }
    .kpi-card.orange { background: linear-gradient(145deg, #26231e 0%, #181614 100%); border-bottom: 4px solid #FF9800; }
    .kpi-card.purple { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    .kpi-card.blue { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.red { background: linear-gradient(145deg, #261e1e 0%, #181414 100%); border-bottom: 4px solid #F44336; }
    .kpi-label { font-size: 0.75em; color: #8b92a8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    .metric-detail { font-size: 0.85em; color: #8b92a8; margin-top: 8px; padding-top: 8px; border-top: 1px solid #2d323e; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; width: 100%; margin: 5px 0; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- COMPREHENSIVE DATA LOADERS ---
@st.cache_data
def load_all_data():
    # Articles data
    articles = ["Artist Spotlight: Paul Duncan", "Live Exchange Summer Recap", "New Gallery Opening", "Behind the Scenes: Luna Park", "Shack Merch Drop #5", "Interview: Alex Rivera", "Studio Sessions: Emma Stone", "Exhibition Review: Hyper Realism"]
    categories = ["Feature", "News", "Interview", "Review", "Announcement", "Video"]
    articles_data = []
    for i in range(30):
        articles_data.append({
            'date': datetime.now() - timedelta(days=random.randint(0, 30)),
            'title': random.choice(articles),
            'category': random.choice(categories),
            'views': random.randint(500, 8000),
            'shares': random.randint(50, 500),
            'engagement': round(random.uniform(2.5, 12.5), 1),
            'revenue': round(random.uniform(0, 150), 2),
            'status': random.choice(["Published", "Draft", "Scheduled", "Trending"])
        })
    
    # YouTube data
    youtube_data = []
    videos = ["Shack News Weekly #12", "Artist Interview: Paul Duncan", "Live Event Highlights", "Gallery Tour", "Behind the Scenes"]
    for i in range(15):
        youtube_data.append({
            'date': datetime.now() - timedelta(days=random.randint(0, 30)),
            'video': random.choice(videos),
            'views': random.randint(100, 2000),
            'likes': random.randint(10, 200),
            'comments': random.randint(5, 50),
            'subscribers_gained': random.randint(1, 15)
        })
    
    # Social media data
    social_data = []
    platforms = ['Twitter/X', 'Facebook', 'Instagram', 'TikTok']
    for platform in platforms:
        social_data.append({
            'platform': platform,
            'followers': random.randint(500, 2000),
            'engagement_rate': round(random.uniform(3.0, 9.0), 1),
            'posts_this_week': random.randint(3, 12),
            'reach': random.randint(2000, 8000)
        })
    
    return pd.DataFrame(articles_data), pd.DataFrame(youtube_data), pd.DataFrame(social_data)

# --- SIDEBAR ---
with st.sidebar:
    if logo_b64: st.markdown(f'<div style="text-align:center; margin-bottom: 15px;"><img src="data:image/png;base64,{logo_b64}" width="140"></div>', unsafe_allow_html=True)
    else: st.markdown("### 🎪 Shack Entertainment")
    
    st.markdown("### 📰 Shack News Network")
    st.markdown("*Director's Command Center*")
    st.markdown("---")
    
    st.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Sync All Platforms", use_container_width=True):
        with st.spinner("Syncing all accounts..."): 
            st.success("✅ All platforms synced"); st.cache_data.clear(); st.rerun()
    if st.button("📝 Write New Article", use_container_width=True): 
        st.info("📝 **Editor:** Opening content studio...")
    if st.button("🎬 Upload YouTube Video", use_container_width=True): 
        st.info("🎬 **YouTube Studio:** Preparing upload...")
    if st.button("📊 Export Full Report", use_container_width=True):
        articles_df, youtube_df, social_df = load_all_data()
        zip_buffer = io.BytesIO()
        with st.spinner("Generating report..."):
            st.success("📊 Report ready for download")
    st.markdown("---")
    
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    st.caption("© 2026 Shack Entertainment | DIRECTOR MODE")

# --- HEADER ---
col_logo, col_title = st.columns([1, 10])
with col_logo:
    if logo_b64: st.markdown(f'<div style="margin-top:10px;"><img src="data:image/png;base64,{logo_b64}" width="60"></div>', unsafe_allow_html=True)
    else: st.markdown("### 📰")
with col_title:
    st.title("Shack News Network")
    st.markdown(f"*Director's Analytics Dashboard* |  {datetime.now().strftime('%d %B %Y')}")
st.markdown("---")

# --- LOAD DATA ---
articles_df, youtube_df, social_df = load_all_data()

# --- CALCULATE METRICS ---
total_reach = social_df['reach'].sum() + articles_df['views'].sum()
social_shares = articles_df['shares'].sum()
referral_sales = articles_df['revenue'].sum()
avg_engagement = articles_df['engagement'].mean()
youtube_views = youtube_df['views'].sum()
youtube_subscribers = youtube_df['subscribers_gained'].sum()
total_followers = social_df['followers'].sum()

# --- TABS FOR FUNCTIONAL PANELS ---
tab_overview, tab_youtube, tab_social, tab_content, tab_analytics = st.tabs([
    "📊 Overview", 
    "▶️ YouTube Studio", 
    "📱 Social Media", 
    "📝 Content Library",
    "📈 Advanced Analytics"
])

# === TAB 1: OVERVIEW ===
with tab_overview:
    st.markdown("### 🎯 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card cyan">
            <div style="font-size: 35px; margin-bottom: 8px;">🌐</div>
            <div class="kpi-label">TOTAL REACH</div>
            <div class="kpi-value">{total_reach:,}</div>
            <div class="kpi-delta">↑ +12% this week</div>
            <div class="metric-detail">All platforms combined</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="kpi-card green">
            <div style="font-size: 35px; margin-bottom: 8px;">🔗</div>
            <div class="kpi-label">SOCIAL SHARES</div>
            <div class="kpi-value">{social_shares}</div>
            <div class="kpi-delta">↑ +8% this week</div>
            <div class="metric-detail">Viral content tracker</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="kpi-card orange">
            <div style="font-size: 35px; margin-bottom: 8px;">💸</div>
            <div class="kpi-label">REFERRAL SALES</div>
            <div class="kpi-value">£{referral_sales:,.2f}</div>
            <div class="kpi-delta">↑ +15% this week</div>
            <div class="metric-detail">Revenue from content</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="kpi-card purple">
            <div style="font-size: 35px; margin-bottom: 8px;">💬</div>
            <div class="kpi-label">AVG ENGAGEMENT</div>
            <div class="kpi-value">{avg_engagement:.1f}%</div>
            <div class="kpi-delta">↑ +2.1% this week</div>
            <div class="metric-detail">Across all platforms</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"""
        <div class="kpi-card red">
            <div style="font-size: 35px; margin-bottom: 8px;">▶️</div>
            <div class="kpi-label">YOUTUBE CHANNEL</div>
            <div class="kpi-value">{youtube_views:,}</div>
            <div class="kpi-delta">+{youtube_subscribers} subscribers</div>
            <div class="metric-detail">Weekly views</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div style="font-size: 35px; margin-bottom: 8px;">📱</div>
            <div class="kpi-label">SOCIAL FOLLOWERS</div>
            <div class="kpi-value">{total_followers:,}</div>
            <div class="kpi-delta">↑ 12% growth</div>
            <div class="metric-detail">Total across platforms</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Performance Chart
    st.markdown("### 📊 Performance by Platform")
    platform_perf = pd.DataFrame({
        'Platform': ['Blog', 'YouTube', 'Twitter/X', 'Facebook', 'Instagram'],
        'Views': [articles_df['views'].sum(), youtube_df['views'].sum(), 
                  social_df[social_df['platform']=='Twitter/X']['reach'].values[0] if len(social_df[social_df['platform']=='Twitter/X']) > 0 else 3000,
                  social_df[social_df['platform']=='Facebook']['reach'].values[0] if len(social_df[social_df['platform']=='Facebook']) > 0 else 4000,
                  social_df[social_df['platform']=='Instagram']['reach'].values[0] if len(social_df[social_df['platform']=='Instagram']) > 0 else 2500]
    })
    
    fig = px.bar(platform_perf, x='Platform', y='Views', 
                 color='Platform',
                 color_discrete_map={'Blog': '#00ACC1', 'YouTube': '#FF0000', 'Twitter/X': '#1DA1F2', 'Facebook': '#1877F2', 'Instagram': '#E4405F'},
                 template='plotly_dark')
    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# === TAB 2: YOUTUBE STUDIO ===
with tab_youtube:
    st.markdown("### ▶️ YouTube Analytics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Views", f"{youtube_df['views'].sum():,}", "+12%")
    with col2:
        st.metric("Total Likes", f"{youtube_df['likes'].sum():,}", "+8%")
    with col3:
        st.metric("Subscribers Gained", f"{youtube_df['subscribers_gained'].sum()}", "+15 this week")
    
    st.markdown("---")
    
    # Top Videos
    st.markdown("### 🎬 Top Performing Videos")
    top_videos = youtube_df.groupby('video')['views'].sum().reset_index().sort_values('views', ascending=False).head(5)
    st.dataframe(top_videos, use_container_width=True, hide_index=True)
    
    # Views Trend
    st.markdown("### 📈 Views Trend")
    daily_views = youtube_df.groupby(youtube_df['date'].dt.date)['views'].sum().reset_index()
    daily_views.columns = ['date', 'views']
    fig_line = px.line(daily_views, x='date', y='views', template='plotly_dark')
    fig_line.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=300)
    st.plotly_chart(fig_line, use_container_width=True)

# === TAB 3: SOCIAL MEDIA ===
with tab_social:
    st.markdown("### 📱 Social Media Dashboard")
    
    # Platform Cards
    for idx, row in social_df.iterrows():
        with st.expander(f"**{row['platform']}** - {row['followers']:,} followers | {row['engagement_rate']}% engagement"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Followers", f"{row['followers']:,}")
            col2.metric("Engagement Rate", f"{row['engagement_rate']}%")
            col3.metric("Weekly Reach", f"{row['reach']:,}")
            st.progress(min(row['engagement_rate'] / 10, 1.0))
            st.caption("Engagement Score")
    
    st.markdown("---")
    
    # Social Comparison
    st.markdown("### 📊 Platform Comparison")
    fig_pie = px.pie(social_df, values='followers', names='platform', 
                     color_discrete_sequence=px.colors.qualitative.Set3,
                     template='plotly_dark')
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# === TAB 4: CONTENT LIBRARY ===
with tab_content:
    st.markdown("### 📝 Content Management")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search articles...", key="content_search")
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All", "Published", "Draft", "Scheduled", "Trending"])
    
    display_df = articles_df.copy()
    if search:
        display_df = display_df[display_df['title'].str.contains(search, case=False, na=False)]
    if filter_status != "All":
        display_df = display_df[display_df['status'] == filter_status]
    
    st.dataframe(display_df[['date', 'title', 'category', 'views', 'engagement', 'status']], 
                 use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### 📅 Content Calendar")
    st.info("📅 **Calendar View:** Integration with Google Calendar coming soon")

# === TAB 5: ADVANCED ANALYTICS ===
with tab_analytics:
    st.markdown("### 📈 Advanced Analytics")
    
    # Engagement Funnel
    st.markdown("#### 🎯 Engagement Funnel")
    funnel_data = pd.DataFrame({
        'Stage': ['Impressions', 'Clicks', 'Engagements', 'Shares', 'Conversions'],
        'Count': [50000, 15000, 8000, 2000, 450]
    })
    fig_funnel = px.funnel(funnel_data, x='Count', y='Stage', template='plotly_dark')
    fig_funnel.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117', height=400)
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    st.markdown("---")
    
    # Revenue Attribution
    st.markdown("#### 💰 Revenue Attribution")
    col1, col2, col3 = st.columns(3)
    col1.metric("Direct Sales", "£1,240", "+10%")
    col2.metric("Affiliate Revenue", "£680", "+15%")
    col3.metric("Ad Revenue", "£347", "+5%")
    
    st.markdown("---")
    
    # Export Options
    st.markdown("### 📥 Export Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Export CSV"):
            csv = articles_df.to_csv(index=False)
            st.download_button("Download Articles", csv, "articles.csv", "text/csv")
    with col2:
        if st.button("📈 Export Analytics"):
            csv = youtube_df.to_csv(index=False)
            st.download_button("Download YouTube Data", csv, "youtube.csv", "text/csv")
    with col3:
        if st.button("📱 Export Social"):
            csv = social_df.to_csv(index=False)
            st.download_button("Download Social Data", csv, "social.csv", "text/csv")

st.markdown("---")
st.caption("Shack Entertainment | Shack News Network | Talent on the Fringe | Director Mode Active")