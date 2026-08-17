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
    """Get Google Sheets credentials - tries OAuth first, then service account, then secrets"""
    
    # PRIORITY 1: Use OAuth credentials (token.json + credentials.json)
    project_root = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(project_root, 'configs', 'token.json')
    creds_path = os.path.join(project_root, 'configs', 'credentials.json')
    
    if os.path.exists(token_path) and os.path.exists(creds_path):
        try:
            from google.oauth2.credentials import Credentials as UserCredentials
            from google.auth.transport.requests import Request
            
            token_data = json.load(open(token_path))
            creds_raw = json.load(open(creds_path)).get('installed', {})
            
            # Use scopes from token.json if available, otherwise default to both spreadsheets + drive
            token_scopes = token_data.get('scopes', [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ])

            user_creds = UserCredentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=creds_raw.get('client_id', ''),
                client_secret=creds_raw.get('client_secret', ''),
                scopes=token_scopes
            )
            
            # Auto-refresh if expired
            if user_creds.expired:
                user_creds.refresh(Request())
                # Save refreshed token
                token_data['token'] = user_creds.token
                if user_creds.refresh_token:
                    token_data['refresh_token'] = user_creds.refresh_token
                json.dump(token_data, open(token_path, 'w'), indent=2)
            
            return user_creds
        except Exception as e:
            # Silently fail - pages will use demo data fallback
            pass
    
    # PRIORITY 2: Service account file
    if os.path.exists('shack_credentials.json'):
        try:
            return Credentials.from_service_account_file('shack_credentials.json')
        except Exception as e:
            pass  # Silently fail - try next method

    # PRIORITY 3: Streamlit secrets (for cloud deployment)
    if hasattr(st, 'secrets'):
        try:
            # Official Streamlit format: [connections.gsheets]
            if 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
                secrets = st.secrets['connections']['gsheets']

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

            # Fallback: Try [google_sheets] format
            elif 'google_sheets' in st.secrets:
                secrets = st.secrets['google_sheets']

                if 'credentials_b64' in secrets:
                    b64_string = secrets['credentials_b64']
                    json_string = base64.b64decode(b64_string).decode('utf-8')
                    creds_dict = json.loads(json_string)
                    return Credentials.from_service_account_info(creds_dict)

                elif 'credentials' in secrets:
                    creds_json = secrets['credentials']
                    if isinstance(creds_json, str):
                        creds_dict = json.loads(creds_json)
                    else:
                        creds_dict = creds_json
                    return Credentials.from_service_account_info(creds_dict)

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
            return None  # Silently fail - pages will use demo data

def _strip_blank_columns(df):
    """Remove columns with no header (blank column names)"""
    if df.empty:
        return df
    return df[[c for c in df.columns if c and str(c).strip() != '']]


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
                   "Failed to load Google credentials. Check configs/token.json and configs/credentials.json.")
        
        gc = gspread.authorize(creds)
        
        # Get spreadsheet name from secrets (safe access — no secrets.toml required)
        spreadsheet_name = 'Shack_Live_Exchange_Master'
        try:
            if hasattr(st, 'secrets') and 'connections' in st.secrets and 'gsheets' in st.secrets['connections']:
                spreadsheet_name = st.secrets['connections']['gsheets'].get('spreadsheet', 'Shack_Live_Exchange_Master')
            elif hasattr(st, 'secrets') and 'google_sheets' in st.secrets:
                spreadsheet_name = st.secrets['google_sheets'].get('spreadsheet_name', 'Shack_Live_Exchange_Master')
        except Exception:
            pass  # No secrets.toml — use default
        
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

            # Strip blank column headers (unnamed columns with no header row value)
            events_df = _strip_blank_columns(events_df)
            bookings_df = _strip_blank_columns(bookings_df)
            artists_df = _strip_blank_columns(artists_df)
            financials_df = _strip_blank_columns(financials_df)
            ops_df = _strip_blank_columns(ops_df)
            
            # Read snapshot data — the sheet is a formatted report, not a table.
            # Parse by row labels to extract key metrics.
            snapshot_dict = {}
            if snapshot_sheet:
                try:
                    raw = snapshot_sheet.get_all_values()
                    # Build a label -> value lookup from the sheet
                    label_col = 0   # Column A holds the row label
                    val_col   = 2   # Column C holds the actual value (after 'Target' in col B)

                    def get(label, col=val_col, row_idx=None, is_float=True):
                        """Find a row starting with `label` and return its column value."""
                        for i, row in enumerate(raw):
                            cell = str(row[label_col]).strip() if label_col < len(row) else ''
                            if cell.startswith(label):
                                if row_idx is not None and i != row_idx:
                                    continue
                                val_str = row[col].strip() if col < len(row) else ''
                                # Strip leading currency symbols
                                val_str = val_str.replace('£', '').replace(',', '').replace('%', '')
                                if not val_str:
                                    return None
                                try:
                                    return float(val_str) if is_float else val_str
                                except ValueError:
                                    return val_str
                        return None

                    def get_int(label):
                        v = get(label, is_float=True)
                        return int(v) if v is not None else 0

                    def get_float(label):
                        v = get(label, is_float=True)
                        return float(v) if v is not None else 0.0

                    # Quarter label is on row 1 in col A
                    quarter = raw[1][1].strip() if len(raw) > 1 and len(raw[1]) > 1 else 'N/A'

                    snapshot_dict = {
                        'quarter':         quarter,
                        'total_revenue':   get_float('Total Revenue'),
                        'total_expenses':  get_float('Total Expenses'),
                        'net_profit':      get_float('NET PROFIT'),
                        'events_held':     get_int('Total Events Hosted'),
                        'total_attendees': get_int('Total Capacity Sold'),
                        # Bonus fields
                        'shack_commission': get_float('Shack Commission (30%)'),
                        'artist_payouts':   get_float('Total Artist Payouts (70%)'),
                        'active_alerts':    get_int('Active Alerts'),
                        'refund_rate':      get_float('Refund Rate'),
                    }
                except Exception:
                    snapshot_dict = {}
            
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


