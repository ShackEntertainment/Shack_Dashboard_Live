import os
import gspread
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Load credentials
env_path = r'C:\Users\Bola\Documents\Shack_Project\configs\.env'
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
CREDENTIALS_FILE = r'C:\Users\Bola\Documents\Shack_Project\configs\service_account.json'
YOUR_CHAT_ID = '8794865372'

def send_daily_report():
    """Sends a daily sales summary to your Telegram"""
    print("Starting Daily Report...")
    
    if not TELEGRAM_TOKEN:
        print("❌ ERROR: Telegram Token not found!")
        return

    try:
        # Connect to Google Sheets
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        sheet = gc.open_by_key(SHEET_ID)
        
        # Find Sales tab
        sales_tab = None
        for tab in sheet.worksheets():
            if 'sales' in tab.title.lower() and 'outlet' not in tab.title.lower():
                sales_tab = tab
                break
        
        if not sales_tab:
            print("❌ Could not find Sales tab.")
            return
        
        # Get data
        data = sales_tab.get_all_records()
        
        # Calculate totals (handle £ symbol)
        total_sales = len(data)
        total_revenue = 0
        for sale in data:
            price_str = str(sale.get('Sale Price (£)', 0)).replace('£', '').strip()
            try:
                total_revenue += float(price_str)
            except:
                pass  # Skip invalid prices
        
        # Build message
        message = f"🎪 **SHACK DAILY BRIEFING** 🎪\n"
        message += f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        message += f"📊 **SUMMARY**\n"
        message += f"• Total Sales: {total_sales}\n"
        message += f"• Total Revenue: £{total_revenue:.2f}\n\n"
        message += f"🤖 Have a great day, Boss!"
        
        # Send to Telegram
        send_message(message)
        
    except Exception as e:
        print(f"❌ Script Error: {str(e)}")

def send_message(text):
    """Sends a message to your Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': YOUR_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    print(f"Sending message to {YOUR_CHAT_ID}...")
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Telegram Error: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == '__main__':
    send_daily_report()