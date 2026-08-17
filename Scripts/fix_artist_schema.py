import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print("Fixing Artist Relations schema...")

# Add missing columns to au_artists
try:
    cursor.execute("ALTER TABLE au_artists ADD COLUMN active_status TEXT DEFAULT 'Active'")
    print("✅ Added active_status to au_artists")
except Exception as e:
    print(f"  active_status already exists or error: {e}")

# Create missing tables
cursor.execute('''CREATE TABLE IF NOT EXISTS au_commissions (
    commission_id TEXT PRIMARY KEY,
    artist_id TEXT,
    sale_id TEXT,
    product_name TEXT,
    sale_amount REAL,
    artist_share REAL,
    shack_share REAL,
    commission_date TEXT,
    payment_status TEXT DEFAULT 'Pending',
    payment_date TEXT
)''')
print("✅ au_commissions table ready")

cursor.execute('''CREATE TABLE IF NOT EXISTS au_payouts (
    payout_id TEXT PRIMARY KEY,
    artist_id TEXT,
    amount REAL,
    payout_date TEXT,
    payment_method TEXT,
    status TEXT DEFAULT 'Pending',
    notes TEXT
)''')
print("✅ au_payouts table ready")

cursor.execute('''CREATE TABLE IF NOT EXISTS talent_roster (
    talent_id TEXT PRIMARY KEY,
    talent_name TEXT NOT NULL,
    talent_type TEXT,
    specialty TEXT,
    email TEXT,
    phone TEXT,
    portfolio_url TEXT,
    contract_date TEXT,
    rate_card TEXT,
    availability TEXT,
    status TEXT DEFAULT 'Active',
    projects_completed INTEGER DEFAULT 0,
    total_earned REAL DEFAULT 0.0
)''')
print("✅ talent_roster table ready")

cursor.execute('''CREATE TABLE IF NOT EXISTS au_contracts (
    contract_id TEXT PRIMARY KEY,
    artist_id TEXT,
    contract_type TEXT,
    start_date TEXT,
    end_date TEXT,
    renewal_date TEXT,
    terms TEXT,
    status TEXT DEFAULT 'Active'
)''')
print("✅ au_contracts table ready")

conn.commit()
print("\n✅ Schema fixed! Restart the Artist Relations Agent.")
conn.close()