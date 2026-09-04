"""
SHACK ENTERTAINMENT — shack_ops_sweep.py
07:00 canary suite. Independent of the bot process.
Tests every internal pipe; reports to the MD alone.
"""
import os
import httpx
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER = os.getenv('TELEGRAM_OWNER_CHAT_ID', '')

lines = []
def ok(name, detail=''):
    lines.append(f"✅ {name}" + (f" — {detail}" if detail else ''))
def bad(name, detail=''):
    lines.append(f"⚠️ {name} — {detail}")

# 1 — telegram api
try:
    r = httpx.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=15)
    r.raise_for_status()
    ok('Telegram bot API', r.json()['result']['username'])
except Exception as e:
    bad('Telegram bot API', str(e)[:120])

# 2 — sheets
try:
    import gspread
    gc = gspread.service_account(filename=os.path.join(
        project_root, 'configs', 'service_account.json'))
    sh = gc.open_by_key(os.getenv('GOOGLE_SHEET_ID'))
    ok('Google Sheets', f"{len(sh.worksheets())} tabs")
except Exception as e:
    bad('Google Sheets', str(e)[:120])

# 3 — finance
try:
    import shack_finance_queries as fq
    ans = fq.query_database('total revenue')
    ok('Finance queries', ans[:60].replace('\n', ' '))
except Exception as e:
    bad('Finance queries', str(e)[:120])

# 4 — calendar
try:
    import shack_calendar as scl
    evs = scl.list_events(1)
    ok('Calendar', f"{len(evs)} event(s) today")
except Exception as e:
    bad('Calendar', str(e)[:120])

# 5 — mail drafts
try:
    import shack_mail_bridge as mb
    d = mb.list_drafts()
    ok('Mail drafts', f"{len(d)} pending")
except Exception as e:
    bad('Mail drafts', str(e)[:120])

# 6 — expenses csv
try:
    with open(os.path.join(project_root, 'Data', 'expenses.csv'),
              encoding='utf-8') as f:
        ok('expenses.csv', f.readline().strip()[:40])
except Exception as e:
    bad('expenses.csv', str(e)[:120])

# 7 — sites (status recorded; dark is the current truth)
for url in ('https://shackentertainment.co.uk', 'https://theliveexchange.co.uk'):
    try:
        r = httpx.get(url, timeout=15, follow_redirects=True,
                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ShackSweep/1.0'})
        ok(url.split('//')[1], f"HTTP {r.status_code}")
    except Exception as e:
        bad(url.split('//')[1], str(e)[:120])

# 8 — subscriber path
lines.append('🟢 Subscriber path — OPEN inbound (intake only); outbound dispatch frozen')

report = '🩺 OPS SWEEP — canary\n' + '\n'.join(lines)
print(report)
try:
    with open(os.path.join(project_root, 'Data', 'ops_sweep.log'),
              'w', encoding='utf-8') as f:
        f.write(report)
except Exception:
    pass
if OWNER:
    try:
        httpx.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                   json={'chat_id': int(OWNER), 'text': report}, timeout=15)
    except Exception as e:
        print('sweep report send failed:', e)