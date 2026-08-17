"""List all spreadsheets accessible to the Shack_Project OAuth account."""

import gspread
import json
from google.oauth2.credentials import Credentials as UserCredentials

with open('configs/token.json') as f:
    token = json.load(f)
with open('configs/credentials.json') as f:
    creds_data = json.load(f)['installed']

user_creds = UserCredentials(
    token=token['token'],
    refresh_token=token.get('refresh_token'),
    token_uri=token['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret'],
    scopes=token['scopes']
)

gc = gspread.authorize(user_creds)

print('=== All Accessible Spreadsheets ===')
for s in gc.list_spreadsheet_files():
    print(f'  {s["name"]}  (id: {s["id"][:30]}...)')

print()
print('=== Checking each master sheet ===')

master_sheets = [
    'Shack_Live_Exchange_Master',
    'Artists_Unlimited_Master',
    'Shack_News_Network_Master',
    'Shack_Financial_Overview_Master',
]

for name in master_sheets:
    try:
        ss = gc.open(name)
        ws_list = [w.title for w in ss.worksheets()]
        print(f'\n{name}:')
        for w in ws_list:
            print(f'  - {w}')
    except Exception as e:
        print(f'\n{name}: NOT FOUND or ERROR - {e}')
