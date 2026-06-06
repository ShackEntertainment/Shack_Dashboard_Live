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
    """Get Google Sheets credentials from Streamlit secrets using official pattern"""
    
    if not hasattr(st, 'secrets'):
        # Fallback to local file for development
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
            
            # Ensure the key has proper line breaks
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
        
        # Fallback: Try [google_sheets] format
        elif 'google_sheets' in st.secrets:
            secrets = st.secrets['google_sheets']
            
            # Try base64 format
            if 'credentials_b64' in secrets:
                b64_string = secrets['credentials_b64']
                json_string = base64.b64decode(b64_string).decode('utf-8')
                creds_dict = json.loads(json_string)
                return Credentials.from_service_account_info(creds_dict)
            
            # Try JSON string format
            elif 'credentials' in secrets:
                creds_json = secrets['credentials']
                if isinstance(creds_json, str):
                    creds_dict = json.loads(creds_json)
                else:
                    creds_dict = creds_json
                return Credentials.from_service_account_info(creds_dict)
            
            # Try flat format
            else:
                private_key = secrets.get('private_key', '')
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
        
        return None
    except Exception as e:
        st.error(f"Error loading credentials: {type(e).__name__}: {e}")
        import traceback
        st.error(traceback.format_exc())
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
        
        # Get spreadsheet name from secrets
        spreadsheet_name = None
        if 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
            spreadsheet_name = st.secrets['connections']['gsheets'].get('spreadsheet', 'Shack_Live_Exchange_Master')
        elif 'google_sheets' in st.secrets:
            spreadsheet_name = st.secrets['google_sheets'].get('spreadsheet_name', 'Shack_Live_Exchange_Master')
        else:
            spreadsheet_name = 'Shack_Live_Exchange_Master'
        
        try:
            spreadsheet = gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Spreadsheet '{spreadsheet_name}' not found. Share it with your service account email.")
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Cannot access spreadsheet: {str(e)}")
        
        try:
            # Try to open worksheets with flexible naming
            worksheet_names = {
                'events': ['01_Events', 'Events', '01_Events_Master'],
                'bookings': ['02_Bookings', 'Bookings', '02_Ticket_Bookings'],
                'artists': ['03_Artists', 'Artists', '03_Artist_Talent'],
                'financials': ['04_Financials', 'Financials', '04_Revenue_Financials'],
                'ops': ['05_Operations_Log', 'Operations', '05_Operations_Log'],
                'snapshot': ['06_Snapshot', 'Snapshot', '07_Quarterly_Snapshot']
            }
            
            def get_worksheet(spreadsheet, possible_names):
                for name in possible_names:
                    try:
                        return spreadsheet.worksheet(name)
                    except gspread.exceptions.WorksheetNotFound:
                        continue
                return None
            
            events_sheet = get_worksheet(spreadsheet, worksheet_names['events'])
            bookings_sheet = get_worksheet(spreadsheet, worksheet_names['bookings'])
            artists_sheet = get_worksheet(spreadsheet, worksheet_names['artists'])
            financials_sheet = get_worksheet(spreadsheet, worksheet_names['financials'])
            ops_sheet = get_worksheet(spreadsheet, worksheet_names['ops'])
            snapshot_sheet = get_worksheet(spreadsheet, worksheet_names['snapshot'])
            
            # Read data from each sheet
            events_df = pd.DataFrame(events_sheet.get_all_records()) if events_sheet else pd.DataFrame()
            bookings_df = pd.DataFrame(bookings_sheet.get_all_records()) if bookings_sheet else pd.DataFrame()
            artists_df = pd.DataFrame(artists_sheet.get_all_records()) if artists_sheet else pd.DataFrame()
            financials_df = pd.DataFrame(financials_sheet.get_all_records()) if financials_sheet else pd.DataFrame()
            ops_df = pd.DataFrame(ops_sheet.get_all_records()) if ops_sheet else pd.DataFrame()
            
            # Read snapshot data
            snapshot_dict = {}
            if snapshot_sheet:
                snapshot_data = snapshot_sheet.get_all_values()
                if len(snapshot_data) > 1:
                    snapshot_dict = {
                        'quarter': snapshot_data[1][0] if len(snapshot_data[1]) > 0 else 'N/A',
                        'total_revenue': float(snapshot_data[1][1]) if len(snapshot_data[1]) > 1 and snapshot_data[1][1] else 0.0,
                        'total_expenses': float(snapshot_data[1][2]) if len(snapshot_data[1]) > 2 and snapshot_data[1][2] else 0.0,
                        'net_profit': float(snapshot_data[1][3]) if len(snapshot_data[1]) > 3 and snapshot_data[1][3] else 0.0,
                        'events_held': int(snapshot_data[1][4]) if len(snapshot_data[1]) > 4 and snapshot_data[1][4] else 0,
                        'total_attendees': int(snapshot_data[1][5]) if len(snapshot_data[1]) > 5 and snapshot_data[1][5] else 0
                    }
            
            return events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, None
            
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
                   pd.DataFrame(), pd.DataFrame(), {}, 
                   f"Error reading worksheets: {str(e)}")
        
    except gspread.exceptions.APIError as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               f"Google API Error: {str(e)}. Check service account permissions.")
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), 
               pd.DataFrame(), pd.DataFrame(), {}, 
               f"Unexpected error: {type(e).__name__}: {str(e)}")