def load_artists_unlimited_data():
    """Load data from Artists_Unlimited_Master — Artists, Inventory, Outlets, Partnerships, Sales."""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               pd.DataFrame(), pd.DataFrame(),
               "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   pd.DataFrame(), pd.DataFrame(),
                   "Failed to load Google credentials. Check configs/token.json and configs/credentials.json.")
        
        gc = gspread.authorize(creds)
        
        try:
            spreadsheet = gc.open("Artists_Unlimited_Master")
        except gspread.exceptions.SpreadsheetNotFound:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   pd.DataFrame(), pd.DataFrame(),
                   "Spreadsheet 'Artists_Unlimited_Master' not found. Share it with your OAuth email.")
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   pd.DataFrame(), pd.DataFrame(),
                   f"Cannot access spreadsheet: {str(e)}")
        
        def ws(names):
            for n in names:
                try:
                    return spreadsheet.worksheet(n)
                except gspread.exceptions.WorksheetNotFound:
                    continue
            return None
        
        artists_ws    = ws(['🎨Artists', 'Artists'])
        inventory_ws  = ws(['InventoryData'])
        outlets_ws    = ws(['🏪 Product Sales Outlets', 'Product Sales Outlets'])
        sales_ws      = ws(['💰 Sales', 'Sales'])
        partners_ws   = ws(['🤝 Partnerships', 'Partnerships'])
        
        def read_records(worksheet):
            if worksheet is None:
                return pd.DataFrame()
            try:
                return pd.DataFrame(worksheet.get_all_records(expected_headers=[]))
            except Exception:
                return pd.DataFrame(worksheet.get_all_records())
        
        artists_df   = _strip_blank_columns(read_records(artists_ws))
        inventory_df = _strip_blank_columns(read_records(inventory_ws))
        outlets_df   = _strip_blank_columns(read_records(outlets_ws))
        sales_df     = _strip_blank_columns(read_records(sales_ws))
        partners_df  = _strip_blank_columns(read_records(partners_ws))
        
        return artists_df, inventory_df, outlets_df, sales_df, partners_df, None
        
    except gspread.exceptions.APIError as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               pd.DataFrame(), pd.DataFrame(),
               f"Google API Error: {str(e)}")
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               pd.DataFrame(), pd.DataFrame(),
               f"Unexpected error: {type(e).__name__}: {str(e)}")


