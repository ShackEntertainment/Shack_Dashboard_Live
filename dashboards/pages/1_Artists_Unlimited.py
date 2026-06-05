# 1_Artists_Unlimited.py - SHACK ENTERTAINMENT (HYBRID GROWTH DASHBOARD)
import streamlit as st
import pandas as pd
import sqlite3
import os
import subprocess
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import random

# Page Configuration
st.set_page_config(
    page_title="Artists Unlimited | Shack",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (Matching Home + Soft Filter Colors)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; border: none; border-radius: 6px;
        padding: 8px 16px; font-weight: 600; width: 100%; margin: 5px 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: #1e2330; border: 1px solid #262730;
        border-radius: 12px; padding: 20px; margin: 10px 0;
        border-left: 4px solid;
    }
    .metric-card.green { border-left-color: #4CAF50; }
    .metric-card.blue { border-left-color: #2196F3; }
    .metric-card.orange { border-left-color: #FF9800; }
    .metric-card.purple { border-left-color: #9C27B0; }
    
    .metric-value { font-size: 2.2em; font-weight: bold; margin: 5px 0; color: #ffffff; }
    .metric-label { font-size: 0.85em; color: #8b92a8; text-transform: uppercase; font-weight: 600; }
    .metric-sub { font-size: 0.8em; color: #4CAF50; margin-top: 5px; }
    
    /* Soft Filter Chips - Slate Blue instead of Red */
    div[data-baseweb="tag"] span {
        background-color: #3b82f6 !important;
        color: white !important;
        border-radius: 15px;
    }
    div[data-baseweb="tag"] button {
        background-color: transparent !important;
        color: white !important;
    }
    
    /* Table Styling */
    .stDataFrame { border-radius: 10px; border: 1px solid #262730; }
    
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION ---
@st.cache_data
def load_artist_data():
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

# Mock Sales Data Generator (With Item Column)
@st.cache_data
def generate_mock_sales():
    artists = ["Paul Duncan", "Emma Stone", "Luna Park", "Alex Rivera", "Marcus Webb", "Sarah Chen", "David Kim"]
    types = ["Painting", "Photography", "Sculpture", "Print", "Mixed Media"]
    statuses = ["Completed", "Completed", "Completed", "Pending", "Shipping"]
    
    data = []
    for i in range(20):
        data.append({
            'date': datetime.now() - timedelta(days=random.randint(0, 30)),
            'artist': random.choice(artists),
            'type': random.choice(types),
            'price': round(random.uniform(50, 500), 2),
            'item': f"Artwork #{random.randint(1000, 9999)}",
            'status': random.choice(statuses)
        })
    return pd.DataFrame(data).sort_values('date', ascending=False)

# --- SIDEBAR (Full Utility) ---
with st.sidebar:
    st.markdown("### 🎨 Artists Unlimited")
    st.markdown("*Creative Growth Engine*")
    st.markdown("---")
    
    st.markdown("### ⚡ Quick Actions")
    
    # SYNC DATA
    if st.button("🔄 Sync Data", use_container_width=True):
        with st.spinner("Syncing from Google Sheets..."):
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
                st.error("Sync failed")
    
    # EXPORT
    if st.button("📥 Export Sales Data", use_container_width=True):
        sales_df = generate_mock_sales()
        csv = io.StringIO()
        sales_df.to_csv(csv, index=False)
        st.download_button("Download CSV", csv.getvalue().encode('utf-8'), 
                           file_name="sales_data.csv", mime="text/csv")
    
    # RESTORED BUTTONS
    if st.button("️ Test Low Stock Alert", use_container_width=True):
        st.warning("⚠️ **Alert:** 1 item(s) low on stock\n\nItem: Albury Downs Print")
        
    if st.button("📷 Scan Barcode", use_container_width=True):
        st.info("📷 **Scanner Active:** Please point camera at artwork barcode...")

    # BACK TO HOME
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("Home.py")
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    # Artist Filter
    artists_df = load_artist_data()
    if not artists_df.empty and 'artist_name' in artists_df.columns:
        selected_artists = st.multiselect("Select Artists", options=artists_df['artist_name'].tolist(), default=[])
    else:
        selected_artists = []
    
    st.markdown("---")
    st.caption("© 2026 Shack Entertainment | STANDALONE MODE")

# --- MAIN DASHBOARD ---
# Header
col_logo, col_title = st.columns([1, 10])
with col_logo: st.markdown("### 🎨")
with col_title:
    st.title("Artists Unlimited")
    st.markdown(f"*Artist Management & Sales Tracking* | 📅 {datetime.now().strftime('%d %B %Y')}")
st.markdown("---")

# --- TOP METRICS (Dynamic 1st Glance) ---
artist_df = load_artist_data()
sales_df = generate_mock_sales()

# Apply filters
if selected_artists:
    sales_df = sales_df[sales_df['artist'].isin(selected_artists)]

total_sales = len(sales_df)
total_revenue = sales_df['price'].sum() if not sales_df.empty else 0
active_artists = len(artist_df[artist_df['status'] == 'Active']) if not artist_df.empty else 0
avg_sale = total_revenue / total_sales if total_sales > 0 else 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card green">
        <div class="metric-label">📊 Total Sales</div>
        <div class="metric-value">{total_sales}</div>
        <div class="metric-sub">↑ 12% from last month</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card blue">
        <div class="metric-label">💰 Total Revenue</div>
        <div class="metric-value">£{total_revenue:,.2f}</div>
        <div class="metric-sub">↑ 8.5% from last month</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card orange">
        <div class="metric-label">🎨 Active Artists</div>
        <div class="metric-value">{active_artists}</div>
        <div class="metric-sub">+2 new this week</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card purple">
        <div class="metric-label">📈 Avg Sale Value</div>
        <div class="metric-value">£{avg_sale:.2f}</div>
        <div class="metric-sub">↑ High-value trend</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- TWO COLUMN LAYOUT ---
col_chart, col_table = st.columns([2, 1])

with col_chart:
    st.markdown("### 📈 Sales Trend")
    
    # Prepare chart data
    if not sales_df.empty:
        daily_sales = sales_df.groupby(sales_df['date'].dt.date)['price'].sum().reset_index()
        daily_sales.columns = ['date', 'revenue']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_sales['date'], y=daily_sales['revenue'],
            mode='lines+markers', name='Revenue',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=6, color='#2196F3'),
            fill='tozeroy', fillcolor='rgba(33, 150, 243, 0.1)'
        ))
        
        fig.update_layout(
            plot_bgcolor='#0e1117', paper_bgcolor='#0e1117',
            font=dict(color='#8b92a8'),
            height=350, margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(gridcolor='#262730', title='Date'),
            yaxis=dict(gridcolor='#262730', title='Revenue (£)')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data to display")

with col_table:
    st.markdown("### 📋 Recent Sales")
    
    if not sales_df.empty:
        # Show 10 rows, include Item column
        recent = sales_df.head(10).copy()
        recent['date'] = recent['date'].dt.strftime('%m/%d')
        recent['price'] = recent['price'].apply(lambda x: f"£{x:.2f}")
        
        st.dataframe(recent[['date', 'artist', 'type', 'price', 'item', 'status']], 
                     use_container_width=True, hide_index=True)
    else:
        st.warning("No recent sales")

st.markdown("---")

# --- ARTIST ROSTER (Growth Management) ---
st.markdown("###  Artist Roster")

if not artist_df.empty:
    # Search bar
    search = st.text_input("🔍 Search artists by name or discipline...", key="artist_search")
    
    # Display columns
    display_cols = ['artist_name', 'art_type_discipline', 'tier', 'status', 'managed_by_shack']
    valid_cols = [c for c in display_cols if c in artist_df.columns]
    
    roster_df = artist_df[valid_cols].copy()
    
    # Apply search
    if search:
        roster_df = roster_df[roster_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    
    st.dataframe(roster_df, use_container_width=True, hide_index=True)
else:
    st.warning("️ No artist data found. Please sync data from the sidebar.")

# --- FOOTER ---
st.caption("Shack Entertainment | Talent on the Fringe | Growth Mode Active")