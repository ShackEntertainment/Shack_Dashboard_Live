import sqlite3
import os

DB_PATH = 'executive_cache.db'

def fix_database_schema():
    print("🔧 Fixing database schema...\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing table and recreate with correct schema
    print("Dropping old au_products table...")
    cursor.execute('DROP TABLE IF EXISTS au_products')
    
    print("Creating new au_products table with correct schema...")
    cursor.execute('''
        CREATE TABLE au_products (
            sku TEXT PRIMARY KEY,
            artist_name TEXT,
            product_name TEXT,
            category TEXT,
            cost_price REAL,
            retail_price REAL,
            initial_stock INTEGER,
            units_sold INTEGER,
            current_stock INTEGER,
            location TEXT,
            status TEXT
        )
    ''')
    
    # Also fix au_sales table
    print("Dropping old au_sales table...")
    cursor.execute('DROP TABLE IF EXISTS au_sales')
    
    print("Creating new au_sales table...")
    cursor.execute('''
        CREATE TABLE au_sales (
            transaction_id TEXT PRIMARY KEY,
            artist TEXT,
            sale_date TEXT,
            quantity INTEGER,
            total_price REAL
        )
    ''')
    
    # Fix au_partnerships
    print("Dropping old au_partnerships table...")
    cursor.execute('DROP TABLE IF EXISTS au_partnerships')
    
    print("Creating new au_partnerships table...")
    cursor.execute('''
        CREATE TABLE au_partnerships (
            partner_org TEXT PRIMARY KEY,
            partnership_type TEXT
        )
    ''')
    
    # Fix au_artists
    print("Dropping old au_artists table...")
    cursor.execute('DROP TABLE IF EXISTS au_artists')
    
    print("Creating new au_artists table...")
    cursor.execute('''
        CREATE TABLE au_artists (
            artist_id TEXT PRIMARY KEY,
            artist_name TEXT,
            art_type TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database schema fixed successfully!")
    print("   Ready to run multi_sheet_sync.py or fix_inventory_sync.py")

if __name__ == "__main__":
    fix_database_schema()