def load_news_network_data():
    """Load data from Shack_News_Network_Master."""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               pd.DataFrame(), pd.DataFrame(), {},
               "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   pd.DataFrame(), pd.DataFrame(), {},
                   "Failed to load Google credentials.")
        
        gc = gspread.authorize(creds)
        
        try:
            spreadsheet = gc.open("Shack_News_Network_Master")
        except gspread.exceptions.SpreadsheetNotFound:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   pd.DataFrame(), pd.DataFrame(), {},
                   "Spreadsheet 'Shack_News_Network_Master' not found.")
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
                   pd.DataFrame(), pd.DataFrame(), {},
                   f"Cannot access spreadsheet: {str(e)}")
        
        def ws(names):
            for n in names:
                try:
                    return spreadsheet.worksheet(n)
                except gspread.exceptions.WorksheetNotFound:
                    continue
            return None
        
        content_ws   = ws(['01_Content_Library'])
        youtube_ws   = ws(['02_Youtube_Analytics'])
        social_ws    = ws(['03_Social_Media_Metrics'])
        referral_ws  = ws(['04_Referral_Monetization'])
        campaign_ws  = ws(['05_Campaign_Tracking'])
        snapshot_ws  = ws(['06_Snapshot'])
        
        def read_records(worksheet):
            if worksheet is None:
                return pd.DataFrame()
            try:
                return pd.DataFrame(worksheet.get_all_records(expected_headers=[]))
            except Exception:
                return pd.DataFrame(worksheet.get_all_records())
        
        content_df  = read_records(content_ws)
        youtube_df  = read_records(youtube_ws)
        social_df   = read_records(social_ws)
        referral_df = read_records(referral_ws)
        campaign_df = read_records(campaign_ws)
        
        snapshot_dict = {}
        if snapshot_ws:
            try:
                raw = snapshot_ws.get_all_values()
                if len(raw) > 1:
                    snapshot_dict = dict(zip(
                        [c.strip() for c in raw[0]],
                        [c.strip() for c in raw[1]]
                    ))
            except Exception:
                pass
        
        return content_df, youtube_df, social_df, referral_df, campaign_df, snapshot_dict, None
        
    except gspread.exceptions.APIError as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               pd.DataFrame(), pd.DataFrame(), {},
               f"Google API Error: {str(e)}")
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(),
               pd.DataFrame(), pd.DataFrame(), {},
               f"Unexpected error: {type(e).__name__}: {str(e)}")


def load_financial_overview_data():
    """Load data from Shack_Financial_Overview_Master."""
    
    if not GOOGLE_SHEETS_AVAILABLE:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
               "Google Sheets libraries not installed")
    
    try:
        creds = get_google_credentials()
        if not creds:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
                   "Failed to load Google credentials.")
        
        gc = gspread.authorize(creds)
        
        try:
            spreadsheet = gc.open("Shack_Financial_Overview_Master")
        except gspread.exceptions.SpreadsheetNotFound:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
                   "Spreadsheet 'Shack_Financial_Overview_Master' not found.")
        except Exception as e:
            return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
                   f"Cannot access spreadsheet: {str(e)}")
        
        def ws(names):
            for n in names:
                try:
                    return spreadsheet.worksheet(n)
                except gspread.exceptions.WorksheetNotFound:
                    continue
            return None
        
        revenue_ws   = ws(['01_Revenue_Streams'])
        expense_ws   = ws(['02_Expense_Breakdown'])
        cashflow_ws  = ws(['03_Cash_Flow'])
        snapshot_ws  = ws(['04_Snapshot'])
        
        def read_records(worksheet):
            if worksheet is None:
                return pd.DataFrame()
            try:
                return pd.DataFrame(worksheet.get_all_records(expected_headers=[]))
            except Exception:
                return pd.DataFrame(worksheet.get_all_records())
        
        revenue_df  = read_records(revenue_ws)
        expense_df  = read_records(expense_ws)
        cashflow_df = read_records(cashflow_ws)
        
        snapshot_dict = {}
        if snapshot_ws:
            try:
                raw = snapshot_ws.get_all_values()
                if len(raw) > 1:
                    snapshot_dict = dict(zip(
                        [c.strip() for c in raw[0]],
                        [c.strip() for c in raw[1]]
                    ))
            except Exception:
                pass
        
        return revenue_df, expense_df, cashflow_df, snapshot_dict, None
        
    except gspread.exceptions.APIError as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
               f"Google API Error: {str(e)}")
    except Exception as e:
        return (pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {},
               f"Unexpected error: {type(e).__name__}: {str(e)}")