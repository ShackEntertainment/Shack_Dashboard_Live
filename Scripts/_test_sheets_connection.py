"""Test Google Sheets connection — one sheet at a time"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gspread
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.transport.requests import Request

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(PROJECT_ROOT, 'configs', 'token.json')
CREDS_PATH = os.path.join(PROJECT_ROOT, 'configs', 'credentials.json')

def p(label, value=None):
    """Print without emoji to avoid Windows cp1252 encoding errors"""
    if value is not None:
        print(f"{label}: {value}")
    else:
        print(label)

p("=== Step 1: Load token.json ===")
with open(TOKEN_PATH) as f:
    token_data = json.load(f)
p("Token expiry", token_data.get('expiry', 'N/A'))
p("Scopes", token_data.get('scopes', []))
p("Has refresh_token", bool(token_data.get('refresh_token')))

p("=== Step 2: Build credentials ===")
creds_raw = json.load(open(CREDS_PATH)).get('installed', {})
user_creds = UserCredentials(
    token=token_data.get('token'),
    refresh_token=token_data.get('refresh_token'),
    token_uri='https://oauth2.googleapis.com/token',
    client_id=creds_raw.get('client_id', ''),
    client_secret=creds_raw.get('client_secret', ''),
    scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/spreadsheets'])
)
p("Expired", user_creds.expired)
p("Valid", user_creds.valid)

p("=== Step 3: Refresh if needed ===")
if user_creds.expired or not user_creds.valid:
    p("Token expired - refreshing...")
    try:
        user_creds.refresh(Request())
        p("Refresh SUCCESS")
        token_data['token'] = user_creds.token
        if user_creds.refresh_token:
            token_data['refresh_token'] = user_creds.refresh_token
        token_data['expiry'] = user_creds.expiry.isoformat()
        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
        p("New expiry", token_data['expiry'])
    except Exception as e:
        p(f"REFRESH FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
else:
    p("Token still valid")

p("=== Step 4: Authorize gspread ===")
try:
    gc = gspread.authorize(user_creds)
    p("gspread authorized OK")
except Exception as e:
    p(f"gspread auth FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

p("=== Step 5: List spreadsheets ===")
try:
    spreadsheets = gc.openall()
    p(f"Found {len(spreadsheets)} spreadsheets:")
    for s in spreadsheets:
        print(f"  - {s.title} ({s.id})")
except Exception as e:
    p(f"List FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

p("=== Step 6: Open Shack_Live_Exchange_Master ===")
try:
    ss = gc.open('Shack_Live_Exchange_Master')
    p(f"Opened: {ss.title}")
    worksheets = ss.worksheets()
    p(f"Worksheets ({len(worksheets)}):")
    for ws in worksheets:
        print(f"  - {ws.title}")
except Exception as e:
    p(f"Open FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

p("=== Step 7: Read each worksheet ===")
for ws in worksheets:
    name = ws.title
    try:
        records = ws.get_all_records()
        p(f"  [{name}] rows={len(records)}")
        if records:
            print(f"    Columns: {list(records[0].keys())[:6]}")
    except Exception as e:
        p(f"  [{name}] READ FAILED: {type(e).__name__}: {e}")

p("=== ALL STEPS PASSED ===")
