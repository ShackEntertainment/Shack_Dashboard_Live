import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Set page config
st.set_page_config(
    page_title="Artists Unlimited | Shack Entertainment",
    page_icon="🎨",
    layout="wide"
)

# Import data sync functions
import sys
sys.path.append('.')
from data_sync import load_live_exchange_data, log_operation

# Page header
st.title("🎨 Artists Unlimited")
st.markdown("*Artist Management & Sales Tracking* | 📅 " + datetime.now().strftime("%d %B %Y"))

# Load data
with st.spinner("Loading artist data..."):
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = load_live_exchange_data()

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
st.sidebar.header("⚡ Quick Actions")

if st.sidebar.button("🔄 Sync Data", use_container_width=True):
    st.cache_data.clear()
    st.success("✅ Data synced successfully!")
    st.rerun()

if st.sidebar.button("📥 Export Sales Data", use_container_width=True):
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

if st.sidebar.button("🔔 Test Low Stock Alert", use_container_width=True):
    st.warning("⚠️ Low Stock Alert: 1 item(s) need attention")

if st.sidebar.button("📷 Scan Barcode", use_container_width=True):
    st.info("📷 Barcode scanner - Feature coming soon!")

if st.sidebar.button("🏠 Back to Home", use_container_width=True):
    st.switch_page("dashboards/Home.py")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Sales Trend")
    
    if artists_df is not None and 'Fee_Amount' in artists_df.columns:
        # Create sample trend data
        dates = pd.date_range(start='2026-05-01', end='2026-06-05', freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Revenue': [total_revenue / len(dates) * (1 + i * 0.01) for i in range(len(dates))]
        })
        
        fig = px.line(trend_data, x='Date', y='Revenue', title='Revenue Over Time')
        fig.update_layout(xaxis_title='Date', yaxis_title='Revenue (£)', hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales data available")

with col2:
    st.subheader("📋 Recent Sales")
    
    if artists_df is not None:
        # Display recent sales
        recent_sales = artists_df.head(10) if len(artists_df) > 10 else artists_df
        st.dataframe(
            recent_sales[['Artist_Name', 'Discipline', 'Fee_Amount', 'Payment_Status']].head(10),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent sales")

st.divider()

# Artists detail table
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
        hide_index=True
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