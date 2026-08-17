"""
SHACK ENTERTAINMENT — shack_brief.py
[BRIEF] v2 — 2026-08-16
Daily 08:00 Chief-of-Staff briefing to Telegram: calendar, pending
mail drafts, event holds, books snapshot, latest sales rows.
Manual run or Task Scheduler.
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

import shack_calendar as scl
import shack_mail_bridge as mb
import shack_finance_queries as fq

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
CHAT = os.getenv('TELEGRAM_CHAT_ID', '')

def _sales_lines():
    try:
        creds = Credentials.from_service_account_file(
            os.path.join(project_root, 'configs', 'service_account.json'),
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        sh = gspread.authorize(creds).open_by_key(
            os.getenv('GOOGLE_SHEET_ID'))
        for ws in sh.worksheets():
            if 'form' in ws.title.lower():
                vals = ws.get_all_values()
                if len(vals) < 2:
                    return ['Sales: none yet.']
                headers = vals[0]
                out = ['Sales — latest entries:']
                for r in vals[-3:]:
                    pairs = [f"{headers[i]}: {r[i]}"
                             for i in range(len(r))
                             if i < len(headers) and str(r[i]).strip()]
                    out.append('  • ' + ' | '.join(pairs[:4]))
                return out
        return ['Sales: no form tab found.']
    except Exception as e:
        return [f'Sales: unavailable ({e})']

def build():
    lines = ['☕ Shack morning brief — '
             + datetime.now().strftime('%a %d %b')]
    try:
        evs = scl.list_events(1)
        lines.append('')
        if evs:
            lines.append('Today:')
            for s, t in evs:
                lines.append(f'  {s[11:16]}  {t}')
        else:
            lines.append('Today: clear.')
        wk = scl.list_events(7)
        if len(wk) > len(evs):
            lines.append(f'Also this week: {len(wk) - len(evs)} more — /cal week')
    except Exception as e:
        lines.append(f'Calendar: unavailable ({e})')
    try:
        pend = mb.list_drafts()
        lines.append('')
        if pend:
            lines.append(f'Mail: {len(pend)} pending draft(s) — /drafts')
        else:
            lines.append('Mail: inbox zero.')
    except Exception as e:
        lines.append(f'Mail: unavailable ({e})')
    try:
        holds = scl.list_holds()
        if holds:
            lines.append(f'Events: {len(holds)} hold(s) awaiting approval — /cal pending')
        else:
            lines.append('Events: no holds waiting.')
    except Exception as e:
        lines.append(f'Events: unavailable ({e})')
    try:
        rev = fq.query_database("What's our total revenue?")
        exp = fq.query_database("What expenses do we have?")
        lines.append('')
        lines.append('Books: ' + ' | '.join(
            x.replace('\n', ' ') for x in (rev, exp))[:600])
    except Exception as e:
        lines.append(f'Books: unavailable ({e})')
    lines.append('')
    lines.extend(_sales_lines())
    return '\n'.join(lines)

def send():
    text = build()
    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                      data={'chat_id': CHAT, 'text': text}, timeout=20)
    return r.status_code, text

if __name__ == '__main__':
    code, text = send()
    print('BRIEF SENT' if code == 200 else f'BRIEF FAILED {code}')
    print(text)