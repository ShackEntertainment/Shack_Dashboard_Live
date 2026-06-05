# check_sheets.py - Lists all sheets in your spreadsheet
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

CREDENTIALS_PATH = "configs/credentials.json"
SHEET_ID = "1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def check_sheets():
    print("🔐 Authenticating...")
    
    # Load credentials
    creds = None
    if os.path.exists("configs/token.json"):
        creds = Credentials.from_authorized_user_file("configs/token.json", SCOPES)
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
        with open("configs/token.json", 'w') as f:
            f.write(creds.to_json())
    
    # Connect and list sheets
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SHEET_ID)
    
    print(f"\n📊 Spreadsheet Title: {spreadsheet.title}")
    print("\n📋 Available Worksheets:")
    
    worksheets = spreadsheet.worksheets()
    for i, ws in enumerate(worksheets, 1):
        print(f"  {i}. '{ws.title}' ({ws.row_count} rows x {ws.col_count} cols)")
    
    print("\n💡 Copy the EXACT sheet name above and update your data_sync.py")

if __name__ == "__main__":
    check_sheets()