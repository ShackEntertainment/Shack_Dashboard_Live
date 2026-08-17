import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# --- HELPER FUNCTION TO LOAD IMAGES AS BASE64 ---
def get_image_as_base64(image_name):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        file_path = os.path.join(root_dir, 'assets', image_name)
        
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        return None

# Set page config
st.set_page_config(
    page_title="Shack Entertainment",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    footer {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 800; margin-top: -20px !important; }
    h2 { color: #ffffff !important; font-weight: 700; }
    h3 { color: #ffffff !important; font-weight: 600; }
    .main { background-color: #0e1117; }
    [data-testid="stSidebar"] { background-color: #0e1117 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stApp { background-color: #0e1117 !important; }
    /* Hide the white Streamlit header bar */
    header { visibility: hidden; }
    [data-testid="stHeader"] { background-color: #0e1117; padding: 0; }
    /* [data-testid="stToolbar"] { visibility: hidden; } */
    /* Sidebar nav text — ensure white and readable */
    [data-testid="stSidebar"] a, [data-testid="stSidebar"] div[class*="nav"], [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] a:hover, [data-testid="stSidebar"] div:hover { color: #60a5fa !important; }
        /* === TEXT VISIBILITY FIX === */
        p, span, div { color: #d8dce8 !important; }
        em, i { color: #b8c0d0 !important; }
        .stMarkdown p { color: #c8d0e0 !important; }
        /* === END TEXT VISIBILITY FIX === */
    .stColumns { align-items: center !important; }
    
    .kpi-card { 
        border: 1px solid #2d323e; 
        border-radius: 12px; 
        padding: 15px 10px; 
        margin-bottom: 10px; 
        text-align: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.5); 
        height: 145px !important;
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
    .kpi-label { font-size: 0.65em; color: #a0a8c0; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin: 0; }
    .kpi-value { font-size: 1.6em; font-weight: bold; color: #ffffff; margin: 2px 0; text-shadow: 1px 1px 2px #000; }
    .kpi-delta { font-size: 0.65em; color: #10b981; margin-top: 0; font-weight: 600; }
    
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

current = "Home"  # auto-detected from filename
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


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("### Shack Entertainment")
    st.markdown("Quick Actions")
    
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

# --- HEADER WITH LOGO IMAGE (UPDATED TO shack_trans.png) ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    # CHANGED: Now uses shack_trans.png
    main_logo_b64 = get_image_as_base64("shack_trans.png")
    if main_logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{main_logo_b64}" width="80" style="display:block;">', unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size: 60px;'>🏠</div>", unsafe_allow_html=True)

with col_title:
    st.title("Shack Entertainment")
    st.markdown("*Executive Command Center* | 📅 " + datetime.now().strftime('%A, %d %B %Y | %I:%M %p'))

st.markdown("---")

# --- EXECUTIVE SUMMARY (KPIs) ---
st.subheader(" Executive Summary")

col1, col2, col3, col4, col5 = st.columns(5)

# 1. Artists Unlimited
with col1:
    img_b64 = get_image_as_base64("artists_unlimited_trans.png")
    img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px;">' if img_b64 else '🎨'
    st.markdown(f"""
    <div class="kpi-card green">
        <div>{img_html}</div>
        <div class="kpi-label">ARTISTS UNLIMITED</div>
        <div class="kpi-value">£230.00</div>
        <div class="kpi-delta">↑ +4 sales • 0 artists</div>
    </div>
    """, unsafe_allow_html=True)

# 2. Live Exchange
with col2:
    img_b64 = get_image_as_base64("live_exchange_trans.png")
    img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px;">' if img_b64 else ''
    st.markdown(f"""
    <div class="kpi-card blue">
        <div>{img_html}</div>
        <div class="kpi-label">LIVE EXCHANGE</div>
        <div class="kpi-value">£1,240.00</div>
        <div class="kpi-delta">↑ +87 tickets • 2 events</div>
    </div>
    """, unsafe_allow_html=True)

# 3. News Network
with col3:
    img_b64 = get_image_as_base64("shack_news_trans.png")
    img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px;">' if img_b64 else '📰'
    st.markdown(f"""
    <div class="kpi-card cyan">
        <div>{img_html}</div>
        <div class="kpi-label">NEWS NETWORK</div>
        <div class="kpi-value">12</div>
        <div class="kpi-delta">↑ 3200 views • 48% growth</div>
    </div>
    """, unsafe_allow_html=True)

# 4. Partnerships
with col4:
    img_b64 = get_image_as_base64("shack_light_logo.png")
    img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px;">' if img_b64 else '🤝'
    st.markdown(f"""
    <div class="kpi-card amber">
        <div>{img_html}</div>
        <div class="kpi-label">PARTNERSHIPS</div>
        <div class="kpi-value">£0</div>
        <div class="kpi-delta">↑ £0/mo • 0 active</div>
    </div>
    """, unsafe_allow_html=True)

# 5. Financial Overview
with col5:
    img_b64 = get_image_as_base64("shack_main.png")
    img_html = f'<img src="data:image/png;base64,{img_b64}" style="width: 40px; height: 40px; object-fit: contain; margin-bottom: 5px;">' if img_b64 else '💰'
    st.markdown(f"""
    <div class="kpi-card purple">
        <div>{img_html}</div>
        <div class="kpi-label">FINANCIAL OVERVIEW</div>
        <div class="kpi-value">£1,470.00</div>
        <div class="kpi-delta">↑ £441.00 Shack (30%)</div>
    </div>
    """, unsafe_allow_html=True)

# --- QUICK ACTION BUTTONS (Below KPIs) ---
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

with col_btn1:
    if st.button("🎨 View Artists", use_container_width=True):
        st.switch_page("dashboards/pages/1_Artists_Unlimited.py")

with col_btn2:
    if st.button(" View Live", use_container_width=True):
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
    data = {
        'Date': ['06/05/2026 06:43:39', '06/05/2026 23:32:21'],
        'Description': ['Artist Commission', 'Live Event Ticket'],
        'Amount': ['£30', '£200']
    }
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader(" Revenue Trend")
    chart_data = pd.DataFrame(
        {'Arm': ['Artists', 'Live', 'News', 'Partnerships', 'Total'],
         'Revenue': [230, 1240, 1470, 1500, 1650]}
    )
    st.dataframe(chart_data, use_container_width=True, hide_index=True)

with col_right:
    st.subheader(" Alerts & Actions")
    
    st.warning("**Low Stock:** 1 item(s)\nAlbury Downs")
    
    st.success("**Opportunity:** Feature top artist")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>© 2026 Shack Entertainment</div>", unsafe_allow_html=True)