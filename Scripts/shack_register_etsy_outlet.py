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
ws = next(w for w in wb.worksheets() if 'product sales outlet' in w.title.lower())
hdr = ws.row_values(1)
have = [v for v in ws.col_values(hdr.index('Outlet Name') + 1) if v]
if 'Etsy' in have:
    print('Etsy already registered')
else:
    row = {
        'Outlet ID': 'OUT-ETSY-001',
        'Outlet Name': 'Etsy',
        'Location': 'Online',
        'Contact': 'Paul Duncan (shop owner)',
        'Email': '',
        'Phone': '',
        'Products Stocked': 'Original Artwork, Giclee Prints, Greetings Cards, Commissions',
        'Commission %': 12.0,
        'Status': 'Active',
        'Total Sales YTD': 0,
    }
    ws.append_row([row.get(h, '') for h in hdr])
    print('Etsy registered in Product Sales Outlets')