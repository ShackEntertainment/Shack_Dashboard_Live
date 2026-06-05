# data_sync.py - With error handling for missing libraries
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Try to import Google libraries, but don't crash if they're missing
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    st.warning("⚠️ Google Sheets libraries not available. Running in demo mode.")

def load_live_exchange_data():
    """Load data from Google Sheets or return demo data"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        # Return demo data instead of crashing
        return get_demo_data()
    
    try:
        # Your existing Google Sheets code here...
        # (Keep the rest of your function as-is)
        ...
    except Exception as e:
        st.error(f"Error loading Google Sheets: {e}")
        return get_demo_data()

def get_demo_data():
    """Return sample data when Google Sheets is unavailable"""
    
    # Events demo data
    events_df = pd.DataFrame({
        'Event_Name': ['Summer Rooftop Jam', 'Underground Bass Night', 'Jazz & Canvas Gala', 'Neon Folk Session'],
        'Event_Date': ['2026-06-15', '2026-06-22', '2026-07-05', '2026-07-12'],
        'Status': ['On Sale', 'Planning', 'On Sale', 'Planning'],
        'Capacity_Total': [150, 80, 200, 40],
        'Capacity_Remaining': [150, 80, 200, 40],
        'Tickets_Sold': [0, 0, 0, 0]
    })
    
    # Bookings demo data
    bookings_df = pd.DataFrame({
        'Booking_ID': ['BK001', 'BK002', 'BK003', 'BK004', 'BK005', 'BK006'],
        'Event_ID': [1, 1, 2, 3, 3, 4],
        'Customer_Name': ['Alice Johnson', 'Bob Smith', 'Carol White', 'David Brown', 'Emma Davis', 'Frank Wilson'],
        'Ticket_Type': ['General Admission', 'VIP', 'General Admission', 'General Admission', 'VIP', 'General Admission'],
        'Quantity': [2, 1, 4, 1, 2, 3],
        'Unit_Price': [25.00, 75.00, 20.00, 30.00, 75.00, 25.00],
        'Total_Price': [50.00, 75.00, 80.00, 30.00, 150.00, 75.00],
        'Booking_Date': ['2026-05-01', '2026-05-03', '2026-05-05', '2026-05-07', '2026-05-10', '2026-05-12'],
        'Payment_Status': ['Paid', 'Paid', 'Pending', 'Paid', 'Paid', 'Pending']
    })
    
    # Artists demo data
    artists_df = pd.DataFrame({
        'Artist_Name': ['DJ Kemet', 'Maya Strings', 'Bass Collective', 'Jazz Fusion Trio', 'Folk Revival', 'Electronic Soul'],
        'Discipline': ['DJ/Producer', 'Visual Artist', 'DJ/Producer', 'Music', 'Music', 'Music'],
        'Fee_Type': ['Fixed', 'Commission', 'Fixed', 'Fixed', 'Fixed', 'Fixed'],
        'Fee_Amount': [500.00, 0.00, 300.00, 800.00, 400.00, 350.00],
        'Payment_Status': ['Paid', 'N/A', 'Pending', 'Deposit Paid', 'Pending', 'Pending']
    })
    
    # Financials demo data
    financials_df = pd.DataFrame({
        'Transaction_ID': ['TXN001', 'TXN002', 'TXN003', 'TXN004', 'TXN005'],
        'Date': ['2026-05-01', '2026-05-05', '2026-05-10', '2026-05-15', '2026-05-20'],
        'Description': ['Ticket Sales - Rooftop Jam', 'Venue Deposit', 'Artist Fee - DJ Kemet', 'Marketing', 'Equipment Rental'],
        'Category': ['Revenue', 'Expense', 'Expense', 'Expense', 'Expense'],
        'Amount_In': [450.00, 0.00, 0.00, 0.00, 0.00],
        'Amount_Out': [0.00, 200.00, 500.00, 150.00, 300.00],
        'Event_Link': ['Summer Rooftop Jam', 'Summer Rooftop Jam', 'Summer Rooftop Jam', 'General', 'General']
    })
    
    # Operations demo data
    ops_df = pd.DataFrame({
        'Date': ['2026-05-01', '2026-05-05', '2026-05-10'],
        'Action': ['Event Created', 'Venue Booked', 'Artist Confirmed'],
        'User': ['Admin', 'Admin', 'Admin'],
        'Details': ['Summer Rooftop Jam created', 'Rooftop venue secured', 'DJ Kemet confirmed']
    })
    
    # Snapshot demo data
    snapshot_dict = {
        'quarter': 'Q2 2026',
        'total_revenue': 2450.00,
        'total_expenses': 1800.00,
        'net_profit': 650.00,
        'events_held': 2,
        'total_attendees': 145
    }
    
    return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict
# data_sync.py - CONNECTS GOOGLE SHEETS TO STREAMLIT (UPDATED)
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

# --- CONFIGURATION ---
# Path to your credentials file
creds_path = os.path.join(os.path.dirname(__file__), 'shack_credentials.json')

# Define scopes
SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Load credentials
try:
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPE)
    gc = gspread.authorize(creds)
    print("✅ Google Sheets connected successfully!")
except Exception as e:
    print(f"❌ Authentication error: {e}")
    print("Make sure shack_credentials.json exists in the same folder")
    exit()

# YOUR SPREADSHEET ID
SHEET_ID = '1WBsT69FpseHJKxk4ryDrvyQfvpByc8GUYoEfFaLy0kg'

def load_live_exchange_data():
    """
    Loads all data from Shack Live Exchange Master Google Sheet
    Returns: events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict
    """
    print("🔄 Syncing Live Exchange Data from Google Sheets...")
    try:
        sh = gc.open_by_key(SHEET_ID)
        
        # 1. EVENTS MASTER
        print("  📅 Loading Events Master...")
        ws = sh.worksheet('01_Events_Master')
        events_df = pd.DataFrame(ws.get_all_records())
        if not events_df.empty:
            events_df.columns = events_df.columns.str.strip()
        
        # 2. TICKET BOOKINGS
        print("  🎫 Loading Ticket Bookings...")
        ws = sh.worksheet('02_Ticket_Bookings')
        bookings_df = pd.DataFrame(ws.get_all_records())
        if not bookings_df.empty:
            bookings_df.columns = bookings_df.columns.str.strip().str.replace(' ', '_')
        
        # 3. ARTIST TALENT
        print("  🎤 Loading Artist Talent...")
        ws = sh.worksheet('03_Artist_Talent')
        artists_df = pd.DataFrame(ws.get_all_records())
        if not artists_df.empty:
            artists_df.columns = artists_df.columns.str.strip()
        
        # 4. REVENUE FINANCIALS
        print("  💰 Loading Revenue Financials...")
        ws = sh.worksheet('04_Revenue_Financials')
        financials_df = pd.DataFrame(ws.get_all_records())
        if not financials_df.empty:
            financials_df.columns = financials_df.columns.str.strip()
        
        # 5. OPERATIONS LOG
        print("  📋 Loading Operations Log...")
        ws = sh.worksheet('05_Operations_Log')
        ops_df = pd.DataFrame(ws.get_all_records())
        if not ops_df.empty:
            ops_df.columns = ops_df.columns.str.strip()
        
        # 6. QUARTERLY SNAPSHOT (For Dashboard KPIs)
        print("  📊 Loading Quarterly Snapshot...")
        ws = sh.worksheet('07_Quarterly_Snapshot')
        snapshot_data = ws.get_all_values()
        # Convert to dict for easy access (Metric Name -> Actual Value)
        snapshot_dict = {}
        for row in snapshot_data:
            if len(row) >= 3 and row[0] and row[2]:
                snapshot_dict[row[0].strip()] = row[2].strip()
        
        print("✅ Data Synced Successfully!")
        print(f"   - Events: {len(events_df)} rows")
        print(f"   - Bookings: {len(bookings_df)} rows")
        print(f"   - Artists: {len(artists_df)} rows")
        print(f"   - Financials: {len(financials_df)} rows")
        print(f"   - Operations: {len(ops_df)} rows")
        
        return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict
        
    except Exception as e:
        print(f"❌ Error syncing data: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, None, None

# Test the connection if run directly
if __name__ == "__main__":
    events, bookings, artists, financials, ops, snapshot = load_live_exchange_data()
    
    if events is not None:
        print("\n📊 PREVIEW OF DATA:")
        print("\n--- EVENTS (First 3 rows) ---")
        print(events.head(3))
        print("\n--- BOOKINGS (First 3 rows) ---")
        print(bookings.head(3))
        print("\n--- SNAPSHOT KPIs ---")
        for key, value in list(snapshot.items())[:5]:
            print(f"{key}: {value}")