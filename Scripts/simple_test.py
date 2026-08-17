import telebot
import os
from dotenv import load_dotenv

# 1. Load environment variables from your configs folder
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

print("="*50)
print(f"Attempting to connect with token: {TOKEN[:15]}...[HIDDEN]")
print("="*50)

try:
    # 2. Initialize the bot
    bot = telebot.TeleBot(TOKEN)
    
    # 3. Define a simple command handler
    @bot.message_handler(commands=['start', 'test'])
    def send_welcome(message):
        bot.reply_to(message, "✅ Connection successful! The Shack - Qwen bot is online and listening.")

    print("✅ Bot initialized successfully!")
    print("👉 Open Telegram and send '/test' to your bot.")
    print("👉 Press Ctrl+C to stop.")
    print("-" * 50)
    
    # 4. Start polling with extended timeouts to prevent rapid disconnects
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

except Exception as e:
    print(f"❌ FAILED TO CONNECT:")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")