import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print("Adding missing columns to au_artists table...\n")

# List of columns to add with their types
columns_to_add = [
    ('email', 'TEXT'),
    ('phone', 'TEXT'),
    ('genre_style', 'TEXT'),
    ('portfolio_url', 'TEXT'),
    ('application_date', 'TEXT'),
    ('review_status', 'TEXT'),
    ('contract_signed', 'TEXT'),
    ('commission_rate', 'REAL DEFAULT 30.0'),
    ('total_sales', 'REAL DEFAULT 0.0'),
    ('total_earned', 'REAL DEFAULT 0.0'),
    ('shack_share', 'REAL DEFAULT 0.0'),
    ('notes', 'TEXT')
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE au_artists ADD COLUMN {col_name} {col_type}")
        print(f"✅ Added {col_name} ({col_type})")
    except Exception as e:
        if 'duplicate column' in str(e).lower():
            print(f"  ⚠️ {col_name} already exists")
        else:
            print(f"  ❌ Error adding {col_name}: {e}")

conn.commit()

# Verify the schema
print("\n=== VERIFICATION ===")
cursor.execute("PRAGMA table_info(au_artists)")
columns = cursor.fetchall()
print(f"au_artists now has {len(columns)} columns:")
for col in columns:
    print(f"  • {col[1]} ({col[2]})")

conn.close()
print("\n✅ Schema fixed! Restart the bot and try /roster again.")