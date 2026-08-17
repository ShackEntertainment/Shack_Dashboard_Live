# FORCE RELOAD 2
import streamlit as st
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="The Live Exchange | Shack Entertainment", layout="wide", page_icon="🎟️")
# --- FORCE BLUE SIDEBAR BUTTONS ---
st.markdown("""
    <style>
    /* Force Standard Buttons to be Blue */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #1E88E5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
    }
    div[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #1565C0 !important;
        color: white !important;
    }
    
    /* Force Download Button to be Blue */
    div[data-testid="stSidebar"] a.stDownloadButton {
        background-color: #1E88E5 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
    }
    div[data-testid="stSidebar"] a.stDownloadButton:hover {
        background-color: #1565C0 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)
# ----------------------------------
# Custom CSS for blue buttons
st.markdown("""
    <style>
    div[data-testid="stSidebar"] button[kind="primary"] {
        background-color: #1E88E5;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    div[data-testid="stSidebar"] button[kind="primary"]:hover {
        background-color: #1565C0;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────
# DUMMY DATA
# ────────────────────────────────────────
events = [
    {"name": "Fringe Folk Festival 🎸", "artist": "The Wandering Minstrels", "date": datetime.now() + timedelta(days=5), "price": 12.50, "capacity": 100, "sold": 47},
    {"name": "Poetry & Paint Night 🎨", "artist": "Sarah Chen", "date": datetime.now() + timedelta(days=12), "price": 15.00, "capacity": 40, "sold": 23},
    {"name": "Comedy Club Showcase 🎤", "artist": "The Laughing Shack", "date": datetime.now() + timedelta(days=18), "price": 10.00, "capacity": 80, "sold": 65},
    {"name": "Jazz in the Park 🎷", "artist": "Blue Note Trio", "date": datetime.now() + timedelta(days=25), "price": 20.00, "capacity": 30, "sold": 12},
    {"name": "Acoustic Sunset 🌅", "artist": "Paul Duncan", "date": datetime.now() + timedelta(days=30), "price": 18.00, "capacity": 50, "sold": 0}
]

df = pd.DataFrame(events)
df["Revenue"] = df["sold"] * df["price"]
df["Artist Payout (70%)"] = df["Revenue"] * 0.70
df["Shack Commission (30%)"] = df["Revenue"] * 0.30

# ────────────────────────────────────────
# SIDEBAR
# ────────────────────────────────────────
with st.sidebar:
    # HOME BUTTON (emoji only in icon, not label)
    st.page_link("Home.py", label="Return to Hub", icon="🏠")
    
    st.divider()
    st.header("⚡ Quick Actions")
    
    # BLUE BUTTONS (type="primary")
    if st.button("📅 Add New Event", use_container_width=True, type="primary"):
        with st.form("new_event_form"):
            st.text_input("Event Name")
            st.text_input("Artist Name")
            st.number_input("Ticket Price", min_value=0.0)
            st.number_input("Capacity", min_value=1)
            submitted = st.form_submit_button("Create Event")
            if submitted: st.success("✅ Event created! (Demo mode)")
    
    if st.button("🎟️ View Ticket Sales", use_container_width=True, type="primary"):
        st.subheader("Current Ticket Sales")
        st.dataframe(df[["name", "artist", "sold", "capacity", "Revenue"]], use_container_width=True, hide_index=True)
    
    if st.button("💰 Calculate Payouts", use_container_width=True, type="primary"):
        st.subheader("Payout Breakdown (70/30)")
        st.dataframe(df[["name", "artist", "Revenue", "Artist Payout (70%)", "Shack Commission (30%)"]], use_container_width=True, hide_index=True)
        total_payout = df["Artist Payout (70%)"].sum()
        st.metric("Total Payout Due", f"£{total_payout:,.2f}")

    st.divider()
    st.caption("💡 Tip: Double-click 'Live Exchange Dashboard' shortcut to launch!")

# ────────────────────────────────────────
# MAIN UI
# ────────────────────────────────────────
st.title("🎟️ The Live Exchange")
st.caption("Event booking, ticketing, performer payouts & streaming integration")
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("Total Projected Revenue", f"£{df['Revenue'].sum():,.2f}")
col2.metric("Tickets Sold", f"{df['sold'].sum()} / {df['capacity'].sum()}")
col3.metric("Artist Payouts Due", f"£{df['Artist Payout (70%)'].sum():,.2f}")

st.divider()
st.subheader("📈 Revenue Projection")
st.bar_chart(df.set_index("name")["Revenue"], color="#4CAF50")

st.divider()
st.subheader("📅 Upcoming Events")
st.dataframe(df[["name", "artist", "date", "sold", "capacity", "Revenue"]], use_container_width=True, hide_index=True)