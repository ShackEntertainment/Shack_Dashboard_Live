import sqlite3
import pandas as pd
import os

DB_NAME = 'executive_cache.db'

def get_db_connection():
    """Get connection to SQLite database"""
    if not os.path.exists(DB_NAME):
        return None
    return sqlite3.connect(DB_NAME)

def read_table(table_name):
    """Read data from a specific table"""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df
    except Exception:
        conn.close()
        return pd.DataFrame()

def get_snapshot_dict(prefix):
    """Get snapshot data as dictionary"""
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{prefix}%Snapshot%'")
        tables = cursor.fetchall()
        conn.close()
        if not tables:
            return {}
        
        df = pd.read_sql_query(f"SELECT * FROM {tables[0][0]}", sqlite3.connect(DB_NAME))
        if len(df.columns) >= 2:
            return dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
        return {}
    except Exception:
        return {}

# --- FUNCTIONS FOR DASHBOARDS ---

def load_live_exchange_data():
    """Load Live Exchange data from cache"""
    events = read_table('le_01_Events_Master')
    bookings = read_table('le_02_Ticket_Bookings')
    artists = read_table('le_03_Artist_Talent')
    financials = read_table('le_04_Revenue_Financials')
    ops = read_table('le_05_Operations_Log')
    snapshot = get_snapshot_dict('le')
    return events, bookings, artists, financials, ops, snapshot, None

def load_artists_unlimited_data():
    """Load Artists Unlimited data from cache"""
    artists = read_table('au_Artists')
    inventory = read_table('au_InventoryData')
    outlets = read_table('au_Product_Sales_Outlets')
    sales = read_table('au_Sales')
    partners = read_table('au_Partnerships')
    return artists, inventory, outlets, sales, partners, None

def load_news_network_data():
    """Load News Network data from cache"""
    content = read_table('sn_01_Content_Library')
    youtube = read_table('sn_02_Youtube_Analytics')
    social = read_table('sn_03_Social_Media_Metrics')
    referral = read_table('sn_04_Referral_Monetization')
    campaign = read_table('sn_05_Campaign_Tracking')
    snapshot = get_snapshot_dict('sn')
    return content, youtube, social, referral, campaign, snapshot, None

def load_financial_overview_data():
    """Load Financial Overview data from cache"""
    revenue = read_table('fin_01_Revenue_Streams')
    expense = read_table('fin_02_Expense_Breakdown')
    cashflow = read_table('fin_03_Cash_Flow')
    snapshot = get_snapshot_dict('fin')
    return revenue, expense, cashflow, snapshot, None

def load_command_data():
    """Load Command Center data from cache"""
    projects = read_table('cmd_01_Project_Pipeline')
    kpi = read_table('cmd_02_KPI_Tracker')
    team = read_table('cmd_03_Team_Activity')
    snapshot = get_snapshot_dict('cmd')
    return projects, kpi, team, snapshot, None