import gspread
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')
CREDENTIALS = os.path.join('configs', 'service_account.json')
SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'

gc = gspread.service_account(filename=CREDENTIALS)
sheet = gc.open_by_key(SHEET_ID)

print("=== INVENTORY DATA TAB - FULL STRUCTURE ===\n")
ws = sheet.worksheet('InventoryData')
data = ws.get_all_values()

print(f"Total rows: {len(data)}\n")

# Show headers
if data:
    print("HEADERS (Row 1):")
    for i, header in enumerate(data[0]):
        print(f"  Column {i}: '{header}'")
    
    print("\n\nFIRST 3 DATA ROWS:")
    for row_num, row in enumerate(data[1:4], 2):
        print(f"\nRow {row_num}:")
        for i, value in enumerate(row):
            print(f"  Col {i}: {value}")

print("\n\n=== SALES TAB - FULL STRUCTURE ===\n")
try:
    ws_sales = sheet.worksheet('💸 Sales')
    data_sales = ws_sales.get_all_values()
    
    print(f"Total rows: {len(data_sales)}\n")
    
    if data_sales:
        print("HEADERS (Row 1):")
        for i, header in enumerate(data_sales[0]):
            print(f"  Column {i}: '{header}'")
        
        print("\n\nFIRST 3 DATA ROWS:")
        for row_num, row in enumerate(data_sales[1:4], 2):
            print(f"\nRow {row_num}:")
            for i, value in enumerate(row):
                print(f"  Col {i}: {value}")
except Exception as e:
    print(f"Error accessing Sales tab: {e}")