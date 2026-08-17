import gspread
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')
CREDENTIALS = os.path.join('configs', 'service_account.json')
SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'

gc = gspread.service_account(filename=CREDENTIALS)
sheet = gc.open_by_key(SHEET_ID)

print("Debugging @Artists and 💸 Sales tabs...\n")

# Try @Artists
try:
    print("1. Trying to access '@Artists'...")
    ws = sheet.worksheet('@Artists')
    data = ws.get_all_values()
    print(f"   ✅ Accessed successfully!")
    print(f"   Total rows: {len(data)}")
    if len(data) > 0:
        print(f"   Headers: {data[0]}")
    if len(data) > 1:
        print(f"   First data row: {data[1]}")
except Exception as e:
    print(f"    Error: {e}")

print()

# Try 💸 Sales
try:
    print("2. Trying to access '💸 Sales'...")
    ws = sheet.worksheet('💸 Sales')
    data = ws.get_all_values()
    print(f"   ✅ Accessed successfully!")
    print(f"   Total rows: {len(data)}")
    if len(data) > 0:
        print(f"   Headers: {data[0]}")
    if len(data) > 1:
        print(f"   First data row: {data[1]}")
except Exception as e:
    print(f"   ❌ Error: {e}")