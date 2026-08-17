import sqlite3
import pandas as pd
import os

# --- PATH CONFIGURATION ---
# This script is in the 'dashboards' folder. We need to go up one level to the root.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(ROOT_DIR, 'executive_cache.db')

def get_db_connection():
    if not os.path.exists(DB_NAME):
        return None
    return sqlite3.connect(DB_NAME)

def read_table(table_name):
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
    """Reads the snapshot table and returns it as a dictionary for the KPI cards"""
    conn = get_db_connection()
    if not conn: return {}
    try:
        cursor = conn.cursor()
        # Find the table that matches the prefix and 'snapshot'
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '{prefix}%snapshot%'")
        tables = cursor.fetchall()
        conn.close()
        
        if not tables: return {}
        
        # Read the first matching table
        df = pd.read_sql_query(f"SELECT * FROM {tables[0][0]}", sqlite3.connect(DB_NAME))
        
        # If the table has 'Metric' and 'Value' columns, map them
        if 'Metric' in df.columns and 'Value' in df.columns:
            return dict(zip(df['Metric'], df['Value']))
        
        # Fallback: just return the last row as a dict if it's a single row snapshot
        if not df.empty:
            return df.iloc[-1].to_dict()
            
        return {}
    except Exception:
        return {}

# --- FUNCTIONS MATCHING DASHBOARD EXPECTATIONS ---

def load_live_exchange_data():
    """Returns 7 items: events, bookings, artists, financials, ops, snapshot, error_msg"""
    events = read_table('le_01_events_master')
    bookings = read_table('le_02_ticket_bookings')
    artists = read_table('le_03_artist_talent')
    financials = read_table('le_04_revenue_financials')
    ops = read_table('le_05_operations_log')
    snapshot = get_snapshot_dict('le')
    return events, bookings, artists, financials, ops, snapshot, None

def load_artists_unlimited_data():
    """Returns 6 items: artists, inventory, outlets, sales, partners, error_msg"""
    artists = read_table('au_artists')
    inventory = read_table('au_inventorydata')
    outlets = read_table('au_product_sales_outlets')
    sales = read_table('au_sales')
    partners = read_table('au_partnerships')
    return artists, inventory, outlets, sales, partners, None

def load_news_network_data():
    """Returns 7 items: content, youtube, social, referral, campaign, snapshot, error_msg"""
    content = read_table('sn_01_content_library')
    youtube = read_table('sn_02_youtube_analytics')
    social = read_table('sn_03_social_media_metrics')
    referral = read_table('sn_04_referral_monetization')
    campaign = read_table('sn_05_campaign_tracking')
    snapshot = get_snapshot_dict('sn')
    return content, youtube, social, referral, campaign, snapshot, None

def load_financial_overview_data():
    """Returns 5 items: revenue, expense, cashflow, snapshot, error_msg"""
    revenue = read_table('fin_01_revenue_streams')
    expense = read_table('fin_02_expense_breakdown')
    cashflow = read_table('fin_03_cash_flow')
    snapshot = get_snapshot_dict('fin')
    return revenue, expense, cashflow, snapshot, None

def load_command_data():
    """Returns 5 items: projects, kpi, team, snapshot, error_msg"""
    projects = read_table('cmd_01_project_pipeline')
    kpi = read_table('cmd_02_kpi_tracker')
    team = read_table('cmd_03_team_activity')
    snapshot = get_snapshot_dict('cmd')
    return projects, kpi, team, snapshot, None