import os
import sys
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import gspread
import pandas as pd
from datetime import datetime, timedelta

# ────────────────────────────────────────
# LOAD CONFIGURATION WITH ABSOLUTE PATHS
# ────────────────────────────────────────
# Get the directory where this script lives
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, 'configs', '.env')

print(f"📁 Script directory: {script_dir}")
print(f"📁 Project root: {project_root}")
print(f"📁 Looking for .env at: {env_path}")

# Load the .env file
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    print("✅ .env file loaded successfully!")
else:
    print(f"❌ .env file NOT found at: {env_path}")
    print("Please check the file exists!")
    sys.exit(1)

# Get tokens
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
CREDENTIALS = os.path.join(project_root, 'configs', 'service_account.json')

print(f"🤖 Token loaded: {'✅ Yes' if TELEGRAM_TOKEN else '❌ No'}")
print(f"💬 Chat ID: {CHAT_ID}")
print(f"📊 Sheet ID: {SHEET_ID}")

# ────────────────────────────────────────
# SETUP LOGGING
# ────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────
# CONNECT TO GOOGLE SHEETS
# ────────────────────────────────────────
def connect_to_sheets():
    """Connect to Google Sheets and return the spreadsheet object."""
    try:
        if not os.path.exists(CREDENTIALS):
            logger.error(f"❌ Service account file not found: {CREDENTIALS}")
            return None
        
        gc = gspread.service_account(filename=CREDENTIALS)
        sheet = gc.open_by_key(SHEET_ID)
        logger.info("✅ Google Sheets connected!")
        return sheet
    except Exception as e:
        logger.error(f"❌ Sheet Connection Failed: {e}")
        return None

# ────────────────────────────────────────
# HELPER FUNCTIONS
# ────────────────────────────────────────
def get_sales_data(sheet):
    """Fetch sales data from Google Sheets."""
    try:
        for tab in sheet.worksheets():
            tab_name = tab.title.lower().strip()
            if 'sales' in tab_name and 'outlet' not in tab_name and 'product' not in tab_name:
                records = tab.get_all_records()
                return pd.DataFrame(records)
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching sales: {e}")
        return pd.DataFrame()

def get_inventory_data(sheet):
    """Fetch inventory data from Google Sheets."""
    try:
        for tab in sheet.worksheets():
            tab_name = tab.title.lower().strip()
            if 'inventory' in tab_name:
                records = tab.get_all_records()
                return pd.DataFrame(records)
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        return pd.DataFrame()

# ────────────────────────────────────────
# BOT COMMANDS
# ────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = """
🎪 <b>Welcome to Shack Entertainment Bot!</b>

I'm your assistant for Artists Unlimited management.

<b>Available Commands:</b>
📊 /sales - Recent sales summary
🎨 /artists - Top performing artists
💰 /royalties - Monthly royalty calculator
📦 /stock [item] - Check stock for specific item
⚠️ /lowstock - Manual low stock check
🟢 /status - Bot health check
🔍 /debug - Show raw inventory data

Need help? Type /help
    """
    await update.message.reply_text(welcome_message, parse_mode='HTML')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bot and system status."""
    sheet = connect_to_sheets()
    
    if sheet:
        status_message = """
🟢 <b>System Active</b>

✅ Bot: Running
✅ Google Sheets: Connected
✅ Last Check: {time}

All systems operational!
        """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M'))
    else:
        status_message = """
🟡 <b>System Partially Active</b>

✅ Bot: Running
❌ Google Sheets: Connection Failed

Please check your credentials.
        """
    
    await update.message.reply_text(status_message, parse_mode='HTML')

