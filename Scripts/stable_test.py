import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

# Load token
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

print("="*50)
print("Starting Shack - Qwen Bot (Stable Version)...")
print("="*50)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Connection successful! The Shack - Qwen bot is online and listening.")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Test passed! Bot is working correctly.")

def main():
    # Create the Application with better timeout settings
    application = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).pool_timeout(30).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("test", test))
    
    # Start the bot
    print("✅ Bot initialized successfully!")
    print("👉 Open Telegram and send '/test' to your bot.")
    print("👉 Press Ctrl+C to stop.")
    print("-" * 50)
    
    # Run polling - this is the key fix
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()