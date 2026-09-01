"""
SHACK ENTERTAINMENT — shack_subscribers.py
Subscriber registry — local source of truth while Mailchimp sleeps.
"""
import os, re
from datetime import date

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
PATH = os.path.join(project_root, 'Data', 'subscribers.csv')
HEADER = 'id,email,date,source,status'
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')

def _rows():
    if not os.path.exists(PATH):
        return []
    with open(PATH, encoding='utf-8') as f:
        return [l.rstrip() for l in f if l.strip()]

def add(email, source='telegram'):
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        return None, 'That address does not look right — check it and try again.'
    rows = _rows()
    if not rows:
        rows = [HEADER]
    for r in rows[1:]:
        p = r.split(',')
        if len(p) > 4 and p[1] == email and p[4] == 'active':
            return None, 'That address is already on the list — welcome aboard regardless.'
    sid = f"SUB-{len(rows):04d}"
    rows.append(f"{sid},{email},{date.today().isoformat()},{source},active")
    with open(PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    return sid, (f"Welcome aboard — {email} is on the Shack list. "
                 f"First dispatch flies when the newsroom ships.")

def count():
    rows = _rows()
    return len([r for r in rows[1:] if r.split(',')[-1] == 'active'])