import gspread
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('configs/.env')

# Path to your service account credentials
# Adjust this path if your service_account.json is located elsewhere
CREDENTIALS = os.path.join('configs', 'service_account.json')

# Artists Unlimited Master Sheet ID
SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'

def main():
    print("Connecting to Google Sheets...")
    try:
        gc = gspread.service_account(filename=CREDENTIALS)
        sheet = gc.open_by_key(SHEET_ID)
        print("✅ Connected successfully!\n")

        # List all tabs (worksheets)
        print("Available Tabs in Artists Unlimited Master:")
        print("-" * 40)
        for i, worksheet in enumerate(sheet.worksheets()):
            print(f"{i+1}. {worksheet.title}")
            
            # Show first 3 rows of each tab to understand structure
            print(f"   (Preview: {worksheet.get('A1:C3')})")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check if 'configs/service_account.json' exists and has access to the sheet.")

if __name__ == "__main__":
    main()