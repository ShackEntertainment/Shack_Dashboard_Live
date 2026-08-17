import sqlite3

def fix_finance_schema():
    conn = sqlite3.connect('executive_cache.db')
    cursor = conn.cursor()
    print("🏰 Expanding Financial Database Schema...")

    # 1. Expenses Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS finance_expenses (
        expense_id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        expense_date TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'Recorded',
        receipt_url TEXT
    )''')
    print("✅ finance_expenses table ready")

    # 2. Cashflow Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS finance_cashflow (
        cashflow_id TEXT PRIMARY KEY,
        month TEXT NOT NULL,
        total_income REAL DEFAULT 0.0,
        total_expenses REAL DEFAULT 0.0,
        net_position REAL DEFAULT 0.0,
        notes TEXT
    )''')
    print("✅ finance_cashflow table ready")

    # 3. Invoices Table (For Drafting)
    cursor.execute('''CREATE TABLE IF NOT EXISTS finance_invoices (
        invoice_id TEXT PRIMARY KEY,
        recipient_name TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'Draft',
        created_date TEXT,
        approved_date TEXT
    )''')
    print("✅ finance_invoices table ready")

    conn.commit()
    conn.close()
    print("\n✅ Financial Schema Expansion Complete!")

if __name__ == "__main__":
    fix_finance_schema()