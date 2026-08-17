import gspread
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')
CREDENTIALS = os.path.join('configs', 'service_account.json')
SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'

gc = gspread.service_account(filename=CREDENTIALS)
sheet = gc.open_by_key(SHEET_ID)

print("Exact worksheet names in Artists Unlimited Master:")
print("=" * 60)
for i, ws in enumerate(sheet.worksheets()):
    print(f"{i+1}. '{ws.title}' (type: {type(ws.title)})")
    # Show first cell to verify access
    try:
        first_cell = ws.acell('A1')
        print(f"   A1 contains: '{first_cell.value}'")
    except Exception as e:
        print(f"   Error reading A1: {e}")
    print()