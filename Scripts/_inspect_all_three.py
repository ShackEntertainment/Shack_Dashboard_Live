"""Inspect all three spreadsheets — tabs, columns, row counts"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gspread
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request

TOKEN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs', 'token.json')
CREDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs', 'credentials.json')

with open(TOKEN_PATH) as f:
    token_data = json.load(f)
creds_raw = json.load(open(CREDS_PATH)).get('installed', {})
user_creds = UserCredentials(
    token=token_data.get('token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=creds_raw.get('client_id', ''),
    client_secret=creds_raw.get('client_secret', ''),
    scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/spreadsheets'])
)
if user_creds.expired:
    user_creds.refresh(Request())
gc = gspread.authorize(user_creds)

for ss_name in [
    'Artists_Unlimited_Master',
    'Shack_News_Network_Master',
    'Shack_Financial_Overview_Master'
]:
    try:
        ss = gc.open(ss_name)
        print(f"\n{'='*60}")
        print(f"SPREADSHEET: {ss_name}")
        print(f"URL: {ss.url}")
        sheets = ss.worksheets()
        print(f"Sheets ({len(sheets)}): {[s.title for s in sheets]}")
        for ws in sheets:
            try:
                vals = ws.get_all_values()
                headers = vals[0] if vals else []
                data_rows = len([r for r in vals[1:] if any(str(c).strip() for c in r)]) if len(vals) > 1 else 0
                print(f"\n  TAB: '{ws.title}'")
                print(f"    Rows: {len(vals)} total, {data_rows} data rows")
                print(f"    Cols ({len(headers)}): {headers[:15]}")
                if len(headers) > 15:
                    print(f"    Extra cols: {headers[15:]}")
                # Show first data row if exists
                if len(vals) > 1:
                    data_row = next((r for r in vals[1:] if any(str(c).strip() for c in r)), None)
                    if data_row:
                        print(f"    Row 1: {data_row[:10]}")
            except Exception as e:
                print(f"\n  TAB: '{ws.title}' — ERROR: {e}")
    except Exception as e:
        print(f"\nSPREADSHEET: {ss_name} — OPEN ERROR: {e}")
