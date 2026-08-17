"""
SHACK ENTERTAINMENT — shack_calendar.py
[CALENDAR] v2 — 2026-08-14
Google Calendar (service account) + pending-holds table.
v2: RFC3339 Z timestamps fix the 400 on event listing; labels local time.
Agents propose HOLDs; only Bola's /cal confirm or /cal add writes
to the calendar. House law: confirmed-only source of truth.
"""
import os
import sqlite3
from datetime import datetime, timedelta

from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

CREDENTIALS = os.path.join(project_root, 'configs', 'service_account.json')
CAL_ID = os.getenv('GOOGLE_CALENDAR_ID', '')
SCOPES = ['https://www.googleapis.com/auth/calendar']
TZ = 'Europe/London'
BASE = 'https://www.googleapis.com/calendar/v3/calendars/'

db_path = os.path.join(script_dir, 'executive_cache.db')
if not os.path.exists(db_path):
    db_path = os.path.join(project_root, 'executive_cache.db')

def _session():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS, scopes=SCOPES)
    return AuthorizedSession(creds)

# ------------------------------------------------------------ holds table
def _holds_init():
    con = sqlite3.connect(db_path)
    con.execute('''CREATE TABLE IF NOT EXISTS pending_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, start TEXT, minutes INTEGER,
        source TEXT, created TEXT)''')
    con.commit()
    con.close()

def add_hold(title, start, minutes, source='ev'):
    _holds_init()
    con = sqlite3.connect(db_path)
    cur = con.execute(
        '''INSERT INTO pending_events
           (title, start, minutes, source, created) VALUES(?,?,?,?,?)''',
        (title, start, int(minutes), source,
         datetime.now().strftime('%Y-%m-%d %H:%M')))
    hid = cur.lastrowid
    con.commit()
    con.close()
    return hid

def list_holds():
    _holds_init()
    con = sqlite3.connect(db_path)
    rows = con.execute(
        'SELECT id, title, start, minutes FROM pending_events ORDER BY id'
    ).fetchall()
    con.close()
    return rows

def get_hold(hold_id):
    _holds_init()
    con = sqlite3.connect(db_path)
    row = con.execute(
        'SELECT id, title, start, minutes FROM pending_events WHERE id=?',
        (hold_id,)).fetchone()
    con.close()
    return row

def delete_hold(hold_id):
    con = sqlite3.connect(db_path)
    con.execute('DELETE FROM pending_events WHERE id=?', (hold_id,))
    con.commit()
    con.close()

# ------------------------------------------------------------ google cal
def add_event(title, start_str, minutes, notes=''):
    """start_str: 'YYYY-MM-DD HH:MM'. Writes to GOOGLE_CALENDAR_ID."""
    start = datetime.strptime(start_str, '%Y-%m-%d %H:%M')
    end = start + timedelta(minutes=int(minutes))
    body = {
        'summary': title,
        'description': notes,
        'start': {'dateTime': start.strftime('%Y-%m-%dT%H:%M:00'),
                  'timeZone': TZ},
        'end': {'dateTime': end.strftime('%Y-%m-%dT%H:%M:00'),
                'timeZone': TZ},
    }
    with _session() as s:
        r = s.post(BASE + CAL_ID + '/events', json=body)
        r.raise_for_status()
        return r.json().get('htmlLink', '')

def list_events(days=1):
    now = datetime.utcnow()
    tmin = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tmax = now + timedelta(days=days)
    params = {
        'timeMin': tmin.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'timeMax': tmax.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'singleEvents': 'true',
        'orderBy': 'startTime',
    }
    with _session() as s:
        r = s.get(BASE + CAL_ID + '/events', params=params)
        r.raise_for_status()
        items = r.json().get('items', [])
    out = []
    for it in items:
        st = it.get('start', {}).get('dateTime', '')
        if st:
            dt = datetime.fromisoformat(st.replace('Z', '+00:00'))
            dt = dt.astimezone()
            lab = dt.strftime('%Y-%m-%d %H:%M')
        else:
            lab = it.get('start', {}).get('date', '')
        out.append((lab, it.get('summary', '(no title)')))
    return out

def confirm_hold(hold_id):
    row = get_hold(hold_id)
    if not row:
        return None
    _, title, start, minutes = row
    add_event(title, start, minutes,
              notes='Approved by Bola via /cal confirm')
    delete_hold(hold_id)
    return title, start