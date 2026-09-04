import os, gspread
from google.oauth2.service_account import Credentials
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
SA_FILE = os.path.join(project_root, 'configs', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
AU_WB = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'
creds = Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
wb = gc.open_by_key(AU_WB)
ws = next(w for w in wb.worksheets() if 'inventory' in w.title.lower())
body = {'requests': [{'setDataValidation': {
    'range': {'sheetId': ws.id,
              'startRowIndex': 1, 'endRowIndex': 1000,
              'startColumnIndex': 11, 'endColumnIndex': 12},
    'rule': {
        'condition': {'type': 'ONE_OF_LIST',
                      'values': [{'userEnteredValue': v} for v in
                                 ['Active', 'Low Stock', 'Discontinued', 'Pre-Order']]},
        'showCustomUi': True,
        'strict': True
    }
}}]}
wb.batch_update(body)
print('status validation set L2:L1000')