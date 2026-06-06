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
    """Get Google Sheets credentials from Streamlit secrets using [connections.gsheets] format"""
    
    if not hasattr(st, 'secrets'):
        if os.path.exists('shack_credentials.json'):
            try:
                return Credentials.from_service_account_file('shack_credentials.json')
            except Exception as e:
                st.error(f"Error loading local credentials: {e}")
                return None
        return None
    
    try:
        # Official Streamlit format: [connections.gsheets]
        if 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
            secrets = st.secrets['connections']['gsheets']
            
            # Extract private key - TOML triple quotes preserve actual newlines
            private_key = secrets.get('private_key', '')
            
            creds_dict = {
                "type": secrets.get('type', 'service_account'),
                "project_id": secrets.get('project_id', ''),
                "private_key_id": secrets.get('private_key_id', ''),
                "private_key": private_key,  # Already has real newlines from TOML
                "client_email": secrets.get('client_email', ''),
                "client_id": secrets.get('client_id', ''),
                "auth_uri": secrets.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
                "token_uri": secrets.get('token_uri', 'https://oauth2.googleapis.com/token'),
                "auth_provider_x509_cert_url": secrets.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs'),
                "client_x509_cert_url": secrets.get('client_x509_cert_url', ''),
                "universe_domain": secrets.get('universe_domain', 'googleapis.com')
            }
            
            return Credentials.from_service_account_info(creds_dict)
        
        return None
    except Exception as e:
        st.error(f"Error loading credentials: {type(e).__name__}: {e}")
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
                   "Failed to load credentials. Check Streamlit secrets.")
        
        gc = gspread.authorize(creds)
        spreadsheet_name = st.secrets.get('connections', {}).get('gsheets', {}).get('spreadsheet', 'Shack_Live_Exchange_Master')
        
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