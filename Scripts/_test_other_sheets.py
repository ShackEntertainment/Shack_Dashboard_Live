"""Test remaining 3 spreadsheets one by one"""
import sys
import os
import json
import gspread
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(PROJECT_ROOT, 'configs', 'token.json')
CREDS_PATH = os.path.join(PROJECT_ROOT, 'configs', 'credentials.json')

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

TARGETS = [
    ('Artists_Unlimited_Master', ['01_Artists', 'Artists', 'Artists_List']),
    ('Shack_News_Network_Master', ['01_News', 'News', 'Articles']),
    ('Shack_Financial_Overview_Master', ['01_Financials', 'Financials', 'Overview']),
]

for name, _ in TARGETS:
    print(f"\n=== {name} ===")
    try:
        ss = gc.open(name)
        wss = ss.worksheets()
        print(f"Worksheets ({len(wss)}): {', '.join([w.title for w in wss])}")
        for ws in wss[:3]:  # First 3 sheets only
            try:
                records = ws.get_all_records()
                print(f"  [{ws.title}] {len(records)} rows, cols: {list(records[0].keys())[:5] if records else 'empty'}")
            except Exception as e:
                etype = type(e).__name__
                if 'duplicates' in str(e).lower():
                    print(f"  [{ws.title}] DUPLICATE HEADERS - will need expected_headers fix")
                else:
                    print(f"  [{ws.title}] ERROR: {etype}: {e}")
    except Exception as e:
        print(f"OPEN FAILED: {type(e).__name__}: {e}")

print("\nDone.")
