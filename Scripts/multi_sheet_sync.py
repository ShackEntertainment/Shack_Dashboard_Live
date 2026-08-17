import gspread
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('configs/.env')

# Configuration
CREDENTIALS = os.path.join('configs', 'service_account.json')
DB_PATH = 'executive_cache.db'
ARTISTS_UNLIMITED_SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'

def parse_currency(value):
    """Convert text currency like '£170.00' or '45' to float"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        clean_value = str(value).replace('£', '').replace(',', '').strip()
        return float(clean_value)
    except:
        return 0.0

def safe_get(row, index, default=''):
    """Safely get a value from a row list"""
    try:
        return row[index] if row[index] else default
    except IndexError:
        return default

def connect_to_sheets():
    print("Connecting to Google Sheets...")
    gc = gspread.service_account(filename=CREDENTIALS)
    print("✅ Connected to Google Sheets")
    return gc

def connect_to_db():
    conn = sqlite3.connect(DB_PATH)
    print(f"✅ Connected to database: {DB_PATH}")
    return conn

def init_db_tables(conn):
    """Create tables if they don't exist"""
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS au_artists (
            artist_id TEXT PRIMARY KEY,
            artist_name TEXT,
            art_type TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS au_products (
            sku TEXT PRIMARY KEY,
            artist_name TEXT,
            product_name TEXT,
            price REAL,
            stock_shack INTEGER,
            stock_direct INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS au_sales (
            transaction_id TEXT PRIMARY KEY,
            artist TEXT,
            sale_date TEXT,
            quantity INTEGER,
            total_price REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS au_partnerships (
            partner_org TEXT PRIMARY KEY,
            partnership_type TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS au_form_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sale_type TEXT,
            sku TEXT
        )
    ''')
    
    conn.commit()
    print("✅ Database tables initialized")

def sync_artists_unlimited(gc, conn):
    print("\n" + "="*50)
    print("Syncing Artists Unlimited Master Sheet...")
    print("="*50)
    
    sheet = gc.open_by_key(ARTISTS_UNLIMITED_SHEET_ID)
    cursor = conn.cursor()
    
    # List all worksheets to see what's available
    worksheets = sheet.worksheets()
    print("\nAvailable worksheets:")
    for ws in worksheets:
        print(f"  • '{ws.title}'")
    print()

    # --- 1. Sync @Artists Tab ---
    try:
        ws = sheet.worksheet('@Artists')
        data = ws.get_all_values()
        if len(data) > 1:
            count = 0
            for row in data[1:]:
                artist_id = safe_get(row, 0)
                artist_name = safe_get(row, 1)
                art_type = safe_get(row, 2)
                if artist_name:
                    cursor.execute('''
                        INSERT OR REPLACE INTO au_artists (artist_id, artist_name, art_type)
                        VALUES (?, ?, ?)
                    ''', (artist_id, artist_name, art_type))
                    count += 1
            print(f"✅ Synced {count} artists from '@Artists'")
    except Exception as e:
        print(f"️ Error syncing @Artists: {e}")

    # --- 2. Sync InventoryData Tab ---
    try:
        ws = sheet.worksheet('InventoryData')
        data = ws.get_all_values()
        if len(data) > 1:
            count = 0
            for row in data[1:]:
                sku = safe_get(row, 0)
                artist_name = safe_get(row, 1)
                product_name = safe_get(row, 2)
                price = parse_currency(safe_get(row, 6))
                stock_shack = int(safe_get(row, 3, 0)) if safe_get(row, 3, '0').isdigit() else 0
                stock_direct = int(safe_get(row, 4, 0)) if safe_get(row, 4, '0').isdigit() else 0

                if sku:
                    cursor.execute('''
                        INSERT OR REPLACE INTO au_products 
                        (sku, artist_name, product_name, price, stock_shack, stock_direct)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (sku, artist_name, product_name, price, stock_shack, stock_direct))
                    count += 1
            print(f"✅ Synced {count} products from 'InventoryData'")
    except Exception as e:
        print(f"⚠️ Error syncing InventoryData: {e}")

    # --- 3. Sync 💸 Sales Tab ---
    try:
        ws = sheet.worksheet('💸 Sales')
        data = ws.get_all_values()
        if len(data) > 1:
            count = 0
            for row in data[1:]:
                txn_id = safe_get(row, 0)
                artist = safe_get(row, 1)
                sale_date = safe_get(row, 2)
                quantity = int(safe_get(row, 3, 0)) if safe_get(row, 3, '0').isdigit() else 0
                total_price = parse_currency(safe_get(row, 4))

                if txn_id:
                    cursor.execute('''
                        INSERT OR REPLACE INTO au_sales 
                        (transaction_id, artist, sale_date, quantity, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (txn_id, artist, sale_date, quantity, total_price))
                    count += 1
            print(f"✅ Synced {count} records from '💸 Sales'")
    except Exception as e:
        print(f"⚠️ Error syncing 💸 Sales: {e}")

    # --- 4. Sync 🤝 Partnerships Tab ---
    try:
        ws = sheet.worksheet('🤝 Partnerships')
        data = ws.get_all_values()
        if len(data) > 1:
            count = 0
            for row in data[1:]:
                partner_org = safe_get(row, 1)
                partnership_type = safe_get(row, 2)

                if partner_org:
                    cursor.execute('''
                        INSERT OR REPLACE INTO au_partnerships (partner_org, partnership_type)
                        VALUES (?, ?)
                    ''', (partner_org, partnership_type))
                    count += 1
            print(f"✅ Synced {count} partnerships from '🤝 Partnerships'")
    except Exception as e:
        print(f"️ Error syncing 🤝 Partnerships: {e}")

    # --- 5. Sync Form responses 1 Tab ---
    try:
        ws = sheet.worksheet('Form responses 1')
        data = ws.get_all_values()
        if len(data) > 1:
            count = 0
            for row in data[1:]:
                timestamp = safe_get(row, 0)
                sale_type = safe_get(row, 1).strip()
                sku = safe_get(row, 2)

                if timestamp and sku:
                    cursor.execute('''
                        INSERT INTO au_form_sales (timestamp, sale_type, sku)
                        VALUES (?, ?, ?)
                    ''', (timestamp, sale_type, sku))
                    count += 1
            print(f"✅ Synced {count} form responses from 'Form responses 1'")
    except Exception as e:
        print(f"⚠️ Error syncing Form responses: {e}")

    conn.commit()

def print_summary(conn):
    print("\n" + "="*50)
    print("SYNC SUMMARY")
    print("="*50)
    cursor = conn.cursor()
    
    tables_to_check = [
        ('au_artists', 'Artists'),
        ('au_products', 'Products/Inventory'),
        ('au_sales', 'Sales Records'),
        ('au_partnerships', 'Partnerships'),
        ('au_form_sales', 'Form Sales Logger')
    ]
    
    for table, name in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  • {name}: {count} records")
        except Exception:
            print(f"  • {name}: Table not found or empty")

def main():
    print("🔄 Starting Multi-Sheet Sync...")
    try:
        gc = connect_to_sheets()
        conn = connect_to_db()
        
        init_db_tables(conn)
        sync_artists_unlimited(gc, conn)
        print_summary(conn)
        
        conn.close()
        print("\n Sync completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()