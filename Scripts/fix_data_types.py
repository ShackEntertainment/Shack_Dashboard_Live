import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print(" FIXING DATA TYPES...\n")

# Fix le_bookings - convert text to numbers
cursor.execute("""
    UPDATE le_bookings 
    SET quantity = CAST(quantity AS INTEGER),
        total_price = CAST(total_price AS REAL)
""")
print("✅ Fixed le_bookings data types")

# Fix le_events - convert text to numbers
cursor.execute("""
    UPDATE le_events 
    SET tickets_sold = CAST(tickets_sold AS INTEGER),
        capacity_total = CAST(capacity_total AS INTEGER)
""")
print("✅ Fixed le_events data types")

# Fix au_products - convert text to numbers
cursor.execute("""
    UPDATE au_products 
    SET cost_price = CAST(cost_price AS REAL),
        retail_price = CAST(retail_price AS REAL),
        initial_stock = CAST(initial_stock AS INTEGER),
        units_sold = CAST(units_sold AS INTEGER),
        current_stock = CAST(current_stock AS INTEGER)
""")
print("✅ Fixed au_products data types")

conn.commit()

# Verify
print("\n=== VERIFICATION ===")
cursor.execute("SELECT SUM(total_price) FROM le_bookings")
print(f"Total bookings revenue: £{cursor.fetchone()[0]:,.2f}")

cursor.execute("SELECT SUM(retail_price * units_sold) FROM au_products")
print(f"Estimated AU revenue: £{cursor.fetchone()[0]:,.2f}")

conn.close()
print("\n✅ DATA TYPES FIXED!")