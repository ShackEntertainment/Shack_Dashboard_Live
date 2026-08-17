import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

# The status command is looking for 'amount' column that doesn't exist
# We'll add it as an alias for artist_share for backward compatibility

try:
    cursor.execute("ALTER TABLE au_commissions ADD COLUMN amount REAL")
    print("✅ Added amount column")
    
    # Copy artist_share to amount
    cursor.execute("UPDATE au_commissions SET amount = artist_share WHERE artist_share IS NOT NULL")
    print("✅ Populated amount from artist_share")
    
    conn.commit()
except Exception as e:
    print(f"Note: {e}")

conn.close()
print("✅ Status command should work now!")