"""
SHACK ENTERTAINMENT — shack_finance_queries.py
Shared finance query engine over executive_cache.db + live Google Sheet reads.
Pure data layer: no Telegram code. Imported by shack_main_agent.py.
"""
import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# DB discovery: Scripts first, then project root
db_path = os.path.join(script_dir, 'executive_cache.db')
if not os.path.exists(db_path):
    db_path = os.path.join(project_root, 'executive_cache.db')

def get_db_connection():
    if not os.path.exists(db_path):
        return None
    try:
        return sqlite3.connect(db_path)
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def parse_currency(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace('£', '').replace(',', ''))
    except:
        return 0.0

def sheet_sales():
    """Live read of the sales form tab (same source /sales uses)."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        from dotenv import load_dotenv
        load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        creds_file = os.path.join(project_root, 'configs', 'service_account.json')
        creds = Credentials.from_service_account_file(
            creds_file, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        sh = gspread.authorize(creds).open_by_key(sheet_id)
        for ws in sh.worksheets():
            if 'form' in ws.title.lower():
                values = ws.get_all_values()
                if not values:
                    return 0.0, 0
                headers = [h.strip().lower() for h in values[0]]
                idx = None
                for i, h in enumerate(headers):
                    if 'total' in h and ('price' in h or 'amount' in h):
                        idx = i
                        break
                if idx is None:
                    for i, h in enumerate(headers):
                        if 'price' in h or 'amount' in h:
                            idx = i
                            break
                if idx is None:
                    return 0.0, 0
                total, count = 0.0, 0
                for row in values[1:]:
                    if idx < len(row) and row[idx]:
                        v = parse_currency(row[idx])
                        if v:
                            total += v
                            count += 1
                return total, count
        return 0.0, 0
    except Exception as e:
        print(f"Sheet sales error: {e}")
        return 0.0, 0

def query_database(question):
    """Route a natural-language question to the right query."""
    conn = get_db_connection()
    if not conn:
        return f"❌ Database not found at {db_path}.\nRun complete_sync.py first."

    cursor = conn.cursor()
    q = question.lower()

    try:
        if 'event' in q or 'schedule' in q:
            cursor.execute("""SELECT Event_Name, Event_Date, Venue_Name, Status,
                Tickets_Sold, Capacity_Total FROM le_events LIMIT 5""")
            rows = cursor.fetchall()
            if rows:
                out = "🎫 **Upcoming Events:**\n\n"
                for r in rows:
                    out += f"• {r[1]}\n  Venue: {r[2]} | Status: {r[3]}\n  Tickets: {r[4]}/{r[5]}\n\n"
                return out
            return "No event data available yet."

        elif 'ticket' in q or 'booking' in q:
            cursor.execute("SELECT SUM(Quantity), SUM(Total_Price) FROM le_bookings")
            r = cursor.fetchone()
            if r and r[0]:
                return f"📊 **Ticket Sales:**\n• Total Tickets Sold: {r[0]}\n• Total Revenue: £{parse_currency(r[1]):,.2f}"
            return "No ticket sales data available yet."

        elif 'capacity' in q or 'full' in q:
            cursor.execute("""SELECT Event_Name, Tickets_Sold, Capacity_Total,
                (Capacity_Total - Tickets_Sold) FROM le_events""")
            rows = cursor.fetchall()
            if rows:
                out = "📊 **Event Capacity:**\n\n"
                for r in rows:
                    pct = (r[1] / r[2] * 100) if r[2] > 0 else 0
                    out += f"• {r[0]}: {r[1]}/{r[2]} ({pct:.0f}% full)\n  Remaining: {r[3]} tickets\n\n"
                return out
            return "No capacity data available yet."

        elif 'product' in q or 'inventory' in q or 'stock' in q:
            cursor.execute("""SELECT product_name, artist_name, retail_price,
                current_stock, location FROM au_products LIMIT 10""")
            rows = cursor.fetchall()
            if rows:
                out = "📦 **Products in Stock:**\n\n"
                for r in rows:
                    out += f"• {r[0]}\n  Artist: {r[1]} | Price: £{parse_currency(r[2]):,.2f}\n  Current Stock: {r[3] or 0} units | Location: {r[4]}\n\n"
                return out
            return "No products in inventory yet."

        elif 'artist' in q or 'roster' in q:
            cursor.execute("SELECT artist_name, art_type FROM au_artists")
            rows = cursor.fetchall()
            if rows:
                out = "🎨 **Artists on Roster:**\n\n"
                for r in rows:
                    out += f"• {r[0]}\n  Type: {r[1]}\n\n"
                return out
            return "No artists on roster yet."

        elif 'au sale' in q or 'art sale' in q or 'artist revenue' in q:
            cursor.execute("SELECT COUNT(*), SUM(total_price) FROM au_sales")
            r = cursor.fetchone()
            if r and r[1]:
                return f"📊 **Art Sales Summary:**\n• Total Transactions: {r[0]}\n• Total Revenue: £{r[1]:,.2f}"
            return "No art sales data available yet."

        elif 'partnership' in q or 'partner' in q:
            cursor.execute("SELECT partner_org, partnership_type FROM au_partnerships")
            rows = cursor.fetchall()
            if rows:
                out = "🤝 **Active Partnerships:**\n\n"
                for r in rows:
                    out += f"• {r[0]}\n  Type: {r[1]}\n\n"
                return out
            return "No partnerships on file yet."

        elif 'total revenue' in q or 'all revenue' in q or q == 'revenue':
            le = 0.0
            au_db = 0.0
            try:
                cursor.execute("SELECT SUM(Total_Price) FROM le_bookings")
                r = cursor.fetchone()
                le = parse_currency(r[0]) if r and r[0] else 0.0
            except Exception:
                le = 0.0
            try:
                cursor.execute("SELECT SUM(total_price) FROM au_sales")
                r = cursor.fetchone()
                au_db = parse_currency(r[0]) if r and r[0] else 0.0
            except Exception:
                au_db = 0.0
            sheet_total, sheet_count = sheet_sales()
            total = le + au_db + sheet_total
            return (f"💰 **Total Revenue (All Divisions):**\n\n"
                    f"• Live Exchange (DB): £{le:,.2f}\n"
                    f"• Artists Unlimited (DB): £{au_db:,.2f}\n"
                    f"• Store Sales (Sheet, live): £{sheet_total:,.2f} "
                    f"({sheet_count} transactions)\n\n"
                    f"**TOTAL: £{total:,.2f}**")

        elif 'expense' in q or 'spend' in q:
            csv_path = os.path.join(project_root, 'Data', 'expenses.csv')
            rows = []
            if os.path.exists(csv_path):
                with open(csv_path, encoding='utf-8') as f:
                    csv_lines = [x.rstrip() for x in f if x.strip()]
                for x in csv_lines[1:][-3:]:
                    parts = x.split(',')
                    if len(parts) >= 5:
                        rows.append((parts[5] if len(parts) > 5 else 'other',
                                     parts[3], parts[4]))
            if rows:
                out = "💸 **Recent Expenses:**\n\n"
                for cat, desc, amt in rows:
                    out += f"• {cat}: {desc} — £{parse_currency(amt):,.2f}\n\n"
                return out
            return "No expense data available yet."

        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            out = "📁 **Available Data Sources:**\n\n" + "".join(f"• {t[0]}\n" for t in tables)
            out += ("\n💡 **Try asking:**\n- What events do we have?\n- How many tickets sold?\n"
                    "- Show me artists\n- What products in stock?\n- What's our total revenue?\n- What expenses do we have?")
            return out

    except Exception as e:
        return f"❌ Database error: {str(e)}"
    finally:
        conn.close()

if __name__ == '__main__':
    print(query_database('What products in stock?'))