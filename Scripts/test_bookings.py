import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print("Checking le_bookings table...\n")

# Get column info
cursor.execute("PRAGMA table_info(le_bookings)")
columns = cursor.fetchall()
print("Columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Get sample data
print("\nSample data (first 3 rows):")
cursor.execute("SELECT * FROM le_bookings LIMIT 3")
rows = cursor.fetchall()
for row in rows:
    print(f"\nRow: {row}")

# Check for NULL or text values in numeric columns
print("\n\nChecking Total_Price column:")
cursor.execute("SELECT Total_Price, typeof(Total_Price) FROM le_bookings LIMIT 5")
results = cursor.fetchall()
for result in results:
    print(f"  Value: {result[0]} | Type: {result[1]}")

conn.close()