import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import sqlite3
import schedule
import time
import os
import logging
from datetime import datetime

# --- CONFIGURATION ---
# Path to your service account (one folder up, inside configs)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(ROOT_DIR, 'configs', 'service_account.json')
DB_NAME = os.path.join(ROOT_DIR, 'executive_cache.db')

# Define the exact Sheet Names and Tab Names based on your uploaded files
SHEET_CONFIG = {
    'Shack_Live_Exchange_Master': {
        'tabs': {
            'le_events': '01_Events_Master',
            'le_bookings': '02_Ticket_Bookings',
            'le_artists': '03_Artist_Talent',
            'le_financials': '04_Revenue_Financials',
            'le_ops': '05_Operations_Log'
        }
    },
    'Artists_Unlimited_Master': {
        'tabs': {
            'au_artists': 'Artists',
            'au_inventory': 'InventoryData',
            'au_outlets': ' Product Sales Outlets',
            'au_sales': '💰 Sales',
            'au_partners': '🤝 Partnerships'
        }
    },
    'Shack_News_Network_Master': {
        'tabs': {
            'sn_content': '01_Content_Library',
            'sn_youtube': '02_Youtube_Analytics',
            'sn_social': '03_Social_Media_Metrics',
            'sn_referral': '04_Referral_Monetization',
            'sn_campaign': '05_Campaign_Tracking',
            'sn_snapshot': '06_Snapshot'
        }
    },
    'Shack_Financial_Overview_Master': {
        'tabs': {
            'fin_revenue': '01_Revenue_Streams',
            'fin_expense': '02_Expense_Breakdown',
            'fin_cashflow': '03_Cash_Flow',
            'fin_snapshot': '04_Snapshot'
        }
    },
    'Shack_Command_Center_Master': {
        'tabs': {
            'cmd_projects': '01_Project_Pipeline',
            'cmd_kpi': '02_KPI_Tracker',
            'cmd_team': '03_Team_Activity',
            'cmd_snapshot': '04_Snapshot'
        }
    }
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_google_client():
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        return gspread.authorize(creds)
    except Exception as e:
        logging.error(f"Auth failed: {e}")
        return None

def sync_all_sheets():
    logging.info("--- 🔄 STARTING SYNC ---")
    client = get_google_client()
    if not client:
        logging.error("Failed to connect. Skipping.")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        logging.info(f"Connected to local cache: {DB_NAME}")
        
        for sheet_name, config in SHEET_CONFIG.items():
            try:
                spreadsheet = client.open(sheet_name)
                for table_name, tab_name in config['tabs'].items():
                    try:
                        worksheet = spreadsheet.worksheet(tab_name)
                        records = worksheet.get_all_records()
                        df = pd.DataFrame(records)
                        
                        # Clean column names (remove spaces and special chars)
                        df.columns = [str(c).strip().replace(' ', '_').replace('(', '').replace(')', '').replace('£', 'GBP').replace('%', 'Percent') for c in df.columns]
                        
                        # Write to SQLite (replace table to keep it fresh)
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        logging.info(f"✅ Synced: {sheet_name} -> {tab_name} ({len(df)} rows)")
                    except gspread.exceptions.WorksheetNotFound:
                        logging.warning(f"⚠️ Tab not found: {tab_name}")
            except gspread.exceptions.SpreadsheetNotFound:
                logging.error(f"❌ Sheet not found: {sheet_name}. Check sharing permissions.")
        
        conn.close()
        logging.info("--- ✅ SYNC COMPLETE ---")
    except Exception as e:
        logging.error(f"Critical error: {e}")

def main():
    logging.info("🏰 Shack Data Sync Agent Starting...")
    sync_all_sheets() # Run immediately
    schedule.every(5).minutes.do(sync_all_sheets) # Then every 5 mins
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()