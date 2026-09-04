"""
SHACK ENTERTAINMENT — shack_sheets_mcp.py
Gated uploader: dig_drops preview CSV -> AU Master (Inventory Data) tab.
Preview first; write only on Bola's /approve token. Idempotent by SKU.
"""
import os, csv
import gspread
from google.oauth2.service_account import Credentials
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
SA_FILE = os.path.join(project_root, 'configs', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
AU_WB = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'
PREVIEW = os.path.join(project_root, 'Data', 'dig_drops', 'au_stock_pnd_preview.csv')
PROCESSED = os.path.join(project_root, 'Data', 'dig_drops', 'processed')
APDIR = os.path.join(project_root, 'Data', 'approvals')

mcp = FastMCP('ShackSheets')

def _connect():
    creds = Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    wb = gc.open_by_key(AU_WB)
    for ws in wb.worksheets():
        if 'inventory' in ws.title.lower():
            return ws
    raise Exception('no tab matching inventory')

def _rows():
    with open(PREVIEW, encoding='utf-8') as f:
        return list(csv.DictReader(f))

@mcp.tool()
def preview_au_stock() -> str:
    """Report what would be written; writes nothing."""
    if not os.path.exists(PREVIEW):
        return 'No preview CSV in dig_drops.'
    ws = _connect()
    have = set(v for v in ws.col_values(1) if v)
    rows = [r for r in _rows() if r['SKU'] not in have]
    return (f"Tab '{ws.title}' | preview rows {len(_rows())} | "
            f"new SKUs {len(rows)} | dupes skipped {len(_rows()) - len(rows)}")

@mcp.tool()
def upload_au_stock(code: str = 'AUSTOCK') -> str:
    """Write preview rows to the Inventory tab. Requires /approve token."""
    code = code.strip().upper()
    tok = os.path.join(APDIR, f"approved_{code}.token")
    if not os.path.exists(tok):
        return f"PENDING — no approval token for {code}. Reply /approve {code} to release."
    ws = _connect()
    rows = _rows()
    hdr = ws.row_values(1)
    if not any(hdr):
        hdr = list(rows[0].keys())
        ws.append_row(hdr)
    if 'Artist Website' not in hdr:
        hdr = hdr + ['Artist Website']
        ws.update_cell(1, len(hdr), 'Artist Website')
    have = set(v for v in ws.col_values(1) if v)
    written = 0
    for r in rows:
        if r['SKU'] in have:
            continue
        ws.append_row([r.get(h, '') for h in hdr])
        written += 1
    os.remove(tok)
    os.makedirs(PROCESSED, exist_ok=True)
    os.replace(PREVIEW, os.path.join(PROCESSED, 'au_stock_pnd_preview.csv'))
    return f"WRITTEN {written} rows to '{ws.title}' by approval {code}; preview moved to processed."

if __name__ == '__main__':
    mcp.run()
