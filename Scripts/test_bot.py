import telebot
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'test'])
def test(message):
    bot.reply_to(message, "✅ Bot is working! Connection successful.")

print("Bot running...")
bot.infinity_polling()