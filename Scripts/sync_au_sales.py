import telebot
import sqlite3
import os
import time
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load Telegram token
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize Bot with retry settings
bot = telebot.TeleBot(TOKEN)

def get_db_connection():
    """Connect to the executive cache database"""
    db_path = 'executive_cache.db'
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def parse_currency(value):
    """Convert text currency like '£170.00' to float"""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        clean_value = str(value).replace('£', '').replace(',', '')
        return float(clean_value)
    except:
        return 0.0

def query_database(question):
    """Query handler for all financial and business questions"""
    conn = get_db_connection()
    if not conn:
        return "❌ Database not found. Run multi_sheet_sync.py first."
    
    cursor = conn.cursor()
    question_lower = question.lower()
    
    try:
        # ========== LIVE EXCHANGE QUERIES ==========
        
        if 'event' in question_lower or 'schedule' in question_lower:
            try:
                cursor.execute("""
                    SELECT Event_Name, Event_Date, Venue_Name, Status, Tickets_Sold, Capacity_Total
                    FROM le_events LIMIT 5
                """)
                results = cursor.fetchall()
                if results:
                    response = "🎫 **Upcoming Events:**\n\n"
                    for row in results:
                        response += f"• {row[1]}\n"
                        response += f"  Venue: {row[2]} | Status: {row[3]}\n"
                        response += f"  Tickets: {row[4]}/{row[5]}\n\n"
                    return response
                return "No event data available yet."
            except Exception as e:
                logger.error(f"Events query error: {e}")
                return "️ Events table not found"
        
        elif 'ticket' in question_lower or 'booking' in question_lower:
            try:
                cursor.execute("""
                    SELECT SUM(Quantity), SUM(Total_Price) FROM le_bookings
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    revenue = parse_currency(result[1]) if result[1] else 0
                    return f"📊 **Ticket Sales:**\n• Total Tickets: {result[0]}\n• Revenue: £{revenue:,.2f}"
                return "No ticket sales data yet."
            except Exception as e:
                logger.error(f"Tickets query error: {e}")
                return "⚠️ Bookings table not found"
        
        elif 'capacity' in question_lower or 'full' in question_lower:
            try:
                cursor.execute("""
                    SELECT Event_Name, Tickets_Sold, Capacity_Total, 
                           (Capacity_Total - Tickets_Sold)
                    FROM le_events
                """)
                results = cursor.fetchall()
                if results:
                    response = "📊 **Event Capacity:**\n\n"
                    for row in results:
                        pct = (row[1] / row[2] * 100) if row[2] > 0 else 0
                        response += f"• {row[0]}: {row[1]}/{row[2]} ({pct:.0f}%)\n"
                        response += f"  Remaining: {row[3]}\n\n"
                    return response
                return "No capacity data yet."
            except Exception as e:
                logger.error(f"Capacity query error: {e}")
                return "️ Events table not found"
        
        # ========== ARTISTS UNLIMITED QUERIES ==========
        
        elif 'artist' in question_lower or 'roster' in question_lower:
            try:
                cursor.execute("SELECT artist_name, art_type FROM au_artists")
                results = cursor.fetchall()
                if results:
                    response = "🎨 **Artists on Roster:**\n\n"
                    for row in results:
                        response += f"• {row[0]}\n  Type: {row[1]}\n\n"
                    return response
                return "No artists on roster yet."
            except Exception as e:
                logger.error(f"Artists query error: {e}")
                return "⚠️ Artists table not found"
        
        elif 'product' in question_lower or 'inventory' in question_lower or 'stock' in question_lower:
            try:
                cursor.execute("""
                    SELECT product_name, artist_name, retail_price, current_stock
                    FROM au_products LIMIT 10
                """)
                results = cursor.fetchall()
                if results:
                    response = "📦 **Products in Stock:**\n\n"
                    for row in results:
                        response += f"• {row[0]}\n"
                        response += f"  Artist: {row[1]} | Price: £{row[2]:,.2f}\n"
                        response += f"  Stock: {row[3]} units\n\n"
                    return response
                return "No products in inventory yet."
            except Exception as e:
                logger.error(f"Products query error: {e}")
                return "️ Products table not found"
        
        elif 'total revenue' in question_lower or 'all revenue' in question_lower or question_lower == 'revenue':
            try:
                # Live Exchange revenue
                le_revenue = 0.0
                try:
                    cursor.execute("SELECT SUM(Total_Price) FROM le_bookings")
                    result = cursor.fetchone()
                    if result and result[0]:
                        le_revenue = parse_currency(result[0])
                except:
                    pass
                
                # Artists Unlimited revenue
                au_revenue = 0.0
                try:
                    cursor.execute("SELECT SUM(total_price) FROM au_sales")
                    result = cursor.fetchone()
                    if result and result[0]:
                        au_revenue = float(result[0])
                except:
                    pass
                
                total = le_revenue + au_revenue
                
                return f"💰 **Total Revenue:**\n\n• Live Exchange: £{le_revenue:,.2f}\n• Artists Unlimited: £{au_revenue:,.2f}\n\n**TOTAL: £{total:,.2f}**"
            except Exception as e:
                logger.error(f"Revenue query error: {e}")
                return "❌ Error calculating revenue"
        
        else:
            return "📁 **Available Commands:**\n\n/events\n/tickets\n/artists\n/products\n/revenue\n/status"
            
    except Exception as e:
        logger.error(f"Database error: {e}")
        return "❌ Database error"
    finally:
        conn.close()

# Telegram Commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome = " **Shack Finance Bot**\n\nCommands:\n/revenue\n/events\n/tickets\n/artists\n/products\n/status"
    bot.reply_to(message, welcome)

@bot.message_handler(commands=['revenue'])
def show_revenue(message):
    try:
        bot.reply_to(message, "🔍 Calculating...")
        answer = query_database("What's our total revenue?")
        bot.edit_message_text(answer, message.chat.id, bot.send_message(message.chat.id, "Loading...").message_id)
    except Exception as e:
        logger.error(f"Revenue command error: {e}")
        bot.reply_to(message, "❌ Error processing request")

@bot.message_handler(commands=['events', 'tickets', 'artists', 'products', 'status'])
def handle_commands(message):
    try:
        cmd = message.text.split()[0].replace('/', '')
        queries = {
            'events': "What events do we have?",
            'tickets': "How many tickets sold?",
            'artists': "Show me artists",
            'products': "What products in stock?",
            'status': "status check"
        }
        answer = query_database(queries.get(cmd, "help"))
        bot.reply_to(message, answer)
    except Exception as e:
        logger.error(f"Command {message.text} error: {e}")
        bot.reply_to(message, "❌ Error processing command")

# Main loop with better error handling
def main():
    logger.info("🏰 Enhanced Shack Finance Bot starting...")
    logger.info(f"Database: executive_cache.db")
    
    while True:
        try:
            logger.info("Connecting to Telegram...")
            bot.polling(
                timeout=60,
                long_polling=True,
                allowed_updates=telebot.util.update_types
            )
        except telebot.apihelper.ApiException as e:
            logger.error(f"Telegram API error: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Connection error: {e}")
            logger.info("Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    main()