async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent sales summary."""
    sheet = connect_to_sheets()
    if not sheet:
        await update.message.reply_text("❌ Cannot connect to Google Sheets", parse_mode='HTML')
        return
    
    sales_df = get_sales_data(sheet)
    
    if sales_df.empty:
        await update.message.reply_text("📊 No sales recorded yet.", parse_mode='HTML')
        return
    
    try:
        sales_df['Sale Date'] = pd.to_datetime(sales_df['Sale Date'], errors='coerce')
        recent = sales_df.sort_values('Sale Date', ascending=False).head(5)
        
        message = "📊 <b>Recent Sales (Last 5)</b>\n\n"
        for _, row in recent.iterrows():
            date = row['Sale Date'].strftime('%d/%m') if pd.notna(row['Sale Date']) else 'N/A'
            artist = row.get('Artist', 'Unknown')
            price = row.get('Sale Price (£)', 'N/A')
            sku = row.get('SKU', 'N/A')
            message += f"📅 {date} | {artist} | £{price} | {sku}\n"
        
        total_revenue = sales_df['Sale Price (£)'].sum() if 'Sale Price (£)' in sales_df.columns else 0
        message += f"\n💰 <b>Total Revenue: £{total_revenue:.2f}</b>"
        
        await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in sales command: {e}")
        await update.message.reply_text(f"❌ Error fetching sales: {e}", parse_mode='HTML')

async def artists(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top performing artists."""
    sheet = connect_to_sheets()
    if not sheet:
        await update.message.reply_text("❌ Cannot connect to Google Sheets", parse_mode='HTML')
        return
    
    sales_df = get_sales_data(sheet)
    
    if sales_df.empty:
        await update.message.reply_text("🎨 No artist data available yet.", parse_mode='HTML')
        return
    
    try:
        if 'Artist' in sales_df.columns and 'Sale Price (£)' in sales_df.columns:
            artist_performance = sales_df.groupby('Artist')['Sale Price (£)'].sum().sort_values(ascending=False)
            
            message = "🎨 <b>Top Performing Artists</b>\n\n"
            for i, (artist, revenue) in enumerate(artist_performance.head(5).items(), 1):
                royalty = revenue * 0.70
                message += f"{i}. {artist}\n   💰 Revenue: £{revenue:.2f}\n   👤 Royalty (70%): £{royalty:.2f}\n\n"
            
            await update.message.reply_text(message, parse_mode='HTML')
        else:
            await update.message.reply_text("⚠️ Missing Artist or Sale Price columns in data", parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in artists command: {e}")
        await update.message.reply_text(f"❌ Error: {e}", parse_mode='HTML')

async def royalties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculate monthly royalties."""
    sheet = connect_to_sheets()
    if not sheet:
        await update.message.reply_text("❌ Cannot connect to Google Sheets", parse_mode='HTML')
        return
    
    sales_df = get_sales_data(sheet)
    
    if sales_df.empty:
        await update.message.reply_text("💰 No sales data for royalty calculation.", parse_mode='HTML')
        return
    
    try:
        sales_df['Sale Date'] = pd.to_datetime(sales_df['Sale Date'], errors='coerce')
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_sales = sales_df[
            (sales_df['Sale Date'].dt.month == current_month) & 
            (sales_df['Sale Date'].dt.year == current_year)
        ]
        
        if monthly_sales.empty:
            await update.message.reply_text(f"💰 No sales in {datetime.now().strftime('%B %Y')}", parse_mode='HTML')
            return
        
        total_revenue = monthly_sales['Sale Price (£)'].sum()
        artist_royalty = total_revenue * 0.70
        shack_commission = total_revenue * 0.30
        
        message = f"""
💰 <b>Monthly Royalty Report</b>
📅 {datetime.now().strftime('%B %Y')}

💵 Total Revenue: £{total_revenue:.2f}
👥 Artist Royalties (70%): £{artist_royalty:.2f}
🎪 Shack Commission (30%): £{shack_commission:.2f}

Number of sales: {len(monthly_sales)}
        """
        await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in royalties command: {e}")
        await update.message.reply_text(f"❌ Error: {e}", parse_mode='HTML')

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check stock for a specific item."""
    sheet = connect_to_sheets()
    if not sheet:
        await update.message.reply_text("❌ Cannot connect to Google Sheets", parse_mode='HTML')
        return
    
    inventory_df = get_inventory_data(sheet)
    
    if inventory_df.empty:
        await update.message.reply_text("📦 No inventory data available.", parse_mode='HTML')
        return
    
    try:
        if not context.args:
            await update.message.reply_text("📦 Usage: /stock [item name or SKU]\n\nExample: /stock Sunset Mug", parse_mode='HTML')
            return
        
        search_term = ' '.join(context.args).lower()
        
        matching_items = inventory_df[
            inventory_df.apply(
                lambda row: search_term in str(row.get('Product Name', '')).lower() or 
                           search_term in str(row.get('SKU', '')).lower(),
                axis=1
            )
        ]
        
        if matching_items.empty:
            await update.message.reply_text(f"🔍 No items found matching '{search_term}'", parse_mode='HTML')
            return
        
        message = f"📦 <b>Stock Results for '{search_term}'</b>\n\n"
        for _, item in matching_items.iterrows():
            name = item.get('Product Name', 'Unknown')
            sku = item.get('SKU', 'N/A')
            stock = item.get('Current Stock', 'N/A')
            price = item.get('Retail Price (£)', 'N/A')
            
            status_emoji = "✅" if int(stock) > 5 else "⚠️" if int(stock) > 0 else "❌"
            message += f"{status_emoji} {name}\n"
            message += f"   SKU: {sku}\n"
            message += f"   Stock: {stock} units\n"
            message += f"   Price: £{price}\n\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in stock command: {e}")
        await update.message.reply_text(f"❌ Error: {e}", parse_mode='HTML')

