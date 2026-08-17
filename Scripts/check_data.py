import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print("=== DATABASE CONTENT CHECK ===\n")

# Check au_artists
try:
    cursor.execute("SELECT * FROM au_artists")
    rows = cursor.fetchall()
    print(f"au_artists: {len(rows)} records")
    for row in rows:
        print(f"  {row}")
except Exception as e:
    print(f"au_artists: {e}")

print()

# Check au_products
try:
    cursor.execute("SELECT product_name, retail_price, current_stock FROM au_products")
    rows = cursor.fetchall()
    print(f"au_products: {len(rows)} records")
    for row in rows:
        print(f"  {row}")
except Exception as e:
    print(f"au_products: {e}")

print()

# Check le_bookings
try:
    cursor.execute("SELECT booking_id, quantity, total_price FROM le_bookings")
    rows = cursor.fetchall()
    print(f"le_bookings: {len(rows)} records")
    for row in rows:
        print(f"  {row}")
except Exception as e:
    print(f"le_bookings: {e}")

print()

# Check le_events
try:
    cursor.execute("SELECT event_id, event_name, tickets_sold, capacity_total FROM le_events")
    rows = cursor.fetchall()
    print(f"le_events: {len(rows)} records")
    for row in rows:
        print(f"  {row}")
except Exception as e:
    print(f"le_events: {e}")

conn.close()