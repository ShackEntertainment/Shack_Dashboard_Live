# agents/data_sync.py - FINAL WORKING VERSION
import pandas as pd
import sqlite3
import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SHEET_ID = "1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE"
WORKSHEET_INDEX = 2
DB_PATH = "agents/executive_cache.db"
CREDENTIALS_PATH = "configs/credentials.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def sync_data():
    print("🔄 Starting Sync Agent...")
    
    try:
        # Authenticate
        creds = None
        if os.path.exists("configs/token.json"):
            creds = Credentials.from_authorized_user_file("configs/token.json", SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                print("🔐 Opening browser for authentication...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            os.makedirs("configs", exist_ok=True)
            with open("configs/token.json", 'w') as f:
                f.write(creds.to_json())
        
        # Connect to Sheets
        print("📊 Connecting to Google Sheets...")
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        
        # Get worksheet by index
        print(f"📂 Accessing worksheet index {WORKSHEET_INDEX}...")
        worksheets = spreadsheet.worksheets()
        worksheet = worksheets[WORKSHEET_INDEX]
        
        print(f"📋 Worksheet: '{worksheet.title}'")
        print(f"📏 Sheet dimensions: {worksheet.row_count} rows x {worksheet.col_count} cols")
        
        # Get all records (this is the most reliable method)
        print("📥 Fetching all records...")
        all_records = worksheet.get_all_records()
        
        if not all_records:
            print("⚠️ No data found in sheet")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(all_records)
        
        if df.empty:
            print("⚠️ No data rows found")
            return
        
        # Clean column names
        df.columns = [col.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_") for col in df.columns]
        
        # Save to SQLite
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("artists_cache", conn, if_exists="replace", index=False)
        conn.close()
        
        print(f"✅ Success! Synced {len(df)} rows to {DB_PATH}")
        print(f"📊 Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_data()