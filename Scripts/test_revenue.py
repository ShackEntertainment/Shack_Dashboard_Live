import sqlite3
import os

DB_PATH = 'executive_cache.db'

def test_revenue_query():
    print("🔍 Testing Revenue Query...\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check what tables exist
    print("=== AVAILABLE TABLES ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  • {table[0]}")
    
    # Try Live Exchange revenue
    print("\n=== LIVE EXCHANGE REVENUE ===")
    try:
        cursor.execute("SELECT SUM(Total_Price) FROM le_bookings")
        result = cursor.fetchone()
        print(f"  le_bookings total: {result[0]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Try Artists Unlimited revenue
    print("\n=== ARTISTS UNLIMITED REVENUE ===")
    try:
        cursor.execute("SELECT SUM(total_price) FROM au_sales")
        result = cursor.fetchone()
        print(f"  au_sales total: {result[0]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Check au_sales structure
    print("\n=== AU_SALES TABLE STRUCTURE ===")
    try:
        cursor.execute("PRAGMA table_info(au_sales)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  • {col[1]} ({col[2]})")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    conn.close()
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_revenue_query()