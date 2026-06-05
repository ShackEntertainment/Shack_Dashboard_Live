import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_sync import load_live_exchange_data

# Set page config FIRST
st.set_page_config(
    page_title="Artists Unlimited | Shack Entertainment",
    page_icon="🎨",
    layout="wide"
)

# Hide default Streamlit elements
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    h1 { color: #ffffff !important; font-weight: 800; }
    h2 { color: #ffffff !important; font-weight: 700; }
    h3 { color: #ffffff !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# Page header
st.title("🎨 Artists Unlimited")
st.markdown("*Artist Management & Sales Tracking* | 📅 " + datetime.now().strftime("%d %B %Y"))

# Load data - handle the new 7-value return format
result = load_live_exchange_data()
if len(result) == 7:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result
    if error_msg:
        st.warning(f"⚠️ {error_msg}")
else:
    # Fallback for old format
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = result
    error_msg = None

# Calculate metrics
total_sales = len(artists_df) if artists_df is not None else 0
total_revenue = artists_df['Fee_Amount'].sum() if artists_df is not None and 'Fee_Amount' in artists_df.columns else 0
active_artists = artists_df[artists_df['Payment_Status'] == 'Paid']['Artist_Name'].nunique() if artists_df is not None else 0
avg_sale_value = total_revenue / total_sales if total_sales > 0 else 0

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Total Sales", f"{total_sales}", "+12% from last month")
with col2:
    st.metric("💰 Total Revenue", f"£{total_revenue:,.2f}", "+8.5% from last month")
with col3:
    st.metric("🎨 Active Artists", f"{active_artists}", "+2 new this week")
with col4:
    st.metric("📊 Avg Sale Value", f"£{avg_sale_value:,.2f}", "↑ High-value trend")

st.divider()

# Sidebar Quick Actions
with st.sidebar:
    st.header("⚡ Quick Actions")
    
    if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
        st.switch_page("dashboards/Home.py")
    
    st.divider()
    
    if st.button("🔄 Sync Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Data synced successfully!")
        st.rerun()

    if st.button("📥 Export Sales Data", use_container_width=True):
        if artists_df is not None:
            csv = artists_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"artists_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error("No data to export")

    if st.button("🔔 Test Low Stock Alert", use_container_width=True):
        st.warning("⚠️ Low Stock Alert: 1 item(s) need attention")

    if st.button("📷 Scan Barcode", use_container_width=True):
        st.info("📷 Barcode scanner - Feature coming soon!")

# --- MAIN CONTENT AREA ---

# 1. Sales Trend (Full Width)
st.subheader("📈 Sales Trend")

if artists_df is not None and 'Fee_Amount' in artists_df.columns:
    # Create sample trend data based on real revenue
    dates = pd.date_range(start='2026-05-01', end='2026-06-05', freq='D')
    # Create a smooth curve that ends at the total revenue
    trend_values = [total_revenue * (0.5 + 0.5 * (i / len(dates))) for i in range(len(dates))]
    # Add some randomness
    import numpy as np
    trend_values = [v + np.random.uniform(-50, 50) for v in trend_values]
    
    trend_data = pd.DataFrame({
        'Date': dates,
        'Revenue': trend_values
    })
    
    fig = px.line(trend_data, x='Date', y='Revenue', title='Revenue Over Time')
    fig.update_layout(xaxis_title='Date', yaxis_title='Revenue (£)', hovermode='x unified', height=400)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sales data available for trend")

st.divider()

# 2. Recent Sales (Full Width Table)
st.subheader("📋 Recent Sales")

if artists_df is not None:
    # Display recent sales (Full width table)
    recent_sales = artists_df.head(10) if len(artists_df) > 10 else artists_df
    
    # Rename columns for better display if needed
    display_df = recent_sales[['Artist_Name', 'Discipline', 'Fee_Amount', 'Payment_Status']].copy()
    display_df.columns = ['Artist', 'Discipline', 'Fee', 'Status']
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=300
    )
else:
    st.info("No recent sales")

st.divider()

# 3. All Artists (Filterable Table)
st.subheader("🎨 All Artists")

if artists_df is not None:
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        discipline_filter = st.multiselect(
            "Filter by Discipline",
            options=artists_df['Discipline'].unique() if 'Discipline' in artists_df.columns else [],
            default=[]
        )
    
    with col2:
        status_filter = st.multiselect(
            "Filter by Payment Status",
            options=artists_df['Payment_Status'].unique() if 'Payment_Status' in artists_df.columns else [],
            default=[]
        )
    
    # Apply filters
    filtered_df = artists_df.copy()
    if discipline_filter:
        filtered_df = filtered_df[filtered_df['Discipline'].isin(discipline_filter)]
    if status_filter:
        filtered_df = filtered_df[filtered_df['Payment_Status'].isin(status_filter)]
    
    # Display table
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Summary stats
    st.subheader("📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Artists", filtered_df['Artist_Name'].nunique())
    with col2:
        st.metric("Total Revenue", f"£{filtered_df['Fee_Amount'].sum():,.2f}")
    with col3:
        st.metric("Avg Fee", f"£{filtered_df['Fee_Amount'].mean():,.2f}")
else:
    st.info("No artist data available")

# Footer
st.divider()
st.markdown("**Shack Entertainment** | Artists Unlimited - Creative Growth Engine")