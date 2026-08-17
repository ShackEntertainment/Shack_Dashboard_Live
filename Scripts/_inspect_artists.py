"""Inspect Artists sheet column structure"""
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

ss = gc.open('Shack_Live_Exchange_Master')
ws = ss.worksheet('03_Artist_Talent')
records = ws.get_all_records()
print(f"Total rows: {len(records)}")
print(f"Columns ({len(records[0]) if records else 0}): {list(records[0].keys()) if records else []}")
if records:
    print(f"Row 1: {records[0]}")
