# Home.py - SHACK ENTERTAINMENT (LOGOS INSIDE KPIS)
import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.graph_objects as go
from datetime import datetime, timedelta
import subprocess
import io
import base64

# Page Configuration
st.set_page_config(
    page_title="Shack Entertainment | Executive",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER TO LOAD IMAGES ---
def get_image_base64(filename):
    """Convert image to base64 for embedding in HTML"""
    possible_paths = [
        os.path.join('assets', filename),
        os.path.join(os.path.dirname(__file__), '..', 'assets', filename),
        os.path.join(os.getcwd(), 'assets', filename),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    return None

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* KPI Card Container */
    .kpi-card {
        border: 1px solid #2d323e;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center; /* Center content */
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 160px;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    
    /* Muted Gradients */
    .kpi-card.artists { background: linear-gradient(145deg, #1e261e 0%, #141814 100%); border-bottom: 4px solid #4CAF50; }
    .kpi-card.live { background: linear-gradient(145deg, #1e2026 0%, #141518 100%); border-bottom: 4px solid #2196F3; }
    .kpi-card.news { background: linear-gradient(145deg, #1e2626 0%, #141818 100%); border-bottom: 4px solid #00ACC1; }
    .kpi-card.partnerships { background: linear-gradient(145deg, #26231e 0%, #181614 100%); border-bottom: 4px solid #FF9800; }
    .kpi-card.financial { background: linear-gradient(145deg, #261e26 0%, #181418 100%); border-bottom: 4px solid #9C27B0; }
    
    /* Internal Elements */
    .card-logo { width: 45px; height: 45px; object-fit: contain; margin-bottom: 10px; opacity: 0.9; }
    .kpi-label { font-size: 0.75em; color: #8b92a8; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px; }
    .kpi-value { font-size: 2em; font-weight: bold; color: #ffffff; margin: 5px 0; }
    .kpi-delta { font-size: 0.75em; color: #4CAF50; margin-top: 5px; font-weight: 600; }
    
    /* Sidebar Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; border: none; border-radius: 6px;
        padding: 8px 16px; font-weight: 600; width: 100%; margin: 5px 0;
    }
    
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# Database Connection
@st.cache_data
def load_data():
    try:
        db_path = r"C:\Users\Bola\Documents\Shack_Project\agents\executive_cache.db"
        if not os.path.exists(db_path):
            return pd.DataFrame()
        conn = sqlite3.connect(db_path)
        df = pd.read_sql('SELECT * FROM artists_cache', conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- SIDEBAR ---
with st.sidebar:
    logo_path = os.path.join('assets', 'shack_main.png')
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.markdown("### 🎪 Shack Entertainment")
    
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Sync Data from Spreadsheet", use_container_width=True):
        with st.spinner("Syncing..."):
            try:
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                result = subprocess.run(
                    ['python', r'C:\Users\Bola\Documents\Shack_Project\agents\data_sync.py'],
                    capture_output=True, text=True, cwd=r'C:\Users\Bola\Documents\Shack_Project',
                    env=env, encoding='utf-8', errors='replace'
                )
                if result.returncode == 0:
                    st.success("✅ Data synced!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("⚠️ Sync failed")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    if st.button("📥 Export Financial Report", use_container_width=True):
        df = load_data()
        if not df.empty:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("Download CSV", csv_buffer.getvalue().encode('utf-8'), 
                               file_name=f"financial_report_{datetime.now().strftime('%Y%m%d')}.csv",
                               mime="text/csv")
    
    if st.button("💰 Calculate Artist Payouts", use_container_width=True):
        st.info("Coming soon")
    
    if st.button(" Generate Invoices", use_container_width=True):
        st.info("Coming soon")
    
    st.markdown("---")
    st.caption("© 2026 Shack Entertainment")

# --- HEADER ---
col_logo, col_title = st.columns([1, 10])
with col_logo:
    logo_path = os.path.join('assets', 'shack_main.png')
    if os.path.exists(logo_path):
        st.image(logo_path, width=70)
    else:
        st.markdown("### 🎪")

with col_title:
    st.title("Shack Entertainment")
    st.markdown(f"*Executive Command Center* | 📅 {datetime.now().strftime('%A, %d %B %Y | %I:%M %p')}")

st.markdown("---")

# --- KPI CARDS (LOGOS EMBEDDED) ---
col1, col2, col3, col4, col5 = st.columns(5)

# 1. ARTISTS UNLIMITED
with col1:
    img_b64 = get_image_base64('artists_unlimited.png')
    logo_html = f'<img class="card-logo" src="data:image/png;base64,{img_b64}" />' if img_b64 else ''
    
    st.markdown(f"""
    <div class="kpi-card artists">
        {logo_html}
        <div class="kpi-label">ARTISTS UNLIMITED</div>
        <div class="kpi-value">£230.00</div>
        <div class="kpi-delta">↑ 4 sales • 0 artists</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎨 View Artists", key="kpi1", use_container_width=True):
        st.switch_page("pages/1_Artists_Unlimited.py")

# 2. LIVE EXCHANGE
with col2:
    img_b64 = get_image_base64('live_exchange.png')
    logo_html = f'<img class="card-logo" src="data:image/png;base64,{img_b64}" />' if img_b64 else ''
    
    st.markdown(f"""
    <div class="kpi-card live">
        {logo_html}
        <div class="kpi-label">LIVE EXCHANGE</div>
        <div class="kpi-value">£1,240.00</div>
        <div class="kpi-delta">↑ 87 tickets • 2 events</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎵 View Live", key="kpi2", use_container_width=True):
        st.switch_page("pages/2_Live_Exchange.py")

# 3. SHACK NEWS
with col3:
    img_b64 = get_image_base64('shack_news.png')
    logo_html = f'<img class="card-logo" src="data:image/png;base64,{img_b64}" />' if img_b64 else ''
    
    st.markdown(f"""
    <div class="kpi-card news">
        {logo_html}
        <div class="kpi-label">SHACK NEWS NETWORK</div>
        <div class="kpi-value">12</div>
        <div class="kpi-delta">↑ 3200 views • 48% growth</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button(" View News", key="kpi3", use_container_width=True):
        st.switch_page("pages/3_News_Network.py")

# 4. PARTNERSHIPS
with col4:
    st.markdown("""
    <div class="kpi-card partnerships">
        <div style="font-size: 40px; margin-bottom: 5px;">🤝</div>
        <div class="kpi-label">PARTNERSHIPS</div>
        <div class="kpi-value">£0</div>
        <div class="kpi-delta">↑ £0/mo • 0 active</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🤝 View Partners", key="kpi4", use_container_width=True):
        st.switch_page("pages/5_Partnerships.py")

# 5. FINANCIAL OVERVIEW
with col5:
    st.markdown("""
    <div class="kpi-card financial">
        <div style="font-size: 40px; margin-bottom: 5px;">💰</div>
        <div class="kpi-label">FINANCIAL OVERVIEW</div>
        <div class="kpi-value">£1,470.00</div>
        <div class="kpi-delta">↑ £441.00 Shack (30%)</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("💰 View Financials", key="kpi5", use_container_width=True):
        st.switch_page("pages/4_Financial_Overview.py")

st.markdown("---")

# --- CONTENT ---
col_left, col_right = st.columns([2, 1])
with col_left:
    st.markdown("### Recent Transactions")
    transactions = pd.DataFrame({
        'Date': ['06/05/2026 06:43:39', '06/05/2026 23:32:21'],
        'Description': ['Artist Commission', 'Live Event Ticket'],
        'Amount': ['£30', '£200']
    })
    st.dataframe(transactions, use_container_width=True, hide_index=True)
    
    st.markdown("### 📈 Revenue Trend")
    dates = pd.date_range(start='2026-06-01', end='2026-06-05', freq='1h')
    revenue = [230 + i*0.1 for i in range(len(dates))]
    fig = go.Figure(go.Scatter(x=dates, y=revenue, mode='lines', 
                                line=dict(color='#4CAF50', width=2),
                                fill='tozeroy', fillcolor='rgba(76, 175, 80, 0.2)'))
    fig.update_layout(plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
                      height=250, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("### ️ Alerts & Actions")
    st.warning("️ **Low Stock:** 1 item(s)\n\nAlbury Downs")
    st.success("✅ **Opportunity:** Feature top artist")

st.markdown("---")
st.caption("Shack Entertainment | Talent on the Fringe")