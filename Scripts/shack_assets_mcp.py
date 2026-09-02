"""
SHACK ENTERTAINMENT — shack_assets_mcp.py
Approval-gated asset pipeline: DA requests, Bola approves via Telegram,
the tool moves. No token, no move.
"""
import os, json, string, random
from datetime import date
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER = os.getenv('TELEGRAM_OWNER_CHAT_ID', '')
DRAFTS = os.path.join(project_root, '03_Drafts')
APPROVED = os.path.join(project_root, '04_Approved')
APDIR = os.path.join(project_root, 'Data', 'approvals')
LOG = os.path.join(project_root, 'Data', 'asset_log.csv')
os.makedirs(APDIR, exist_ok=True)
HEADER = 'date,code,from,to,note'

mcp = FastMCP('ShackAssets')

def _log(code, src, dst, note):
    rows = [HEADER]
    if os.path.exists(LOG):
        with open(LOG, encoding='utf-8') as f:
            rows = [l.rstrip() for l in f if l.strip()] or [HEADER]
    rows.append(','.join([date.today().isoformat(), code, src, dst,
                          note.replace(',', ' ')]))
    with open(LOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')

@mcp.tool()
def request_approval(filenames: str, note: str = '') -> str:
    """Ask Bola to approve moving draft asset(s) from 03_Drafts. Comma-separated names."""
    names = [n.strip() for n in filenames.split(',') if n.strip()]
    missing = [n for n in names if not os.path.exists(os.path.join(DRAFTS, n))]
    if missing:
        return 'NOT FOUND in 03_Drafts: ' + ', '.join(missing)
    code = ''.join(random.choices(string.ascii_uppercase, k=4))
    with open(os.path.join(APDIR, f"pending_{code}.json"), 'w') as f:
        json.dump({'files': names, 'note': note}, f)
    msg = (f"🎨 APPROVAL REQUEST {code}\n" + '\n'.join(names) +
           (f"\n{note}" if note else '') +
           f"\nReply /approve {code} to release the move.")
    try:
        if TOKEN and OWNER:
            httpx.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                       json={'chat_id': int(OWNER), 'text': msg}, timeout=15)
    except Exception:
        pass
    return f"Request {code} sent to Bola. Await /approve {code}. Move nothing yourself."

@mcp.tool()
def approve_asset(code: str) -> str:
    """Move approved draft(s) to 04_Approved with versioned names. Requires Bola's token."""
    code = code.strip().upper()
    tok = os.path.join(APDIR, f"approved_{code}.token")
    pend = os.path.join(APDIR, f"pending_{code}.json")
    if not os.path.exists(tok):
        return f"PENDING — no approval token for {code}. The move is Bola's act."
    if not os.path.exists(pend):
        return f"Token yes, request no — no pending record for {code}."
    with open(pend) as f:
        rec = json.load(f)
    moved = []
    for n in rec['files']:
        src = os.path.join(DRAFTS, n)
        base, ext = os.path.splitext(n)
        base = base.replace('_draft', '')
        v = 1
        while os.path.exists(os.path.join(APPROVED, f"{base}_v{v}{ext}")):
            v += 1
        dst = os.path.join(APPROVED, f"{base}_v{v}{ext}")
        os.replace(src, dst)
        moved.append(os.path.basename(dst))
        _log(code, n, os.path.basename(dst), rec.get('note', ''))
    os.remove(tok); os.remove(pend)
    return 'MOVED by approval ' + code + ': ' + ', '.join(moved)

if __name__ == '__main__':
    mcp.run()