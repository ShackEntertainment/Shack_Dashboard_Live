import telebot
import sqlite3
import os
import time
from dotenv import load_dotenv

# Load Telegram token
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize Bot
bot = telebot.TeleBot(TOKEN)

def get_db_connection():
    """Connect to the executive cache database"""
    db_path = 'executive_cache.db'
    if not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(db_path)
    return conn

def parse_currency(value):
    """Convert text currency like '£170.00' to float"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    # Remove £ symbol and convert to float
    try:
        clean_value = str(value).replace('£', '').replace(',', '')
        return float(clean_value)
    except:
        return 0.0

def query_database(question):
    """Simple query handler for common financial questions"""
    conn = get_db_connection()
    if not conn:
        return " Database not found. Run data_sync.py first."
    
    cursor = conn.cursor()
    question_lower = question.lower()
    
    try:
        # EVENTS OVERVIEW
        if 'event' in question_lower or 'schedule' in question_lower:
            cursor.execute("""
                SELECT Event_Name, Event_Date, Venue_Name, Status, Tickets_Sold, Capacity_Total
                FROM le_events
                LIMIT 5
            """)
            results = cursor.fetchall()
            if results:
                response = "🎫 **Upcoming Events:**\n\n"
                for row in results:
                    response += f"• {row[1]} ({row[2]})\n"
                    response += f"  Date: {row[2] if row[2] else 'TBD'} | Status: {row[3]}\n"
                    response += f"  Tickets: {row[4]}/{row[5]}\n\n"
                return response
            return "No event data available yet."
        
        # TICKET SALES / REVENUE
        elif 'ticket' in question_lower or 'sale' in question_lower or 'revenue' in question_lower:
            cursor.execute("""
                SELECT SUM(Quantity) as total_tickets, SUM(Total_Price) as total_revenue
                FROM le_bookings
            """)
            result = cursor.fetchone()
            if result and result[0]:
                # Parse revenue (it's text with £ symbol)
                total_revenue = parse_currency(result[1])
                return f"📊 **Ticket Sales Summary:**\n• Total Tickets Sold: {result[0]}\n• Total Revenue: £{total_revenue:,.2f}"
            return "No ticket sales data available yet."
        
        # BOOKINGS/SALES DETAIL
        elif 'booking' in question_lower or 'customer' in question_lower or 'sales' in question_lower:
            cursor.execute("""
                SELECT Customer_Name, Event_ID, Ticket_Type, Quantity, Total_Price, Payment_Status
                FROM le_bookings
                LIMIT 5
            """)
            results = cursor.fetchall()
            if results:
                response = "📋 **Recent Bookings:**\n\n"
                for row in results:
                    customer = row[0] or "Unknown"
                    ticket_type = row[2] or "Standard"
                    qty = row[3] or 0
                    # Parse the Total_Price (it's text with £)
                    price = parse_currency(row[4])
                    status = row[5] or "Unknown"
                    
                    response += f"• {customer}\n"
                    response += f"  {ticket_type} x{qty} = £{price:,.2f}\n"
                    response += f"  Status: {status}\n\n"
                return response
            return "No booking data available yet."
        
        # CAPACITY
        elif 'capacity' in question_lower or 'full' in question_lower:
            cursor.execute("""
                SELECT Event_Name, Tickets_Sold, Capacity_Total, 
                       (Capacity_Total - Tickets_Sold) as Remaining
                FROM le_events
            """)
            results = cursor.fetchall()
            if results:
                response = "📊 **Event Capacity:**\n\n"
                for row in results:
                    pct = (row[1] / row[2] * 100) if row[2] > 0 else 0
                    response += f"• {row[0]}: {row[1]}/{row[2]} ({pct:.0f}% full)\n"
                    response += f"  Remaining: {row[3]} tickets\n\n"
                return response
            return "No capacity data available yet."
        
        # DEFAULT - Show available tables
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            response = "📁 **Available Data Sources:**\n\n"
            for table in tables:
                response += f"• {table[0]}\n"
            response += "\n💡 Try asking:\n- What events do we have?\n- How many tickets sold?\n- Show me bookings\n- What's our capacity?"
            return response
            
    except Exception as e:
        return f" Database error: {str(e)}"
    finally:
        conn.close()

# Telegram Commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome = (
        "🏰 Shack Finance Bot - Online!\n\n"
        "I can query your financial data directly from the database.\n\n"
        "Commands:\n"
        "/finance [question] - Ask about finances\n"
        "/events - View events\n"
        "/tickets - View ticket sales\n"
        "/bookings - View recent bookings\n"
        "/capacity - Check event capacity\n"
        "/status - System check\n\n"
        "Example: /finance How many tickets sold?"
    )
    bot.reply_to(message, welcome)

@bot.message_handler(commands=['finance', 'ask'])
def finance_query(message):
    question = message.text.replace('/finance ', '').replace('/ask ', '').strip()
    
    if not question or message.text in ['/finance', '/ask']:
        bot.reply_to(message, "Please ask a question. Example: /finance How many tickets sold?")
        return
    
    # Send thinking message
    thinking = bot.reply_to(message, "🔍 Querying database...")
    
    # Get answer
    answer = query_database(question)
    
    # Update message
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=thinking.message_id,
        text=answer
    )

@bot.message_handler(commands=['events'])
def show_events(message):
    answer = query_database("What events do we have?")
    bot.reply_to(message, answer)

@bot.message_handler(commands=['tickets'])
def show_tickets(message):
    answer = query_database("How many tickets sold?")
    bot.reply_to(message, answer)

@bot.message_handler(commands=['bookings'])
def show_bookings(message):
    answer = query_database("Show me recent bookings")
    bot.reply_to(message, answer)

@bot.message_handler(commands=['capacity'])
def show_capacity(message):
    answer = query_database("What's our event capacity?")
    bot.reply_to(message, answer)

@bot.message_handler(commands=['status'])
def status_check(message):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        bot.reply_to(message, f"✅ Database connected\n📊 {len(tables)} tables available")
    else:
        bot.reply_to(message, "❌ Database not found\nRun data_sync.py first")

# Start the bot
print("="*50)
print("🏰 Shack Finance Bot starting...")
print("Database: executive_cache.db")
print("Listening for commands...")
print("="*50)

while True:
    try:
        bot.polling(timeout=10)
    except Exception as e:
        print(f"Connection error: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)