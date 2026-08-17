import requests
import os
from dotenv import load_dotenv

# Load the token
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

print("Attempting to clear webhooks...")

# This URL tells Telegram to stop sending messages to a website and go back to normal
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true"

try:
    response = requests.get(url)
    print("Result:", response.json())
    if response.json().get('ok'):
        print("✅ Webhook cleared! You can now run your bot script.")
    else:
        print("❌ Failed to clear webhook.")
except Exception as e:
    print(f"Error: {e}")