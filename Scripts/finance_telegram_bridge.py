import telebot
import os
import requests
import time
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv('configs/.env')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '-8794865372')

# 2. AnythingLLM Configuration
ANYTHINGLLM_API_KEY = "SYWBDAJ-CXZ4AEE-H9VWVR1-P3WDYVG"  # Your API key
WORKSPACE_SLUG = "shack-finance"
ANYTHINGLLM_URL = f"http://localhost:3001/api/v1/workspace/{WORKSPACE_SLUG}/chat"

# 3. Initialize Bot
bot = telebot.TeleBot(TOKEN)

def ask_finance_agent(question):
    """Send question to AnythingLLM and return the answer"""
    headers = {
        "Authorization": f"Bearer {ANYTHINGLLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": question,
        "mode": "chat"
    }
    
    try:
        response = requests.post(ANYTHINGLLM_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('textResponse', 'I received the data, but the response was empty.')
        else:
            return f"⚠️ API Error: Status {response.status_code}. Check if AnythingLLM is running."
    except requests.exceptions.Timeout:
        return "⏳ The agent is thinking too long. Please try a simpler question."
    except Exception as e:
        return f"❌ Connection error: {str(e)}. Is AnythingLLM running?"

# 4. Telegram Commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🏰 **Shack Finance Agent Online**\n\n"
        "I am your automated CFO. Here is how to use me:\n\n"
        "/finance [your question] - Ask me anything about our finances.\n"
        "/status - Check system connection.\n\n"
        "*Example:* `/finance What is our current cash runway?`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['finance'])
def finance_command(message):
    # Extract the question after /finance
    question = message.text.replace('/finance ', '').strip()
    
    if not question or question == "/finance":
        bot.reply_to(message, "Please ask a question. Example: `/finance What are our top expenses?`", parse_mode='Markdown')
        return

    # Send a "thinking" message
    thinking_msg = bot.reply_to(message, "🏰 Shack Finance Agent analyzing data...")
    
    # Get response from Finance Agent
    response_text = ask_finance_agent(question)
    
    # Edit the "thinking" message with the actual answer
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=thinking_msg.message_id,
        text=response_text,
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['status'])
def status_command(message):
    bot.reply_to(message, "✅ System Online. Connected to Shack Finance Workspace.")

# 5. Start Polling
print("="*50)
print("🏰 Shack Finance Telegram Bridge starting...")
print("Listening for commands...")
print("="*50)

while True:
    try:
        bot.polling(timeout=10)
    except Exception as e:
        print(f"Connection error: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)