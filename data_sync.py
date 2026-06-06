import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# Try to import Google libraries safely
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

def get_google_credentials():
    """Get Google Sheets credentials from Streamlit secrets or local file"""
    
    # Try Streamlit secrets - using official [connections.gsheets] format
    if hasattr(st, 'secrets') and 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
        try:
            secrets = st.secrets['connections']['gsheets']
            
            # Get private key and handle both escaped and unescaped newlines
            private_key = secrets.get('private_key', '')
            
            # If the key contains literal \n, convert to actual newlines
            if '\\n' in private_key:
                private_key = private_key.replace('\\n', '\n')
            
            # Build credentials dict from flat TOML format
            creds_dict = {
                "type": "service_account",
                "project_id": secrets.get('project_id', ''),
                "private_key_id": secrets.get('private_key_id', ''),
                "private_key": private_key,
                "client_email": secrets.get('client_email', ''),
                "client_id": secrets.get('client_id', ''),
                "auth_uri": secrets.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
                "token_uri": secrets.get('token_uri', 'https://oauth2.googleapis.com/token'),
                "auth_provider_x509_cert_url": secrets.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs'),
                "client_x509_cert_url": secrets.get('client_x509_cert_url', ''),
                "universe_domain": secrets.get('universe_domain', 'googleapis.com')
            }
            
            return Credentials.from_service_account_info(creds_dict)
        except Exception as e:
            st.error(f"Error loading credentials from secrets: {e}")
            return None
    
    # Fallback to local file (for local development)
    if os.path.exists('shack_credentials.json'):
        try:
            return Credentials.from_service_account_file('shack_credentials.json')
        except Exception as e:
            st.error(f"Error loading local credentials: {e}")
            return None
    
    return None

def get_demo_data():
    """Return sample data when Google Sheets is unavailable"""
    
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
        'quarter': 'Q2 2026',
        'total_revenue': 2450.00,
        'total_expenses': 1800.00,
        'net_profit': 650.00,
        'events_held': 2,
        'total_attendees': 145
    }
    
    return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict

def load_live_exchange_data():
    """Load data from Google Sheets or return demo data with error message"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        demo_data = get_demo_data()
        return demo_data + ("Google Sheets libraries not installed",)
    
    try:
        creds = get_google_credentials()
        if not creds:
            demo_data = get_demo_data()
            if hasattr(st, 'secrets'):
                return demo_data + ("Credentials found but invalid. Check Secrets format.",)
            else:
                return demo_data + ("Credentials file not found. Running in demo mode.",)
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('connections', {}).get('gsheets', {}).get('spreadsheet', 'Shack_Live_Exchange_Master')
        
        try:
            spreadsheet = gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            demo_data = get_demo_data()
            return demo_data + (f"Spreadsheet '{spreadsheet_name}' not found. Did you share it with the service account?",)
        except Exception as e:
            demo_data = get_demo_data()
            return demo_data + (f"Error opening spreadsheet: {str(e)}",)
        
        try:
            events_sheet = spreadsheet.worksheet("01_Events")
            bookings_sheet = spreadsheet.worksheet("02_Bookings")
            artists_sheet = spreadsheet.worksheet("03_Artists")
            financials_sheet = spreadsheet.worksheet("04_Financials")
            ops_sheet = spreadsheet.worksheet("05_Operations_Log")
            snapshot_sheet = spreadsheet.worksheet("06_Snapshot")
            
            events_df = pd.DataFrame(events_sheet.get_all_records())
            bookings_df = pd.DataFrame(bookings_sheet.get_all_records())
            artists_df = pd.DataFrame(artists_sheet.get_all_records())
            financials_df = pd.DataFrame(financials_sheet.get_all_records())
            ops_df = pd.DataFrame(ops_sheet.get_all_records())
            
            snapshot_data = snapshot_sheet.get_all_values()
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
            demo_data = get_demo_data()
            return demo_data + (f"Worksheet not found: {str(e)}. Make sure sheets are named correctly.",)
        except Exception as e:
            demo_data = get_demo_data()
            return demo_data + (f"Error reading worksheets: {str(e)}",)
        
    except gspread.exceptions.APIError as e:
        demo_data = get_demo_data()
        return demo_data + (f"Google API Error: {str(e)}. Check credentials and permissions.",)
    except Exception as e:
        demo_data = get_demo_data()
        return demo_data + (f"Unexpected error: {str(e)}",)

def update_sheet_data(worksheet, df):
    """Update a Google Sheet with DataFrame data"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return False, "Google Sheets libraries not available"
    
    try:
        creds = get_google_credentials()
        if not creds:
            return False, "Credentials not found"
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('connections', {}).get('gsheets', {}).get('spreadsheet', 'Shack_Live_Exchange_Master')
        spreadsheet = gc.open(spreadsheet_name)
        
        # Clear existing data
        worksheet.clear()
        
        # Update with new data
        worksheet.update([df.columns.tolist()] + df.values.tolist())
        
        return True, "Success"
    except Exception as e:
        return False, f"Error updating sheet: {str(e)}"

def add_booking_to_sheet(booking_data):
    """Add a new booking to Google Sheets"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return False, "Google Sheets libraries not available"
    
    try:
        creds = get_google_credentials()
        if not creds:
            return False, "Credentials not found"
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('connections', {}).get('gsheets', {}).get('spreadsheet', 'Shack_Live_Exchange_Master')
        spreadsheet = gc.open(spreadsheet_name)
        bookings_sheet = spreadsheet.worksheet("02_Bookings")
        
        # Append new row
        bookings_sheet.append_row([
            booking_data.get('Booking_ID', ''),
            booking_data.get('Event_ID', ''),
            booking_data.get('Customer_Name', ''),
            booking_data.get('Ticket_Type', ''),
            booking_data.get('Quantity', ''),
            booking_data.get('Unit_Price', ''),
            booking_data.get('Total_Price', ''),
            booking_data.get('Booking_Date', ''),
            booking_data.get('Payment_Status', '')
        ])
        
        return True, "Booking added successfully"
    except Exception as e:
        return False, f"Error adding booking: {str(e)}"

def log_operation(action, user, details):
    """Log an operation to the operations sheet"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return False, "Google Sheets libraries not available"
    
    try:
        creds = get_google_credentials()
        if not creds:
            return False, "Credentials not found"
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('connections', {}).get('gsheets', {}).get('spreadsheet', 'Shack_Live_Exchange_Master')
        spreadsheet = gc.open(spreadsheet_name)
        ops_sheet = spreadsheet.worksheet("05_Operations_Log")
        
        # Append new log entry
        ops_sheet.append_row([
            datetime.now().strftime('%Y-%m-%d'),
            action,
            user,
            details
        ])
        
        return True, "Operation logged"
    except Exception as e:
        return False, f"Error logging operation: {str(e)}"