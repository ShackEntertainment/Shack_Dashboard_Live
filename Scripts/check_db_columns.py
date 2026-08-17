import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print("=== DATABASE SCHEMA CHECK ===\n")

# Check au_artists table
print("au_artists columns:")
cursor.execute("PRAGMA table_info(au_artists)")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

# Check au_commissions table  
print("\nau_commissions columns:")
cursor.execute("PRAGMA table_info(au_commissions)")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

# Check talent_roster table
print("\ntalent_roster columns:")
cursor.execute("PRAGMA table_info(talent_roster)")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

conn.close()