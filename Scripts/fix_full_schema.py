import sqlite3

def fix_full_schema():
    conn = sqlite3.connect('executive_cache.db')
    cursor = conn.cursor()
    print("🏰 Updating Full Database Schema...")

    # 1. Update Live Exchange Events Table (Add new columns from your screenshot)
    try:
        cursor.execute("ALTER TABLE le_events ADD COLUMN event_type TEXT")
        cursor.execute("ALTER TABLE le_events ADD COLUMN venue_address TEXT")
        cursor.execute("ALTER TABLE le_events ADD COLUMN status TEXT")
        print("✅ Updated le_events table")
    except Exception as e:
        print(f"  (le_events columns may already exist: {e})")

    # 2. Create Shack News Network Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS sn_content (
        content_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        type TEXT,
        author TEXT,
        publish_date TEXT,
        status TEXT,
        url TEXT
    )''')
    print("✅ sn_content table ready")

    # 3. Create Financial Revenue Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS finance_revenue (
        revenue_id TEXT PRIMARY KEY,
        platform TEXT,
        category TEXT,
        amount REAL,
        date TEXT,
        status TEXT
    )''')
    print("✅ finance_revenue table ready")

    # 4. Ensure Finance Expenses Table exists (from previous step)
    cursor.execute('''CREATE TABLE IF NOT EXISTS finance_expenses (
        expense_id TEXT PRIMARY KEY,
        category TEXT,
        amount REAL,
        expense_date TEXT,
        description TEXT,
        status TEXT DEFAULT 'Recorded'
    )''')
    print("✅ finance_expenses table ready")

    conn.commit()
    conn.close()
    print("\n✅ Full Schema Update Complete!")

if __name__ == "__main__":
    fix_full_schema()