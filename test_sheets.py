import gspread
import os
from dotenv import load_dotenv

# Load config
load_dotenv('configs/.env')
CREDENTIALS = 'configs/service_account.json'

# We will try to open by TITLE instead of ID to rule out ID typos
SHEET_TITLE = "Artists_Unlimited_Master"

print(f"Trying to connect to sheet by TITLE: '{SHEET_TITLE}'")

try:
    gc = gspread.service_account(filename=CREDENTIALS)
    
    # Try opening by Title
    sheet = gc.open(SHEET_TITLE)
    
    print("✅ SUCCESS! Connected to:", sheet.title)
    print(" Actual Sheet ID is:", sheet.id)
    print("Tabs found:", [w.title for w in sheet.worksheets()])
    
    # If this works, copy the ID printed above and update your .env file!
    
except Exception as e:
    print("❌ FAILED:", e)