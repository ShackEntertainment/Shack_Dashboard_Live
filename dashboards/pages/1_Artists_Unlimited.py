import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_sync import load_live_exchange_data

st.set_page_config(page_title="Artists Unlimited | Shack", page_icon="🎨", layout="wide")

st.markdown("""
<style>
h1, h2, h3 { color: #ffffff !important; }
.kpi-card { background: #1A1D24; border-radius: 12px; padding: 15px; border-left: 4px solid #3b82f6; }
.stDataFrame { background-color: #0E1117; }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Artists Unlimited")
st.markdown(f"*Artist Management & Sales Tracking* | 📅 {datetime.now().strftime('%d %B %Y')}")

# Safe unpacking (handles 7 values from data_sync)
result = load_live_exchange_data()
if len(result) == 7:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result
else:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = result
    error_msg = None

if error_msg:
    st.warning(f"⚠️ {error_msg}")

# Metrics
total_sales = len(artists_df) if artists_df is not None else 0
total_revenue = artists_df['Fee_Amount'].sum() if artists_df is not None and 'Fee_Amount' in artists_df.columns else 0
active_artists = artists_df[artists_df['Payment_Status'] == 'Paid']['Artist_Name'].nunique() if artists_df is not None else 0
avg_sale = total_revenue / total_sales if total_sales > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric(" Total Sales", total_sales)
col2.metric("💰 Total Revenue", f"£{total_revenue:,.2f}")
col3.metric(" Active Artists", active_artists)
col4.metric("📊 Avg Sale Value", f"£{avg_sale:,.2f}")

st.divider()

# Sidebar
with st.sidebar:
    if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
        st.switch_page("dashboards/Home.py")
    st.markdown("---")
    st.markdown("###  Quick Actions")
    if st.button("🔄 Sync Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Synced!")
        st.rerun()
    if st.button("📥 Export CSV", use_container_width=True) and artists_df is not None:
        st.download_button("Download", artists_df.to_csv(index=False), "artists.csv", "text/csv")

# Main Content
if artists_df is not None and not artists_df.empty:
    st.subheader("📈 Sales Trend")
    fig = px.line(artists_df, x='Artist_Name', y='Fee_Amount', title='Artist Fees')
    fig.update_layout(paper_bgcolor='#0E1117', plot_bgcolor='#0E1117', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Artist Roster")
    st.dataframe(artists_df, use_container_width=True, hide_index=True)
else:
    st.info("No artist data loaded.")