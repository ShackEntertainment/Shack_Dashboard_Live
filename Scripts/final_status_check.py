import sqlite3

conn = sqlite3.connect('executive_cache.db')
cursor = conn.cursor()

print("="*60)
print(" SHACK ENTERTAINMENT - SYSTEM STATUS")
print("="*60)

tables = {
    'Finance': ['finance_revenue', 'finance_expenses', 'finance_cashflow'],
    'Live Exchange': ['le_events', 'le_bookings'],
    'Artists Unlimited': ['au_products', 'au_artists'],
    'News Network': ['snn_content'],
    'Command Center': ['cc_projects', 'cc_kpi']
}

total_records = 0

for division, table_list in tables.items():
    print(f"\n{division.upper()}:")
    for table in table_list:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            total_records += count
            status = "✅" if count > 0 else "⚠️  (empty)"
            print(f"  {status} {table}: {count} records")
        except:
            print(f"  ❌ {table}: Table missing")

print("\n" + "="*60)
print(f"TOTAL RECORDS IN DATABASE: {total_records}")
print("="*60)

# Financial Summary
print("\n FINANCIAL OVERVIEW:")
try:
    cursor.execute("SELECT SUM(total_price) FROM le_bookings")
    le_rev = cursor.fetchone()[0] or 0
    print(f"  • Live Exchange Revenue: £{le_rev:,.2f}")
except:
    print("  • Live Exchange Revenue: N/A")

try:
    cursor.execute("SELECT SUM(retail_price * units_sold) FROM au_products")
    au_rev = cursor.fetchone()[0] or 0
    print(f"  • Artists Unlimited (Est): £{au_rev:,.2f}")
except:
    print("  • Artists Unlimited: N/A")

conn.close()

print("\n✅ STATUS CHECK COMPLETE!")