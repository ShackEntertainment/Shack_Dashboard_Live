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
i = ws.row_values(1).index('Location/Store') + 1
n = 0
for r, v in enumerate(ws.col_values(i)[1:], start=2):
    if v.startswith('Etsy:'):
        ws.update_cell(r, i, 'Etsy')
        n += 1
print(f'normalized {n} cells to Etsy')