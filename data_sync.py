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
    
    if not hasattr(st, 'secrets'):
        # Fallback to local file
        if os.path.exists('shack_credentials.json'):
            try:
                return Credentials.from_service_account_file('shack_credentials.json')
            except Exception as e:
                st.error(f"Error loading local credentials: {e}")
                return None
        return None
    
    try:
        # Try [google_sheets] format first
        if 'google_sheets' in st.secrets:
            secrets = st.secrets['google_sheets']
            
            # Check if it's a JSON blob format
            if 'credentials' in secrets:
                import json
                creds_json = secrets['credentials']
                if isinstance(creds_json, str):
                    try:
                        creds_dict = json.loads(creds_json)
                    except json.JSONDecodeError:
                        # Try to fix common issues
                        creds_json = creds_json.replace('\\n', '\n')
                        creds_dict = json.loads(creds_json)
                else:
                    creds_dict = creds_json
                
                return Credentials.from_service_account_info(creds_dict)
            
            # Try flat format
            else:
                private_key = secrets.get('private_key', '')
                # Handle both escaped and unescaped newlines
                if '\\n' in private_key:
                    private_key = private_key.replace('\\n', '\n')
                
                creds_dict = {
                    "type": secrets.get('type', 'service_account'),
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
        
        # Try [connections.gsheets] format as fallback
        elif 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
            secrets = st.secrets['connections']['gsheets']
            private_key = secrets.get('private_key', '')
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
        
        else:
            st.error("No credentials found in secrets")
            return None
                
    except Exception as e:
        st.error(f"Error loading credentials: {type(e).__name__}: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

def load_live_exchange_data():
    """Load data from Google Sheets - NO DEMO DATA FALLBACK"""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   "Credentials found but invalid. Check Secrets format.")
        
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