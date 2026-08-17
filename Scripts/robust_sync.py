import gspread
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')

CREDENTIALS = os.path.join('configs', 'service_account.json')
DB_PATH = 'executive_cache.db'
SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'

def parse_currency(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace('£', '').replace(',', '').strip())
    except:
        return 0.0

def find_worksheet_by_name(sheet, partial_name):
    """Find worksheet that contains the partial name"""
    for ws in sheet.worksheets():
        if partial_name.lower() in ws.title.lower():
            return ws
    return None

def sync_all_data():
    print("🔄 Starting robust sync...\n")
    
    gc = gspread.service_account(filename=CREDENTIALS)
    sheet = gc.open_by_key(SHEET_ID)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('CREATE TABLE IF NOT EXISTS au_artists (artist_id TEXT, artist_name TEXT, art_type TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS au_products (sku TEXT, artist_name TEXT, product_name TEXT, price REAL, stock_shack INTEGER, stock_direct INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS au_sales (transaction_id TEXT, artist TEXT, sale_date TEXT, quantity INTEGER, total_price REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS au_partnerships (partner_org TEXT, partnership_type TEXT)')
    
    # List all worksheets
    print("Available worksheets:")
    worksheets = sheet.worksheets()
    for i, ws in enumerate(worksheets):
        print(f"  {i+1}. '{ws.title}'")
    print()
    
    # Sync Artists (worksheet #3 based on inspection)
    try:
        ws = find_worksheet_by_name(sheet, 'Artists')
        if ws:
            data = ws.get_all_values()
            if len(data) > 1:
                count = 0
                for row in data[1:]:
                    if len(row) >= 2 and row[1]:  # Has artist name
                        cursor.execute('INSERT OR REPLACE INTO au_artists VALUES (?, ?, ?)',
                                     (row[0], row[1], row[2] if len(row) > 2 else ''))
                        count += 1
                print(f"✅ Synced {count} artists")
        else:
            print("⚠️ Artists worksheet not found")
    except Exception as e:
        print(f"❌ Error syncing artists: {e}")
    
    # Sync Inventory (worksheet #5)
    try:
        ws = find_worksheet_by_name(sheet, 'Inventory')
        if ws:
            data = ws.get_all_values()
            if len(data) > 1:
                count = 0
                for row in data[1:]:
                    if len(row) >= 3 and row[0]:  # Has SKU
                        price = parse_currency(row[6] if len(row) > 6 else 0)
                        stock_shack = int(row[3]) if len(row) > 3 and row[3].isdigit() else 0
                        stock_direct = int(row[4]) if len(row) > 4 and row[4].isdigit() else 0
                        cursor.execute('INSERT OR REPLACE INTO au_products VALUES (?, ?, ?, ?, ?, ?)',
                                     (row[0], row[1], row[2], price, stock_shack, stock_direct))
                        count += 1
                print(f"✅ Synced {count} products")
        else:
            print("⚠️ Inventory worksheet not found")
    except Exception as e:
        print(f" Error syncing inventory: {e}")
    
    # Sync Sales (worksheet #8 - has 💸 emoji)
    try:
        ws = find_worksheet_by_name(sheet, 'Sales')
        if ws:
            data = ws.get_all_values()
            if len(data) > 1:
                count = 0
                for row in data[1:]:
                    if len(row) >= 1 and row[0]:  # Has transaction ID
                        cursor.execute('INSERT OR REPLACE INTO au_sales VALUES (?, ?, ?, ?, ?)',
                                     (row[0], 
                                      row[1] if len(row) > 1 else '',
                                      row[2] if len(row) > 2 else '',
                                      int(row[3]) if len(row) > 3 and row[3].isdigit() else 0,
                                      parse_currency(row[4] if len(row) > 4 else 0)))
                        count += 1
                print(f"✅ Synced {count} sales records")
        else:
            print("️ Sales worksheet not found")
    except Exception as e:
        print(f"❌ Error syncing sales: {e}")
    
    # Sync Partnerships (worksheet #10 - has  emoji)
    try:
        ws = find_worksheet_by_name(sheet, 'Partnerships')
        if ws:
            data = ws.get_all_values()
            if len(data) > 1:
                count = 0
                for row in data[1:]:
                    if len(row) >= 2 and row[1]:  # Has partner org
                        cursor.execute('INSERT OR REPLACE INTO au_partnerships VALUES (?, ?)',
                                     (row[1], row[2] if len(row) > 2 else ''))
                        count += 1
                print(f"✅ Synced {count} partnerships")
        else:
            print("️ Partnerships worksheet not found")
    except Exception as e:
        print(f"❌ Error syncing partnerships: {e}")
    
    conn.commit()
    
    # Summary
    print("\n📊 SYNC SUMMARY:")
    for table, name in [('au_artists', 'Artists'), ('au_products', 'Products'), 
                        ('au_sales', 'Sales'), ('au_partnerships', 'Partnerships')]:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"  • {name}: {count} records")
    
    conn.close()
    print("\n✅ Sync complete!")

if __name__ == "__main__":
    sync_all_data()