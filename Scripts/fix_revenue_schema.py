import sqlite3

def fix_revenue_schema():
    conn = sqlite3.connect('executive_cache.db')
    cursor = conn.cursor()
    print("🔧 Fixing finance_revenue schema...")
    
    # Drop and recreate the table with correct columns
    cursor.execute("DROP TABLE IF EXISTS finance_revenue")
    
    cursor.execute('''CREATE TABLE finance_revenue (
        revenue_id TEXT PRIMARY KEY,
        platform TEXT,
        category TEXT,
        amount REAL,
        date TEXT,
        status TEXT DEFAULT 'Recorded'
    )''')
    
    print("✅ finance_revenue table recreated with correct schema")
    
    # Also ensure finance_expenses has the right columns
    try:
        cursor.execute("ALTER TABLE finance_expenses ADD COLUMN status")
        print("✅ finance_expenses status column added")
    except:
        print("  (status column may already exist)")
    
    conn.commit()
    conn.close()
    print("\n✅ Schema fix complete! Run sync again.")

if __name__ == "__main__":
    fix_revenue_schema()