import gspread
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')
CREDENTIALS = os.path.join('configs', 'service_account.json')

def diagnose_all_sheets():
    print("🔍 DIAGNOSING ALL GOOGLE SHEETS...\n")
    print("="*60)
    
    gc = gspread.service_account(filename=CREDENTIALS)
    
    # List all spreadsheets
    print("📂 ALL SPREADSHEETS IN YOUR DRIVE:\n")
    spreadsheets = gc.openall()
    
    for i, spreadsheet in enumerate(spreadsheets, 1):
        print(f"{i}. {spreadsheet.title}")
        print(f"   Sheet ID: {spreadsheet.id}")
        print(f"   URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit\n")
        
        # Show tabs
        print("   Tabs:")
        for ws in spreadsheet.worksheets():
            print(f"     • {ws.title}")
        print("-"*60)
    
    print("\n✅ DIAGNOSIS COMPLETE!")
    print("\nCopy these Sheet IDs for the sync script:")
    print("-" * 60)
    for spreadsheet in spreadsheets:
        print(f"{spreadsheet.title}: `{spreadsheet.id}`")

if __name__ == "__main__":
    diagnose_all_sheets()