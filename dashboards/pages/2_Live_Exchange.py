import streamlit as st
import pandas as pd
from datetime import datetime
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_sync import load_live_exchange_data

st.set_page_config(page_title="Live Exchange | Shack", page_icon="", layout="wide")

st.markdown("""
<style>
h1, h2, h3 { color: #ffffff !important; }
.kpi { background: #1A1D24; padding: 15px; border-radius: 10px; text-align: center; }
.kpi-val { font-size: 1.8em; font-weight: bold; color: #fff; }
.kpi-lbl { color: #8b92a8; text-transform: uppercase; font-size: 0.8em; }
</style>
""", unsafe_allow_html=True)

st.title(" Live Exchange")
st.markdown(f"*Event Management & Ticketing* | {datetime.now().strftime('%d %B %Y')}")

# Safe unpacking
result = load_live_exchange_data()
if len(result) == 7:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result
else:
    events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict = result
    error_msg = None

if error_msg:
    st.error(f"⚠️ {error_msg}")

# Metrics
total_events = len(events_df) if events_df is not None else 0
total_rev = financials_df['Amount_In'].sum() if financials_df is not None and 'Amount_In' in financials_df.columns else 0
total_exp = financials_df['Amount_Out'].sum() if financials_df is not None and 'Amount_Out' in financials_df.columns else 0
tickets = bookings_df['Quantity'].sum() if bookings_df is not None and 'Quantity' in bookings_df.columns else 0

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi"><div class="kpi-lbl">Events</div><div class="kpi-val">{total_events}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi"><div class="kpi-lbl">Revenue</div><div class="kpi-val">£{total_rev:,.2f}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi"><div class="kpi-lbl">Tickets</div><div class="kpi-val">{int(tickets)}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi"><div class="kpi-lbl">Net Profit</div><div class="kpi-val">£{total_rev-total_exp:,.2f}</div></div>', unsafe_allow_html=True)

st.divider()

# Sidebar
with st.sidebar:
    if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
        st.switch_page("dashboards/Home.py")
    st.markdown("---")
    st.markdown("### ⚡ Actions")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ Refreshed")
        st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs([" Events", "🎫 Bookings", "💰 Financials"])
with tab1:
    st.dataframe(events_df, use_container_width=True, hide_index=True) if events_df is not None else st.info("No data")
with tab2:
    st.dataframe(bookings_df, use_container_width=True, hide_index=True) if bookings_df is not None else st.info("No data")
with tab3:
    st.dataframe(financials_df, use_container_width=True, hide_index=True) if financials_df is not None else st.info("No data")