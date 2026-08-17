import telebot
import sqlite3
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = telebot.TeleBot(TOKEN)

def get_db():
    """Connect to executive cache database"""
    db_path = 'executive_cache.db'
    if not os.path.exists(db_path):
        return None
    return sqlite3.connect(db_path)

def init_artist_tables(conn):
    """Initialize Artist Relations database tables safely"""
    cursor = conn.cursor()
    
    # Artist Profiles
    cursor.execute('''CREATE TABLE IF NOT EXISTS au_artists (
        artist_id TEXT PRIMARY KEY,
        artist_name TEXT NOT NULL,
        art_type TEXT,
        email TEXT,
        phone TEXT,
        genre_style TEXT,
        portfolio_url TEXT,
        application_date TEXT,
        review_status TEXT,
        contract_signed TEXT,
        commission_rate REAL DEFAULT 30.0,
        total_sales REAL DEFAULT 0.0,
        total_earned REAL DEFAULT 0.0,
        shack_share REAL DEFAULT 0.0,
        active_status TEXT DEFAULT 'Active',
        notes TEXT
    )''')
    
    # Commission Tracking
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
        payment_date TEXT,
        amount REAL DEFAULT 0.0
    )''')
    
    # Artist Payouts
    cursor.execute('''CREATE TABLE IF NOT EXISTS au_payouts (
        payout_id TEXT PRIMARY KEY,
        artist_id TEXT,
        amount REAL,
        payout_date TEXT,
        payment_method TEXT,
        status TEXT DEFAULT 'Pending',
        notes TEXT
    )''')
    
    # Talent Roster
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
    
    # Artist Contracts
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
    
    conn.commit()

# ============================================================================
# TELEGRAM COMMANDS
# ============================================================================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = """
🏰 **Shack Entertainment - Artist Relations Agent**

**Artist Management:**
/artist [name] - View artist details & earnings
/add_artist - Onboard new artist
/roster - List all artists & talent
/commission [artist], [amount] - Calculate 70/30 split
/payout [artist] - Generate payout report

**Talent Management:**
/add_talent - Add writer/presenter/speaker
/talent_list - View all talent

**System:**
/status - Database status
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def system_status(message):
    """Check database status - STABLE VERSION"""
    conn = get_db()
    if not conn:
        bot.reply_to(message, "❌ Database not found.")
        return
    
    cursor = conn.cursor()
    
    try:
        # Safe queries using COALESCE to prevent None errors
        cursor.execute("SELECT COUNT(*) FROM au_artists WHERE active_status = 'Active'")
        total_artists = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM au_artists WHERE art_type = 'Visual' AND active_status = 'Active'")
        visual = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM au_artists WHERE art_type = 'Performance' AND active_status = 'Active'")
        performance = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM talent_roster WHERE status = 'Active'")
        talent = cursor.fetchone()[0] or 0
        
        # COALESCE ensures sum is 0.0 if no rows exist
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM au_commissions WHERE payment_status = 'Pending'")
        pending_row = cursor.fetchone()
        pending_count = pending_row[0] or 0
        pending_amount = pending_row[1] or 0.0
        
        response = f"""
🏰 **ARTIST RELATIONS AGENT - STATUS**

**Roster:**
• Total Artists: {total_artists}/50
  - Visual: {visual}/25
  - Performance: {performance}/25
• Talent: {talent} active

**Commissions:**
• Pending Payouts: {pending_count}
• Total Pending: £{pending_amount:,.2f}

**Database:** ✅ Connected
**Last Sync:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error checking status: {str(e)}")
    finally:
        conn.close()

@bot.message_handler(commands=['roster'])
def view_roster(message):
    """View all active artists and talent - STABLE VERSION"""
    conn = get_db()
    if not conn:
        bot.reply_to(message, "❌ Database not found.")
        return
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT artist_name, genre_style, total_sales, active_status 
            FROM au_artists 
            WHERE art_type = 'Visual' AND active_status = 'Active'
            ORDER BY total_sales DESC
        """)
        visual = cursor.fetchall()
        
        cursor.execute("""
            SELECT artist_name, genre_style, total_sales, active_status 
            FROM au_artists 
            WHERE art_type = 'Performance' AND active_status = 'Active'
            ORDER BY total_sales DESC
        """)
        performance = cursor.fetchall()
        
        cursor.execute("""
            SELECT talent_name, talent_type, specialty, status 
            FROM talent_roster 
            WHERE status = 'Active'
        """)
        talent = cursor.fetchall()
        
        response = f"🏰 **SHACK ENTERTAINMENT ROSTER**\n\n"
        response += f"🎨 **VISUAL ARTISTS** ({len(visual)}/25)\n"
        
        if visual:
            for artist in visual[:10]:
                sales = artist[2] if artist[2] is not None else 0.0
                response += f"• {artist[0]} | {artist[1]} | Sales: £{sales:,.2f}\n"
        else:
            response += "• No visual artists yet.\n"
            
        response += f"\n🎭 **PERFORMANCE ACTS** ({len(performance)}/25)\n"
        
        if performance:
            for artist in performance[:10]:
                sales = artist[2] if artist[2] is not None else 0.0
                response += f"• {artist[0]} | {artist[1]} | Sales: £{sales:,.2f}\n"
        else:
            response += "• No performance acts yet.\n"
            
        response += f"\n✍️ **TALENT ROSTER**\n"
        
        if talent:
            for t in talent[:10]:
                response += f"• {t[0]} | {t[1]} | {t[2]}\n"
        else:
            response += "• No talent on roster yet.\n"
            
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error fetching roster: {str(e)}")
    finally:
        conn.close()

@bot.message_handler(commands=['add_artist'])
def add_artist(message):
    """Onboard new artist"""
    conn = get_db()
    if not conn:
        bot.reply_to(message, "❌ Database not found.")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM au_artists WHERE active_status = 'Active'")
    count = cursor.fetchone()[0] or 0
    
    if count >= 50:
        bot.reply_to(message, f"⚠️ Roster full! Maximum 50 artists (currently {count}).")
        conn.close()
        return
    
    response = f"""
🎨 **New Artist Onboarding**

**Current Roster:** {count}/50

**To add an artist, provide:**
1. Full name
2. Type: Visual or Performance
3. Email address
4. Genre/Style
5. Portfolio link

Example:
`/add_artist Paul Duncan, Visual, paul@art.com, Painting, paulduncan.art`
"""
    bot.reply_to(message, response)
    conn.close()

@bot.message_handler(commands=['commission'])
def calculate_commission(message):
    """Calculate 70/30 split"""
    try:
        parts = message.text.split('/commission ', 1)[1].strip()
        artist_name, amount_str = parts.split(',', 1)
        artist_name = artist_name.strip()
        amount = float(amount_str.strip().replace('£', '').replace(',', ''))
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: `/commission [artist name], [amount]`\nExample: `/commission Paul Duncan, 150`")
        return
    
    conn = get_db()
    if not conn:
        bot.reply_to(message, "❌ Database not found.")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT artist_name, commission_rate FROM au_artists WHERE LOWER(artist_name) LIKE LOWER(?)", (f'%{artist_name}%',))
    artist = cursor.fetchone()
    
    if not artist:
        bot.reply_to(message, f"❌ Artist '{artist_name}' not found. Use /add_artist first.")
        conn.close()
        return
    
    shack_rate = artist[1] if artist[1] is not None else 30.0
    artist_rate = 100 - shack_rate
    
    shack_share = (amount * shack_rate) / 100
    artist_share = (amount * artist_rate) / 100
    
    response = f"""
💰 **Commission Calculation**

**Artist:** {artist[0]}
**Sale Amount:** £{amount:,.2f}

**Split:**
🏰 Shack ({shack_rate}%): £{shack_share:,.2f}
🎨 Artist ({artist_rate}%): £{artist_share:,.2f}
"""
    bot.reply_to(message, response)
    conn.close()

@bot.message_handler(commands=['payout'])
def generate_payout(message):
    """Generate payout report"""
    try:
        artist_name = message.text.split('/payout ', 1)[1].strip()
    except IndexError:
        bot.reply_to(message, "Usage: `/payout [artist name]`")
        return
    
    conn = get_db()
    if not conn:
        bot.reply_to(message, " Database not found.")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT artist_name, total_earned FROM au_artists WHERE LOWER(artist_name) LIKE LOWER(?)", (f'%{artist_name}%',))
    artist = cursor.fetchone()
    
    if not artist:
        bot.reply_to(message, f"❌ Artist '{artist_name}' not found.")
        conn.close()
        return
    
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(artist_share), 0) FROM au_commissions WHERE artist_id = (SELECT artist_id FROM au_artists WHERE artist_name = ?) AND payment_status = 'Pending'", (artist[0],))
    pending = cursor.fetchone()
    
    response = f"""
💸 **PAYOUT REPORT - {artist[0]}**

**Total Career Earnings:** £{artist[1] if artist[1] else 0:,.2f}

**Pending Payouts:**
• Count: {pending[0] or 0}
• Amount: £{pending[1] or 0:,.2f}
"""
    bot.reply_to(message, response)
    conn.close()

@bot.message_handler(commands=['add_talent'])
def add_talent(message):
    response = """
✍️ **Add Talent to Roster**

Provide details:
`/add_talent Name, Type, Specialty, Email`

Example:
`/add_talent Sarah Johnson, Writer, Politics, sarah@email.com`
"""
    bot.reply_to(message, response)

@bot.message_handler(commands=['talent_list'])
def talent_list(message):
    conn = get_db()
    if not conn:
        bot.reply_to(message, "❌ Database not found.")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT talent_name, talent_type, specialty FROM talent_roster WHERE status = 'Active'")
    talent = cursor.fetchall()
    
    if not talent:
        bot.reply_to(message, "No talent on roster yet.")
        conn.close()
        return
    
    response = "️ **TALENT ROSTER**\n\n"
    for t in talent:
        response += f"• {t[0]} | {t[1]} | {t[2]}\n"
    
    bot.reply_to(message, response)
    conn.close()

# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    print("="*50)
    print("🏰 Shack Entertainment - Artist Relations Agent")
    print("Managing 50 artists & talent roster")
    print("="*50)
    
    conn = get_db()
    if conn:
        init_artist_tables(conn)
        conn.close()
    
    while True:
        try:
            print("Listening for commands...")
            bot.polling()
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()