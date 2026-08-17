import streamlit as st
import pandas as pd
import gspread
import json
import os
from datetime import datetime

st.set_page_config(page_title="The Live Exchange | Shack Entertainment", layout="wide")

# ────────────────────────────────────────
# SHEETS CONNECTION
# ────────────────────────────────────────
@st.cache_resource
def get_sheet_connection():
    project_root = os.path.dirname(os.path.abspath(__file__))
    token_data = json.load(open(os.path.join(project_root, 'configs', 'token.json')))
    creds_raw = json.load(open(os.path.join(project_root, 'configs', 'credentials.json')))['installed']
    
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    creds_obj = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=creds_raw['client_id'],
        client_secret=creds_raw['client_secret'],
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    
    if creds_obj.expired:
        creds_obj.refresh(Request())
        token_data['token'] = creds_obj.token
        if creds_obj.refresh_token:
            token_data['refresh_token'] = creds_obj.refresh_token
        json.dump(token_data, open(os.path.join(project_root, 'configs', 'token.json'), 'w'), indent=2)
    
    gc = gspread.authorize(creds_obj)
    return gc

@st.cache_data(ttl=60)
def load_events():
    try:
        gc = get_sheet_connection()
        sh = gc.open_by_key('1WBsT69FpseHJKxk4ryDrvyQfvpByc8GUYoEfFaLy0kg')
        ws = sh.worksheet('01_Events_Master')
        data = ws.get_all_values()
        if len(data) < 2:
            return pd.DataFrame()
        df = pd.DataFrame(data[1:], columns=data[0])
        # Parse numeric columns
        for col in ['Capacity_Total', 'Tickets_Sold', 'Capacity_Remaining', 'Revenue_Generated']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Event_Date'] = pd.to_datetime(df['Event_Date'], dayfirst=True, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading events: {e}")
        return pd.DataFrame()

# ────────────────────────────────────────
# CUSTOM CSS
# ────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="stSidebar"] button[kind="primary"] {
    background-color: #1E88E5 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px;
}
div[data-testid="stSidebar"] button[kind="primary"]:hover {
    background-color: #1565C0 !important;
}
.stMetric { background: #1A1D24; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────
with st.sidebar:
    st.page_link("live_exchange_dashboard_live.py", label="Live Exchange Hub", icon="#")
    st.divider()
    st.header("Quick Actions")
    if st.button("Add New Event", use_container_width=True, type="primary"):
        st.info("Event creation coming soon - connect to Sheets first!")
    if st.button("View Ticket Sales", use_container_width=True, type="primary"):
        st.session_state.show_sales = True
    if st.button("Calculate Payouts", use_container_width=True, type="primary"):
        st.session_state.show_payouts = True
    st.divider()
    st.caption("Data refreshes every 60 seconds")

# ────────────────────────────────────────
# LOAD DATA
# ────────────────────────────────────────
df = load_events()

# ────────────────────────────────────────
# MAIN UI
# ────────────────────────────────────────
st.title("The Live Exchange")
st.caption("Event booking, ticketing, performer payouts & streaming integration")
st.divider()

if df.empty:
    st.warning("No event data found. Add events to the 01_Events_Master sheet.")
else:
    # Upcoming events only
    upcoming = df[df['Event_Date'] >= pd.Timestamp.today()].sort_values('Event_Date')
    past = df[df['Event_Date'] < pd.Timestamp.today()].sort_values('Event_Date', ascending=False)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    total_rev = df['Revenue_Generated'].sum()
    total_sold = df['Tickets_Sold'].sum()
    total_cap = df['Capacity_Total'].sum()
    col1.metric("Total Revenue", f"£{total_rev:,.2f}")
    col2.metric("Tickets Sold", f"{int(total_sold)}")
    col3.metric("Capacity Fill Rate", f"{total_sold/total_cap*100:.0f}%" if total_cap > 0 else "N/A")
    col4.metric("Events This Year", str(len(df)))

    st.divider()

    # Revenue chart
    if not df.empty:
        st.subheader("Revenue Projection")
        chart_df = df.sort_values('Event_Date').set_index('Event_Name')[['Revenue_Generated']]
        st.bar_chart(chart_df, color="#4CAF50")

    st.divider()

    # Upcoming events
    st.subheader("Upcoming Events")
    if upcoming.empty:
        st.info("No upcoming events scheduled.")
    else:
        display_cols = ['Event_ID', 'Event_Name', 'Event_Date', 'Venue_Name', 
                        'Status', 'Tickets_Sold', 'Capacity_Total', 'Revenue_Generated']
        available = [c for c in display_cols if c in upcoming.columns]
        st.dataframe(upcoming[available].rename(columns={
            'Event_ID': 'ID', 'Event_Name': 'Event', 'Event_Date': 'Date',
            'Venue_Name': 'Venue', 'Tickets_Sold': 'Sold', 'Capacity_Total': 'Capacity',
            'Revenue_Generated': 'Revenue'
        }), use_container_width=True, hide_index=True)

    # Past events
    if not past.empty:
        with st.expander("View Past Events"):
            display_cols = ['Event_ID', 'Event_Name', 'Event_Date', 'Venue_Name', 'Status', 'Tickets_Sold', 'Revenue_Generated']
            available = [c for c in display_cols if c in past.columns]
            st.dataframe(past[available], use_container_width=True, hide_index=True)
