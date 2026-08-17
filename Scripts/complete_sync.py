import gspread
import sqlite3
import os
from google.oauth2.service_account import Credentials
from datetime import datetime

# ============================================================================
# [HARDENING] ROBUST PATH RESOLUTION
# Works no matter which folder the script is launched from.
# Writes to Scripts\executive_cache.db — same location the bot reads.
# ============================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

SERVICE_ACCOUNT_FILE = os.path.join(project_root, 'configs', 'service_account.json')
DB_PATH = os.path.join(script_dir, 'executive_cache.db')

# Your Google Sheet IDs
AU_SHEET_ID = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'
LE_SHEET_ID = '1WBsT69FpseHJKxk4ryDrvyQfvpByc8GUYoEfFaLy0kg'
SN_SHEET_ID = '1qJ_SdA1RYEmI-dEdhKzPa0ze-DC5KEkJyqXuZVjtnoI'
FIN_SHEET_ID = '1nXxNoWAWMLgDUKUEYn7qkcKaxgzEI-sCLaK2hNpzO3A'

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_gspread_client():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def get_db():
    return sqlite3.connect(DB_PATH)

def safe_float(val, default=0.0):
    if val is None: return default
    try: return float(str(val).replace('£', '').replace(',', '').strip())
    except: return default

def safe_int(val, default=0):
    if val is None: return default
    try: return int(float(str(val).replace(',', '').strip()))
    except: return default

# ============================================================================
# SYNC FUNCTIONS
# ============================================================================