async def lowstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual check for low stock items."""
    sheet = connect_to_sheets()
    if not sheet:
        await update.message.reply_text("❌ Cannot connect to Google Sheets", parse_mode='HTML')
        return
    
    inventory_df = get_inventory_data(sheet)
    
    if inventory_df.empty:
        await update.message.reply_text("📦 No inventory data available.", parse_mode='HTML')
        return
    
    try:
        low_stock_items = inventory_df[inventory_df['Current Stock'] < 5]
        
        if low_stock_items.empty:
            await update.message.reply_text("✅ All stock levels healthy! No items below 5 units.", parse_mode='HTML')
            return
        
        message = f"⚠️ <b>Low Stock Alert</b>\n\n{len(low_stock_items)} items below 5 units:\n\n"
        for _, item in low_stock_items.iterrows():
            name = item.get('Product Name', 'Unknown')
            sku = item.get('SKU', 'N/A')
            stock = item.get('Current Stock', 'N/A')
            
            emoji = "🔴" if int(stock) == 0 else "⚠️"
            message += f"{emoji} {name} (SKU: {sku})\n"
            message += f"   Current Stock: {stock} units\n\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in lowstock command: {e}")
        await update.message.reply_text(f"❌ Error: {e}", parse_mode='HTML')

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show raw inventory data for debugging."""
    sheet = connect_to_sheets()
    if not sheet:
        await update.message.reply_text("❌ Cannot connect to Google Sheets", parse_mode='HTML')
        return
    
    inventory_df = get_inventory_data(sheet)
    
    if inventory_df.empty:
        await update.message.reply_text("🔍 No inventory data available.", parse_mode='HTML')
        return
    
    try:
        message = "🔍 <b>Raw Inventory Data</b>\n\n"
        message += f"Total Items: {len(inventory_df)}\n"
        message += f"Columns: {', '.join(inventory_df.columns)}\n\n"
        
        for idx, row in inventory_df.head(3).iterrows():
            message += f"Item {idx + 1}:\n"
            for col in inventory_df.columns:
                message += f"  {col}: {row.get(col, 'N/A')}\n"
            message += "\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in debug command: {e}")
        await update.message.reply_text(f"❌ Error: {e}", parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message."""
    help_message = """
🎪 <b>Shack Entertainment Bot - Help</b>

<b>General Commands:</b>
/start - Show welcome message
/help - Show this help message
/status - Check bot and system status

<b>Sales & Artists:</b>
/sales - View recent sales summary
/artists - Top performing artists
/royalties - Monthly royalty calculator (70/30 split)

<b>Inventory Management:</b>
/stock [item] - Check stock for specific item
Example: /stock Sunset Mug
/lowstock - Manual low stock check
/debug - Show raw inventory data

<b>Support:</b>
📧 Email: bola@shackentertainment.com
    """
    await update.message.reply_text(help_message, parse_mode='HTML')

async def daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual trigger for daily report."""
    await update.message.reply_text("📊 Generating daily report...", parse_mode='HTML')
    await sales(update, context)

# ────────────────────────────────────────
# MAIN FUNCTION
# ────────────────────────────────────────
def main():
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN not found in .env file!")
        sys.exit(1)
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("sales", sales))
    application.add_handler(CommandHandler("artists", artists))
    application.add_handler(CommandHandler("royalties", royalties))
    application.add_handler(CommandHandler("stock", stock))
    application.add_handler(CommandHandler("lowstock", lowstock))
    application.add_handler(CommandHandler("debug", debug))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("dailyreport", daily_report))
    
    # Start the Bot
    logger.info("🎪 Shack Agent running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()