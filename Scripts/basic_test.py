import telebot
import time
import os
from dotenv import load_dotenv

# Load token
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

print("="*50)
print("Starting Basic Bot Test...")
print("="*50)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['test', 'start'])
def handle_test(message):
    print(f"✅ Received message from {message.chat.id}")
    try:
        bot.reply_to(message, "✅ SUCCESS! Bot is working!")
        print("✅ Reply sent successfully")
    except Exception as e:
        print(f"❌ Error sending reply: {e}")

print("✅ Bot initialized. Waiting for messages...")
print("Send /test to your bot now.")
print("-" * 50)

# Use simple polling instead of infinity_polling
while True:
    try:
        bot.polling(timeout=10)
    except Exception as e:
        print(f"Connection error: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)