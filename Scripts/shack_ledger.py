"""
SHACK ENTERTAINMENT — shack_ledger.py
[LEDGER] v1 — 2026-08-15
Quick expense capture into executive_cache.db (finance_expenses).
The write-side of the read-only SQL connector: feeds /fin and the
morning brief. Revenue already flows live from sheet + bookings.
"""
import os
import sqlite3
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
db_path = os.path.join(script_dir, 'executive_cache.db')
if not os.path.exists(db_path):
    db_path = os.path.join(project_root, 'executive_cache.db')

def add_expense(description, amount, category='general',
                division='Shack Entertainment'):
    con = sqlite3.connect(db_path)
    con.execute(
        '''INSERT INTO finance_expenses
           (category, description, amount, date, division, status)
           VALUES(?,?,?,?,?,?)''',
        (category, description, float(amount),
         datetime.now().strftime('%Y-%m-%d'), division, 'recorded'))
    con.commit()
    con.close()
    return f"Logged 💸 £{float(amount):,.2f} — {description} [{category}]"