"""
SHACK ENTERTAINMENT — shack_sales_mcp.py
Gated sales ledger: Etsy orders CSV -> Outlet Sales tab (AU Master).
Doctrine line 8: fees off the top, then 70/30. Preview first; /approve to write.
"""
import os, csv, re
import gspread
from google.oauth2.service_account import Credentials
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
SA_FILE = os.path.join(project_root, 'configs', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
AU_WB = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'
DROPS = os.path.join(project_root, 'Data', 'dig_drops')
APDIR = os.path.join(project_root, 'Data', 'approvals')
ARTIST = 'Paul Duncan'
OUTLET = 'Etsy'
COMMISSION = 12.0

mcp = FastMCP('ShackSales')

def _connect(tabpart):
    creds = Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    wb = gc.open_by_key(AU_WB)
    return next(w for w in wb.worksheets() if tabpart in w.title.lower())

def _read(path):
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def _col(hdrs, *pats):
    for p in pats:
        for h in hdrs:
            if re.search(p, h or '', re.I):
                return h
    return None

def _map(rows):
    out = []
    if not rows:
        return out
    hdrs = list(rows[0].keys())
    c_id = _col(hdrs, r'receipt', r'order.?id', r'transaction', r'sale.?id')
    c_date = _col(hdrs, r'date')
    c_item = _col(hdrs, r'item', r'title', r'product')
    c_sku = _col(hdrs, r'sku')
    c_qty = _col(hdrs, r'quant')
    c_price = _col(hdrs, r'price', r'total', r'amount')
    c_fees = _col(hdrs, r'fee')
    for r in rows:
        g = lambda c: (r.get(c) or '').strip() if c else ''
        qty = int(float(g(c_qty) or 1)) if g(c_qty) else 1
        gross = round(float(g(c_price) or 0) * qty, 2) if g(c_price) else 0.0
        fees = round(float(g(c_fees)), 2) if c_fees and g(c_fees) else round(gross * COMMISSION / 100, 2)
        net = round(gross - fees, 2)
        low = g(c_item).lower()
        ptype = ('Giclee Print' if 'print' in low else
                 'Greetings Card' if 'card' in low else
                 'Commission' if 'commission' in low else 'Original Artwork')
        out.append({
            'Sale ID': g(c_id) or g(c_item)[:20],
            'Outlet Name': OUTLET,
            'Product Type': ptype,
            'Sale Date': g(c_date),
            'Sale Price (£)': gross,
            'Artist Name': ARTIST,
            'Shack Share% £': round(net * 0.30, 2),
            'Artist Share % £': round(net * 0.70, 2),
            'Outlet Commission %': COMMISSION,
            'SKU': g(c_sku),
            'Quantity': qty,
            'Product Name': g(c_item),
        })
    return out

@mcp.tool()
def preview_sales(filename: str) -> str:
    """Map an orders CSV to Outlet Sales shape; writes preview only."""
    p = os.path.join(DROPS, filename)
    if not os.path.exists(p):
        return f'No {filename} in dig_drops.'
    rows = _map(_read(p))
    if not rows:
        return 'CSV read but no rows mapped — check headers.'
    prev = os.path.join(DROPS, 'sales_preview_etsy.csv')
    with open(prev, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    tg = sum(r['Sale Price (£)'] for r in rows)
    ts = sum(r['Shack Share% £'] for r in rows)
    return (f"Preview {len(rows)} orders | gross £{tg:.2f} | "
            f"Shack share £{ts:.2f} -> sales_preview_etsy.csv")

@mcp.tool()
def upload_sales(code: str = 'SALES-PND') -> str:
    """Write previewed sales rows to Outlet Sales. Requires /approve token."""
    code = code.strip().upper()
    tok = os.path.join(APDIR, f'approved_{code}.token')
    if not os.path.exists(tok):
        return f'PENDING — no token for {code}. Reply /approve {code} to release.'
    prev = os.path.join(DROPS, 'sales_preview_etsy.csv')
    if not os.path.exists(prev):
        return 'No preview; run preview_sales first.'
    ws = _connect('outlet sales')
    hdr = ws.row_values(1)
    have = set(v for v in ws.col_values(1) if v)
    rows = [r for r in _read(prev) if r['Sale ID'] not in have]
    for r in rows:
        ws.append_row([r.get(h, '') for h in hdr])
    os.remove(tok)
    return f"WRITTEN {len(rows)} sales rows to Outlet Sales by approval {code}."

if __name__ == '__main__':
    mcp.run()