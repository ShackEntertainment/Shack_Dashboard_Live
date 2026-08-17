import gspread
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')

CREDENTIALS = os.path.join('configs', 'service_account.json')
DB_PATH = 'executive_cache.db'

def parse_currency(value):
    if value is None: return 0.0
    if isinstance(value, (int, float)): return float(value)
    try: return float(str(value).replace('£', '').replace(',', '').strip())
    except: return 0.0

def safe_get(row, index, default=''):
    try: return row[index] if row[index] else default
    except IndexError: return default

def main():
    print("🔧 FIXING DATABASE SCHEMA & RESYNCING...\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Drop the old table
    print("Dropping old au_products table...")
    cursor.execute("DROP TABLE IF EXISTS au_products")
    
    # 2. Recreate table WITH barcode column to match the sheet
    print("Creating new au_products table with correct columns...")
    cursor.execute('''CREATE TABLE au_products (
        sku TEXT PRIMARY KEY, 
        artist_name TEXT, 
        product_name TEXT, 
        barcode TEXT, 
        category TEXT, 
        cost_price REAL, 
        retail_price REAL, 
        initial_stock INTEGER, 
        units_sold INTEGER, 
        current_stock INTEGER, 
        location TEXT, 
        status TEXT
    )''')
    conn.commit()
    print("✅ Schema fixed.\n")
    
    # 3. Sync the data
    print(" Syncing Artists Unlimited Master...")
    gc = gspread.service_account(filename=CREDENTIALS)
    all_sheets = gc.openall()
    sheet_dict = {sheet.title: sheet for sheet in all_sheets}
    
    if 'Artists_Unlimited_Master' in sheet_dict:
        sheet = sheet_dict['Artists_Unlimited_Master']
        ws = sheet.worksheet('InventoryData')
        data = ws.get_all_values()
        
        if len(data) > 1:
            count = 0
            # Define the 12 columns exactly as they appear in the sheet
            columns = ['sku', 'artist_name', 'product_name', 'barcode', 'category', 'cost_price', 'retail_price', 'initial_stock', 'units_sold', 'current_stock', 'location', 'status']
            
            for row in data[1:]:
                values = []
                for i in range(len(columns)):
                    val = safe_get(row, i)
                    # Auto-convert prices and stocks
                    if columns[i] in ['cost_price', 'retail_price']:
                        values.append(parse_currency(val))
                    elif columns[i] in ['initial_stock', 'units_sold', 'current_stock']:
                        values.append(int(val) if str(val).isdigit() else 0)
                    else:
                        values.append(val)
                
                placeholders = ','.join(['?'] * len(columns))
                cursor.execute(f"INSERT INTO au_products ({','.join(columns)}) VALUES ({placeholders})", values)
                count += 1
            
            print(f"✅ Synced {count} products with correct prices!")
    
    conn.commit()
    
    # 4. Verify
    print("\n=== VERIFICATION ===")
    cursor.execute("SELECT product_name, retail_price, current_stock FROM au_products")
    rows = cursor.fetchall()
    for row in rows:
        print(f"• {row[0]}: £{row[1]:,.2f} (Stock: {row[2]})")
        
    conn.close()
    print("\n✅ COMPLETE!")

if __name__ == "__main__":
    main()