import gspread
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')
CREDENTIALS = os.path.join('configs', 'service_account.json')

gc = gspread.service_account(filename=CREDENTIALS)

# Try to open each sheet by ID
sheets_to_check = {
    'financial': '1nXxNoWAWMLgDUKUEYn7qkcKaxgzEI-sCLaK2hNpz03A',
    'live_ex': '1WBsT69FpseHJKxk4ryDrvyQfvpByc8GUYoEffaLy0kg',
    'news': '1qJ_SdA1RYEmI-dEdhKzPaOze-DC5KEkJyqXuZVjtnoI',
    'command': '1y2uV-cPiuDT6EJHlkny-wF1mTK76-_I8jDAnqcCZw_U',
    'artists': '1XuiEI9HF2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOP1YE'
}

for name, sheet_id in sheets_to_check.items():
    try:
        sheet = gc.open_by_key(sheet_id)
        print(f"✅ {name}: ACCESSIBLE")
        print(f"   Title: {sheet.title}")
        print(f"   Tabs: {[ws.title for ws in sheet.worksheets()]}")
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
    print()