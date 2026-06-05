import gspread
import telebot
from telebot import types
import pandas as pd
from datetime import datetime, timedelta
import schedule
import time
import os
from dotenv import load_dotenv

# ────────────────────────────────────────
# LOAD CONFIG
# ────────────────────────────────────────
load_dotenv('configs/.env')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
CREDENTIALS = 'configs/service_account.json'

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Your chat ID (where to send daily reports)
ADMIN_CHAT_ID = -8794865372  # REPLACE WITH YOUR CHAT ID

# ────────────────────────────────────────
# GOOGLE SHEETS CONNECTION
# ────────────────────────────────────────
def get_sheet_data():
    """Fetch data from Google Sheets"""
    try:
        gc = gspread.service_account(filename=CREDENTIALS)
        sheet = gc.open_by_key(SHEET_ID)
        
        sales_df = pd.DataFrame()
        inv_df = pd.DataFrame()
        
        # Get sales data
        for tab in sheet.worksheets():
            if 'sales' in tab.title.lower() or 'form' in tab.title.lower():
                if 'outlet' not in tab.title.lower():
                    sales_df = pd.DataFrame(tab.get_all_records())
                    break
        
        # Get inventory data
        for tab in sheet.worksheets():
            if 'inventory' in tab.title.lower():
                inv_df = pd.DataFrame(tab.get_all_records())
                break
        
        return sales_df, inv_df, "✅ Connected"
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), f"❌ Error: {e}"

# ────────────────────────────────────────
# 9 AM DAILY REPORT
# ────────────────────────────────────────
def send_daily_report():
    """Send automated 9 AM status report"""
    print(f"[{datetime.now()}] Sending daily report...")
    
    sales_df, inv_df, status = get_sheet_data()
    
    # Calculate metrics
    if not sales_df.empty:
        # Today's sales (filter by today's date)
        today = datetime.now().strftime('%d/%m/%Y')
        today_sales = sales_df[sales_df['Sale Date'].str.contains(today, na=False)]
        
        total_revenue = today_sales['Sale Price (£)'].sum() if 'Sale Price (£)' in today_sales.columns else 0
        total_sales = len(today_sales)
        top_artist = today_sales['Artist'].mode()[0] if 'Artist' in today_sales.columns and not today_sales.empty else "N/A"
    else:
        total_revenue = 0
        total_sales = 0
        top_artist = "N/A"
    
    # Low stock items
    if not inv_df.empty and 'Current Stock' in inv_df.columns:
        low_stock = inv_df[inv_df['Current Stock'] < 5]
        low_stock_count = len(low_stock)
    else:
        low_stock_count = 0
    
    # Build message
    message = f"""
🏰 **SHACK ENTERTAINMENT - DAILY STATUS**
📅 {datetime.now().strftime('%A, %d %B %Y')}
⏰ 9:00 AM Report

━━━━━━━━━━━━━━━━━━━━━━

💰 **SALES OVERVIEW**
📊 Total Sales Today: {total_sales}
💷 Revenue: £{total_revenue:,.2f}
🎨 Top Performer: {top_artist}

━━━━━━━━━━━━━━━━━━━━━━

📦 **INVENTORY ALERTS**
⚠️ Low Stock Items: {low_stock_count}
{f"🚨 Action needed!" if low_stock_count > 0 else "✅ All stock levels healthy"}

━━━━━━━━━━━━━━━━━━━━━━

📱 **SYSTEM STATUS**
{status}
 Bot: Online
 Dashboard: Live

━━━━━━━━━━━━━━━━━━━━━━

*Shack Entertainment - Talent on the Fringe*
    """
    
    # Send message
    try:
        bot.send_message(ADMIN_CHAT_ID, message, parse_mode='Markdown')
        print("✅ Daily report sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send report: {e}")

# ────────────────────────────────────────
# BOT COMMANDS
# ────────────────────────────────────────
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Handle /start and /help commands"""
    bot.reply_to(message, """
🏰 **Welcome to Shack Entertainment Bot!**

Available commands:
/status - Get current system status
/sales - View today's sales
/lowstock - Check inventory alerts
/report - Send daily report manually

*Talent on the Fringe*
    """, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def status_command(message):
    """Handle /status command"""
    sales_df, inv_df, status = get_sheet_data()
    bot.reply_to(message, f"🤖 Bot Status: Online\n📊 Sheets: {status}\n⏰ Last Check: {datetime.now().strftime('%H:%M:%S')}")

@bot.message_handler(commands=['sales'])
def sales_command(message):
    """Handle /sales command"""
    sales_df, inv_df, status = get_sheet_data()
    
    if not sales_df.empty:
        today = datetime.now().strftime('%d/%m/%Y')
        today_sales = sales_df[sales_df['Sale Date'].str.contains(today, na=False)]
        
        if not today_sales.empty:
            revenue = today_sales['Sale Price (£)'].sum()
            msg = f"💰 **Today's Sales**\n\n"
            for _, row in today_sales.iterrows():
                msg += f"• {row.get('Artist', 'Unknown')}: £{row.get('Sale Price (£)', 0)}\n"
            msg += f"\n**Total: £{revenue:,.2f}**"
            bot.reply_to(message, msg, parse_mode='Markdown')
        else:
            bot.reply_to(message, "📊 No sales recorded today yet.")
    else:
        bot.reply_to(message, "⚠️ Unable to fetch sales data.")

@bot.message_handler(commands=['lowstock'])
def lowstock_command(message):
    """Handle /lowstock command"""
    sales_df, inv_df, status = get_sheet_data()
    
    if not inv_df.empty and 'Current Stock' in inv_df.columns:
        low_stock = inv_df[inv_df['Current Stock'] < 5]
        
        if not low_stock.empty:
            msg = "🚨 **LOW STOCK ALERT**\n\n"
            for _, row in low_stock.iterrows():
                msg += f"• {row.get('Product Name', 'Unknown')}: {row['Current Stock']} left\n"
            bot.reply_to(message, msg, parse_mode='Markdown')
        else:
            bot.reply_to(message, "✅ All stock levels healthy!")
    else:
        bot.reply_to(message, "⚠️ Unable to fetch inventory data.")

@bot.message_handler(commands=['report'])
def report_command(message):
    """Handle /report command - manual trigger"""
    bot.reply_to(message, "📊 Generating daily report...")
    send_daily_report()

# ────────────────────────────────────────
# SCHEDULER
# ────────────────────────────────────────
def run_scheduler():
    """Run the scheduler in a separate thread"""
    schedule.every().day.at("09:00").do(send_daily_report)
    print("⏰ Scheduler started - Daily report set for 9:00 AM")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# ────────────────────────────────────────
# MAIN
# ────────────────────────────────────────
if __name__ == "__main__":
    print("🏰 Shack Entertainment Bot Starting...")
    print(f"🤖 Bot Token: {'✅ Set' if TELEGRAM_TOKEN else '❌ Missing'}")
    print(f"📊 Sheet ID: {'✅ Set' if SHEET_ID else '❌ Missing'}")
    
    # Start scheduler in background
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start bot
    print(" Bot is running... Press Ctrl+C to stop")
    bot.infinity_polling()