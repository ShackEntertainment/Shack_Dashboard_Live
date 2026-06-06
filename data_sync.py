import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import base64

# Try to import Google libraries safely
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

def get_google_credentials():
    """Get Google Sheets credentials from Streamlit secrets"""
    
    if not hasattr(st, 'secrets') or 'google_sheets' not in st.secrets:
        return None
    
    try:
        secrets = st.secrets['google_sheets']
        
        # 1. Try the Base64 format (Best for Streamlit Cloud)
        if 'credentials_b64' in secrets:
            b64_string = secrets['credentials_b64']
            # Decode base64 to string, then string to JSON
            json_string = base64.b64decode(b64_string).decode('utf-8')
            creds_dict = json.loads(json_string)
            return Credentials.from_service_account_info(creds_dict)
        
        # 2. Fallback to JSON String format
        elif 'credentials' in secrets:
            creds_json = secrets['credentials']
            creds_dict = json.loads(creds_json)
            return Credentials.from_service_account_info(creds_dict)
            
        # 3. Fallback to Flat format (with newline handling)
        else:
            private_key = secrets.get('private_key', '')
            # If newlines are escaped, convert them
            if '\\n' in private_key:
                private_key = private_key.replace('\\n', '\n')
            
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
        st.error(f"Error loading credentials: {e}")
        return None

def load_live_exchange_data():
    """Load data from Google Sheets"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   "Failed to load credentials.")
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('google_sheets', {}).get('spreadsheet_name', 'Shack_Live_Exchange_Master')
        
        try:
            spreadsheet = gc.open(spreadsheet_name)
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Cannot access spreadsheet: {str(e)}")
        
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
            
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Error reading worksheets: {str(e)}")
        
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               f"Error: {str(e)}")