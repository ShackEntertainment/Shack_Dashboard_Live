import gspread
from google.oauth2.service_account import Credentials

# Use the same scopes as your main script
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_service_account_file('configs/service_account.json', scopes=SCOPES)
gc = gspread.authorize(creds)

print("🔍 Searching for 'Shack_News_Network_Master'...")

try:
    # Try to open by exact title
    sh = gc.open('Shack_News_Network_Master')
    print("✅ SUCCESS! Found the sheet.")
    print("👉 The Correct ID is:", sh.id)
    print("\nPlease copy this ID and replace the SN_SHEET_ID in your complete_sync.py file.")
    
except gspread.SpreadsheetNotFound:
    print("❌ Could not find a sheet with that exact name.")
    print("\nHere are all the sheets your Service Account can currently see:")
    for s in gc.list_spreadsheet_files():
        print(f" - {s['name']}  (ID: {s['id']})")