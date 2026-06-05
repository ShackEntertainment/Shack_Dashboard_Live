import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

def get_google_credentials():
    if hasattr(st, 'secrets') and 'google_sheets' in st.secrets:
        try:
            creds_json = st.secrets['google_sheets']['credentials']
            creds_dict = json.loads(creds_json)
            return Credentials.from_service_account_info(creds_dict)
        except Exception as e:
            return None
    if os.path.exists('shack_credentials.json'):
        try:
            return Credentials.from_service_account_file('shack_credentials.json')
        except Exception:
            return None
    return None

def get_demo_data():
    events_df = pd.DataFrame({
        'Event_Name': ['Summer Rooftop Jam', 'Underground Bass Night', 'Jazz & Canvas Gala', 'Neon Folk Session'],
        'Event_Date': ['2026-06-15', '2026-06-22', '2026-07-05', '2026-07-12'],
        'Status': ['On Sale', 'Planning', 'On Sale', 'Planning'],
        'Capacity_Total': [150, 80, 200, 40],
        'Capacity_Remaining': [150, 80, 200, 40],
        'Tickets_Sold': [0, 0, 0, 0]
    })
    bookings_df = pd.DataFrame({
        'Booking_ID': ['BK001', 'BK002', 'BK003', 'BK004', 'BK005', 'BK006'],
        'Event_ID': [1, 1, 2, 3, 3, 4],
        'Customer_Name': ['Alice Johnson', 'Bob Smith', 'Carol White', 'David Brown', 'Emma Davis', 'Frank Wilson'],
        'Ticket_Type': ['General Admission', 'VIP', 'General Admission', 'General Admission', 'VIP', 'General Admission'],
        'Quantity': [2, 1, 4, 1, 2, 3],
        'Unit_Price': [25.00, 75.00, 20.00, 30.00, 75.00, 25.00],
        'Total_Price': [50.00, 75.00, 80.00, 30.00, 150.00, 75.00],
        'Booking_Date': ['2026-05-01', '2026-05-03', '2026-05-05', '2026-05-07', '2026-05-10', '2026-05-12'],
        'Payment_Status': ['Paid', 'Paid', 'Pending', 'Paid', 'Paid', 'Pending']
    })
    artists_df = pd.DataFrame({
        'Artist_Name': ['DJ Kemet', 'Maya Strings', 'Bass Collective', 'Jazz Fusion Trio', 'Folk Revival', 'Electronic Soul'],
        'Discipline': ['DJ/Producer', 'Visual Artist', 'DJ/Producer', 'Music', 'Music', 'Music'],
        'Fee_Type': ['Fixed', 'Commission', 'Fixed', 'Fixed', 'Fixed', 'Fixed'],
        'Fee_Amount': [500.00, 0.00, 300.00, 800.00, 400.00, 350.00],
        'Payment_Status': ['Paid', 'N/A', 'Pending', 'Deposit Paid', 'Pending', 'Pending']
    })
    financials_df = pd.DataFrame({
        'Transaction_ID': ['TXN001', 'TXN002', 'TXN003', 'TXN004', 'TXN005'],
        'Date': ['2026-05-01', '2026-05-05', '2026-05-10', '2026-05-15', '2026-05-20'],
        'Description': ['Ticket Sales - Rooftop Jam', 'Venue Deposit', 'Artist Fee - DJ Kemet', 'Marketing', 'Equipment Rental'],
        'Category': ['Revenue', 'Expense', 'Expense', 'Expense', 'Expense'],
        'Amount_In': [450.00, 0.00, 0.00, 0.00, 0.00],
        'Amount_Out': [0.00, 200.00, 500.00, 150.00, 300.00],
        'Event_Link': ['Summer Rooftop Jam', 'Summer Rooftop Jam', 'Summer Rooftop Jam', 'General', 'General']
    })
    ops_df = pd.DataFrame({
        'Date': ['2026-05-01', '2026-05-05', '2026-05-10'],
        'Action': ['Event Created', 'Venue Booked', 'Artist Confirmed'],
        'User': ['Admin', 'Admin', 'Admin'],
        'Details': ['Summer Rooftop Jam created', 'Rooftop venue secured', 'DJ Kemet confirmed']
    })
    snapshot_dict = {
        'quarter': 'Q2 2026', 'total_revenue': 2450.00, 'total_expenses': 1800.00,
        'net_profit': 650.00, 'events_held': 2, 'total_attendees': 145
    }
    return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict

def load_live_exchange_data():
    if not GOOGLE_SHEETS_AVAILABLE:
        return get_demo_data() + ("Google Sheets libraries not installed",)
    
    try:
        creds = get_google_credentials()
        if not creds:
            return get_demo_data() + ("Credentials not found. Add them to Streamlit Secrets or local shack_credentials.json.",)
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('google_sheets', {}).get('spreadsheet_name', 'Shack_Live_Exchange_Master')
        
        try:
            spreadsheet = gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            return get_demo_data() + (f"Spreadsheet '{spreadsheet_name}' not found. Share it with the service account email.",)
        except Exception as e:
            return get_demo_data() + (f"Auth error: {str(e)}. Enable Google Sheets API in Google Cloud Console.",)
        
        try:
            events_df = pd.DataFrame(spreadsheet.worksheet("01_Events").get_all_records())
            bookings_df = pd.DataFrame(spreadsheet.worksheet("02_Bookings").get_all_records())
            artists_df = pd.DataFrame(spreadsheet.worksheet("03_Artists").get_all_records())
            financials_df = pd.DataFrame(spreadsheet.worksheet("04_Financials").get_all_records())
            ops_df = pd.DataFrame(spreadsheet.worksheet("05_Operations_Log").get_all_records())
            snapshot_data = spreadsheet.worksheet("06_Snapshot").get_all_values()
            snapshot_dict = {
                'quarter': snapshot_data[1][0] if len(snapshot_data) > 1 else 'N/A',
                'total_revenue': float(snapshot_data[1][1]) if len(snapshot_data) > 1 and snapshot_data[1][1] else 0.0,
                'total_expenses': float(snapshot_data[1][2]) if len(snapshot_data) > 1 and snapshot_data[1][2] else 0.0,
                'net_profit': float(snapshot_data[1][3]) if len(snapshot_data) > 1 and snapshot_data[1][3] else 0.0,
                'events_held': int(snapshot_data[1][4]) if len(snapshot_data) > 1 and snapshot_data[1][4] else 0,
                'total_attendees': int(snapshot_data[1][5]) if len(snapshot_data) > 1 and snapshot_data[1][5] else 0
            }
            return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, None
        except gspread.exceptions.WorksheetNotFound as e:
            return get_demo_data() + (f"Worksheet missing: {str(e)}",)
        except Exception as e:
            return get_demo_data() + (f"Data read error: {str(e)}",)
    except Exception as e:
        return get_demo_data() + (f"Connection failed: {str(e)}",)