def sync_artists_unlimited(sh):
    print("🎨 Syncing Artists Unlimited...")
    conn = get_db()
    cursor = conn.cursor()
    try:
        worksheet = sh.worksheet("InventoryData")
        records = worksheet.get_all_records()
        cursor.execute("DELETE FROM au_products")

        for row in records:
            if row.get('SKU'):
                cursor.execute('''INSERT OR REPLACE INTO au_products
                    (product_id, product_name, retail_price, current_stock, units_sold, artist_name)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (str(row['SKU']), row.get('Product Name', ''),
                     safe_float(row.get('Retail Price (£)')),
                     safe_int(row.get('Current Stock')),
                     safe_int(row.get('Units Sold')),
                     row.get('Artist Name', 'Unknown')))
        print(f"   ✅ Synced {len(records)} AU products")
    except Exception as e:
        print(f"   ❌ AU Sync error: {e}")
    finally:
        conn.commit()
        conn.close()

def sync_live_exchange(sh):
    print("🎫 Syncing Live Exchange...")
    conn = get_db()
    cursor = conn.cursor()

    # Based on your error log, the correct tab is '01_Events_Master'
    tab_name = "01_Events_Master"
    try:
        worksheet = sh.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        print(f"   ⚠️ '{tab_name}' not found. Trying '02_Ticket_Bookings'...")
        try:
            worksheet = sh.worksheet("02_Ticket_Bookings")
            tab_name = "02_Ticket_Bookings"
        except:
            print(f"   ❌ Could not find events tab. Available: {[w.title for w in sh.worksheets()]}")
            conn.close()
            return

    print(f"   ✅ Using tab: '{tab_name}'")

    try:
        records = worksheet.get_all_records()
        cursor.execute("DELETE FROM le_events")

        for row in records:
            if row.get('Event_ID'):
                # Map only the columns that exist in your le_events database table
                cursor.execute('''INSERT OR REPLACE INTO le_events
                    (event_id, event_name, event_type, venue_name, venue_address, event_date, capacity_total, tickets_sold, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (str(row.get('Event_ID', '')),
                     row.get('Event_Name', ''),
                     row.get('Event_Type', ''),
                     row.get('Venue_Name', ''),
                     row.get('Venue_Address', ''),
                     row.get('Event_Date', ''),
                     safe_int(row.get('Capacity_Total')),
                     safe_int(row.get('Tickets_Sold')),
                     row.get('Status', 'Planned')))
        print(f"   ✅ Synced {len(records)} LE events")
    except Exception as e:
        print(f"   ❌ LE Sync error: {e}")
    finally:
        conn.commit()
        conn.close()

def sync_news_network(sh):
    print("📰 Syncing Shack News Network...")
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Based on your screenshot, the tab is '01_Content_Library'
        worksheet = sh.worksheet("01_Content_Library")
        records = worksheet.get_all_records()
        cursor.execute("DELETE FROM sn_content")

        for row in records:
            if row.get('Content_ID'):
                cursor.execute('''INSERT OR REPLACE INTO sn_content
                    (content_id, title, type, author, publish_date, status, url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (str(row['Content_ID']), row.get('Title', ''),
                     row.get('Type', ''), row.get('Author', ''),
                     row.get('Publish_Date', ''), row.get('Status', 'Draft'),
                     row.get('URL', '')))
        print(f"   ✅ Synced {len(records)} News articles")
    except Exception as e:
        print(f"   ❌ News Sync error: {e}")
    finally:
        conn.commit()
        conn.close()

def sync_financial_overview(sh):
    print("💰 Syncing Financial Overview...")
    conn = get_db()
    cursor = conn.cursor()

    # 1. Revenue
    try:
        worksheet = sh.worksheet("01_Revenue_Streams")
        records = worksheet.get_all_records()
        cursor.execute("DELETE FROM finance_revenue")

        count = 0
        for row in records:
            if row.get('Revenue_ID'):
                cursor.execute('''INSERT OR REPLACE INTO finance_revenue
                    (revenue_id, platform, category, amount, date, status)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (str(row['Revenue_ID']), row.get('Platform', ''),
                     row.get('Category', ''), safe_float(row.get('Amount')),
                     row.get('Date', ''), row.get('Status', '')))
                count += 1
        print(f"   ✅ Synced {count} Revenue records")
    except Exception as e:
        print(f"   ❌ Revenue Sync error: {e}")

    # 2. Expenses
    try:
        worksheet = sh.worksheet("02_Expense_Breakdown")
        records = worksheet.get_all_records()
        cursor.execute("DELETE FROM finance_expenses")

        count = 0
        for row in records:
            desc = row.get('Description', row.get('description', row.get('Category', '')))
            if desc:
                exp_id = row.get('expense_id', f"EXP-{count}")
                cursor.execute('''INSERT OR REPLACE INTO finance_expenses
                    (expense_id, category, amount, expense_date, description, status)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (str(exp_id), row.get('Category', 'General'),
                     safe_float(row.get('Amount')), row.get('Date', ''),
                     desc, 'Recorded'))
                count += 1
        print(f"   ✅ Synced {count} Expense records")
    except Exception as e:
        print(f"   ❌ Expense Sync error: {e}")

    conn.commit()
    conn.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("="*60)
    print("🔄 SHACK ENTERTAINMENT - MASTER DATA SYNC")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Service account: {SERVICE_ACCOUNT_FILE}")
    print(f"Writing to DB:    {DB_PATH}")
    print("="*60)

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ Error: Service account file not found at {SERVICE_ACCOUNT_FILE}")
        return

    try:
        gc = get_gspread_client()
        print("✅ Connected to Google API")

        # 1. Artists Unlimited
        try:
            sh_au = gc.open_by_key(AU_SHEET_ID)
            print(f"✅ Opened AU Sheet: {sh_au.title}")
            sync_artists_unlimited(sh_au)
        except Exception as e:
            print(f"❌ AU Sheet Error: {e}")

        # 2. Live Exchange
        try:
            sh_le = gc.open_by_key(LE_SHEET_ID)
            print(f"✅ Opened LE Sheet: {sh_le.title}")
            sync_live_exchange(sh_le)
        except Exception as e:
            print(f"❌ LE Sheet Error: {e}")

        # 3. News Network
        try:
            sh_sn = gc.open_by_key(SN_SHEET_ID)
            print(f"✅ Opened SN Sheet: {sh_sn.title}")
            sync_news_network(sh_sn)
        except Exception as e:
            print(f"❌ SN Sheet Error: {e}")

        # 4. Financial Overview
        try:
            sh_fin = gc.open_by_key(FIN_SHEET_ID)
            print(f"✅ Opened FIN Sheet: {sh_fin.title}")
            sync_financial_overview(sh_fin)
        except Exception as e:
            print(f"❌ FIN Sheet Error: {e}")

        print("\n" + "="*60)
        print("✅ MASTER SYNC COMPLETED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ CRITICAL API ERROR: {e}")

if __name__ == "__main__":
    main()