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