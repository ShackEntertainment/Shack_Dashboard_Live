import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Tables in executive_cache.db:\n")
for table in tables:
    table_name = table[0]  # Access by index, not name
    print(f"\nTable: {table_name}")
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"Columns: {[col[1] for col in columns]}")  # col[1] is the column name
    
    # Count rows
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Rows: {count}")

conn.close()