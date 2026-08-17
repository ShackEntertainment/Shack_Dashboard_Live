"""
SHACK ENTERTAINMENT — shack_alerts.py
[WATCHDOG] v1 — 2026-08-14
Twilio SMS alerts. No twilio pip package — raw REST via requests.
Usage: py shack_alerts.py "message text"
"""
import os
import sys
import requests
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

def sms(text: str) -> str:
    sid = os.getenv('TWILIO_ACCOUNT_SID', '')
    tok = os.getenv('TWILIO_AUTH_TOKEN', '')
    frm = os.getenv('TWILIO_FROM', '')
    to = os.getenv('TWILIO_TO', '')
    if not (sid and tok and frm and to):
        return 'MISSING TWILIO .env VALUES'
    url = f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json'
    try:
        r = requests.post(url, auth=(sid, tok),
                          data={'From': frm, 'To': to, 'Body': text},
                          timeout=20)
        if r.status_code in (200, 201):
            return 'SMS SENT'
        return f'SMS FAILED {r.status_code}: {r.text[:200]}'
    except Exception as e:
        return f'SMS ERROR: {e}'

if __name__ == '__main__':
    print(sms(' '.join(sys.argv[1:]) or 'Shack alert'))