import os
import logging
import traceback
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
import gspread

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
CREDENTIALS = os.path.join(project_root, 'configs', 'service_account.json')

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def connect():
    gc = gspread.service_account(filename=CREDENTIALS)
    return gc.open_by_key(SHEET_ID)

async def sales(update: Update, context):
    print("=== SALES COMMAND STARTED ===")
    try:
        print("Step 1: Connecting...")
        sheet = connect()
        print("Step 2: Connected!")
        
        print("Step 3: Finding tab...")
        tab_data = None
        for tab in sheet.worksheets():
            print("  Checking tab:", tab.title)
            if 'form' in tab.title.lower():
                tab_data = tab
                print("  Found it!")
                break
        
        if not tab_data:
            await update.message.reply_text("No sales tab found")
            return
        
        print("Step 4: Getting values...")
        all_values = tab_data.get_all_values()
        print("  Got", len(all_values), "rows")
        
        if len(all_values) < 2:
            await update.message.reply_text("No data")
            return
        
        headers = all_values[0]
        rows = all_values[-5:]
        
        print("Step 5: Building message...")
        msg = "Sales:\n\n"
        for i, row in enumerate(rows, 1):
            print("  Processing row", i)
            msg += "Row " + str(i) + ":\n"
            for j, val in enumerate(row):
                if j < len(headers):
                    msg += "  " + str(headers[j]) + ": " + str(val) + "\n"
            msg += "\n"
        
        print("Step 6: Sending message...")
        print("Message length:", len(msg))
        await update.message.reply_text(msg)
        print("=== SUCCESS ===")
        
    except Exception as e:
        print("=== ERROR ===")
        print("Error type:", type(e))
        print("Error:", str(e))
        print("Traceback:")
        traceback.print_exc()
        
        await update.message.reply_text("ERROR: " + str(e))

async def status(update: Update, context):
    await update.message.reply_text("Bot running")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("sales", sales))
    
    print("Bot started...")
    app.run_polling()