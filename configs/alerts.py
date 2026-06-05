# ────────────────────────────────────────
# 🚨 SHACK ENTERTAINMENT - ALERT SYSTEM
# Automated Notifications & Monitoring
# ────────────────────────────────────────

import gspread
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('configs/.env')

# ────────────────────────────────────────
# 🔌 CONNECT TO SHEETS
# ────────────────────────────────────────
def connect_to_sheets():
    """Connect to Google Sheets"""
    try:
        gc = gspread.service_account(filename='configs/service_account.json')
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        return gc.open_by_key(sheet_id)
    except Exception as e:
        print(f"❌ Sheet connection error: {e}")
        return None

# ────────────────────────────────────────
# 📦 LOW STOCK ALERT
# ────────────────────────────────────────
def check_low_stock(threshold=5):
    """Check inventory for low stock items"""
    sheet = connect_to_sheets()
    if not sheet:
        return []
    
    low_stock_items = []
    
    try:
        for tab in sheet.worksheets():
            if 'inventory' in tab.title.lower():
                df = pd.DataFrame(tab.get_all_records())
                if 'Current Stock' in df.columns and 'Product Name' in df.columns:
                    low_items = df[df['Current Stock'] < threshold]
                    for _, item in low_items.iterrows():
                        low_stock_items.append({
                            'product': item.get('Product Name', 'Unknown'),
                            'stock': item.get('Current Stock', 0),
                            'threshold': threshold
                        })
    except Exception as e:
        print(f"Error checking stock: {e}")
    
    return low_stock_items

# ────────────────────────────────────────
# 🤝 PARTNERSHIP ALERTS
# ────────────────────────────────────────
def check_partnership_pipeline():
    """Check for partnerships nearing end date or pending"""
    sheet = connect_to_sheets()
    if not sheet:
        return [], []
    
    expiring_soon = []
    pending_deals = []
    
    try:
        for tab in sheet.worksheets():
            if 'partnership' in tab.title.lower():
                df = pd.DataFrame(tab.get_all_records())
                
                # Check expiring contracts (within 30 days)
                if 'End Date' in df.columns:
                    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
                    thirty_days_later = pd.Timestamp.now() + pd.Timedelta(days=30)
                    expiring = df[(df['End Date'] <= thirty_days_later) & 
                                 (df['End Date'] >= pd.Timestamp.now())]
                    
                    for _, partner in expiring.iterrows():
                        expiring_soon.append({
                            'partner': partner.get('Partner Organisation', 'Unknown'),
                            'end_date': partner.get('End Date').strftime('%d/%m/%Y'),
                            'value': partner.get('Partnership Value (£)', 'N/A')
                        })
                
                # Check pending deals
                if 'Status' in df.columns:
                    pending = df[df['Status'] == 'Pending']
                    for _, deal in pending.iterrows():
                        pending_deals.append({
                            'partner': deal.get('Partner Organisation', 'Unknown'),
                            'value': deal.get('Partnership Value (£)', 'N/A'),
                            'stage': deal.get('Stage', 'Negotiation')
                        })
    except Exception as e:
        print(f"Error checking partnerships: {e}")
    
    return expiring_soon, pending_deals

# ────────────────────────────────────────
# 📊 DAILY SUMMARY
# ────────────────────────────────────────
def generate_daily_summary():
    """Generate daily business summary"""
    sheet = connect_to_sheets()
    if not sheet:
        return None
    
    summary = {
        'date': datetime.now().strftime('%d %B %Y'),
        'total_revenue': 0,
        'sales_count': 0,
        'active_partnerships': 0,
        'low_stock_count': 0
    }
    
    try:
        # Get today's sales
        for tab in sheet.worksheets():
            if 'form' in tab.title.lower() or tab.title.lower() == 'sales':
                if 'outlet' not in tab.title.lower():
                    df = pd.DataFrame(tab.get_all_records())
                    if not df.empty and 'Timestamp' in df.columns:
                        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                        today = pd.Timestamp.now().date()
                        today_sales = df[df['Timestamp'].dt.date == today]
                        
                        if 'Sale Price (£)' in today_sales.columns:
                            today_sales['Sale Price (£)'] = today_sales['Sale Price (£)'].astype(str).str.replace('£', '').str.replace(',', '')
                            today_sales['Sale Price (£)'] = pd.to_numeric(today_sales['Sale Price (£)'], errors='coerce').fillna(0)
                            summary['total_revenue'] = today_sales['Sale Price (£)'].sum()
                            summary['sales_count'] = len(today_sales)
        
        # Count active partnerships
        for tab in sheet.worksheets():
            if 'partnership' in tab.title.lower():
                df = pd.DataFrame(tab.get_all_records())
                if 'Status' in df.columns:
                    summary['active_partnerships'] = len(df[df['Status'] == 'Active'])
        
        # Count low stock
        summary['low_stock_count'] = len(check_low_stock())
        
    except Exception as e:
        print(f"Error generating summary: {e}")
    
    return summary

# ────────────────────────────────────────
# 📱 SEND ALERTS (Placeholder)
# ────────────────────────────────────────
def send_telegram_alert(message):
    """Send alert via Telegram (implement when bot is set up)"""
    # TODO: Implement Telegram bot
    print(f"📱 TELEGRAM ALERT: {message}")
    pass

def send_email_alert(subject, body):
    """Send alert via Email (implement when SMTP is configured)"""
    # TODO: Implement email sending
    print(f"📧 EMAIL ALERT - {subject}: {body}")
    pass

# ────────────────────────────────────────
# ⏰ RUN 9AM ALERTS
# ────────────────────────────────────────
def run_morning_alerts():
    """Run all morning alerts (call this at 9am)"""
    print(f"\n{'='*50}")
    print(f"🌅 MORNING ALERTS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*50}\n")
    
    # 1. Daily Summary
    summary = generate_daily_summary()
    if summary:
        print(f"📊 DAILY SUMMARY")
        print(f"   Date: {summary['date']}")
        print(f"   Revenue Today: £{summary['total_revenue']:,.2f}")
        print(f"   Sales Count: {summary['sales_count']}")
        print(f"   Active Partnerships: {summary['active_partnerships']}")
        print(f"   Low Stock Items: {summary['low_stock_count']}")
        print()
    
    # 2. Low Stock Alerts
    low_stock = check_low_stock()
    if low_stock:
        print(f"🚨 LOW STOCK ALERTS ({len(low_stock)} items)")
        for item in low_stock:
            print(f"   ⚠️ {item['product']}: Only {item['stock']} left!")
        print()
    
    # 3. Partnership Alerts
    expiring, pending = check_partnership_pipeline()
    
    if expiring:
        print(f"⏰ EXPIRING PARTNERSHIPS ({len(expiring)})")
        for partner in expiring:
            print(f"   ⏳ {partner['partner']} expires {partner['end_date']} (£{partner['value']})")
        print()
    
    if pending:
        print(f"💼 PENDING DEALS ({len(pending)})")
        for deal in pending:
            print(f"   📋 {deal['partner']}: £{deal['value']} - {deal['stage']}")
        print()
    
    print(f"{'='*50}\n")

# ────────────────────────────────────────
# 🎯 MAIN EXECUTION
# ────────────────────────────────────────
if __name__ == "__main__":
    run_morning_alerts()