"""
SHACK ENTERTAINMENT — shack_mail_bridge.py
[MAILBRIDGE] v4 — 2026-08-15 (SIX INBOXES)
Polls all six Hostinger inboxes (IMAP), files new mail as PENDING
drafts. Tries Communications workspace for reply; falls back to approved
reply templates.
House law (Tier 3): NOTHING is sent externally except via the bot's
/senddraft command with Bola's explicit approval.
"""
import os
import re
import time
import imaplib
import smtplib
import sqlite3
from email.utils import parseaddr
from email.header import decode_header
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

drafts_dir = os.path.join(project_root, 'Mail_Drafts')
os.makedirs(drafts_dir, exist_ok=True)
db_path = os.path.join(script_dir, 'executive_cache.db')

ACCOUNTS = {
    'a-r':  {'user_env': 'MAIL_AR_USER',  'pass_env': 'MAIL_AR_PASS',
             'kind': 'talent'},
    'b2b':  {'user_env': 'MAIL_B2B_USER', 'pass_env': 'MAIL_B2B_PASS',
             'kind': 'partner'},
    'info': {'user_env': 'MAIL_INFO_USER', 'pass_env': 'MAIL_INFO_PASS',
             'kind': 'general'},
    'amit': {'user_env': 'MAIL_AMIT_USER', 'pass_env': 'MAIL_AMIT_PASS',
             'kind': 'general'},
    'bola': {'user_env': 'MAIL_BOLA_USER', 'pass_env': 'MAIL_BOLA_PASS',
             'kind': 'general'},
    'leo':  {'user_env': 'MAIL_LEO_USER',  'pass_env': 'MAIL_LEO_PASS',
             'kind': 'general'},
}

SKIP_FROM = ['noreply', 'no-reply', 'donotreply', 'do-not-reply',
             'linkedin', 'facebook', 'twitter', 'instagram', 'youtube',
             'newsletter', 'mailer-daemon', 'postmaster']

TEMPLATES = {
'talent': """Dear {name},

Thank you for writing to Shack Artists Unlimited — we read every message that comes in.

What working with Shack means for you:
- You keep your voice. We build around it — promotion, bookings support, and follow-through on everything we agree.
- Artist-first terms, always: 70/30 in your favour during the standard one-year Shack contract, and full ownership of your works, merchandise and all future income once it ends.
- One professional point of contact: me, at a-r@shackentertainment.co.uk.

We would love to set up a first call at your convenience — no commitments, just a conversation about where you want your work to go next.

Warm regards,
Leo — Chief of Staff, Shack Entertainment
a-r@shackentertainment.co.uk | www.shackentertainment.co.uk""",

'partner': """Dear {name},

Thank you for getting in touch with Shack Entertainment.

We are a London-based collective of talented creatives in all fields — independent, innovative startups in their own right, individually outstanding yet proudly on the fringe.

On the association itself: we can design an opportunity that generates exposure among our talent base and, by extension, the wider artist community, as part of our broad range of coverage — a well-structured collaboration in which your offering sits in the hands of working artists, in front of new audiences.

Would a 20-minute call this week or next be worth your while? This first conversation creates no obligations on either side.

Warm regards,
Leo — Chief of Staff, Shack Entertainment
b2b@shackentertainment.co.uk | www.shackentertainment.co.uk""",

'fan': """Hi {name},

Welcome to Shack Entertainment — a London-based family of talented creatives in all fields, individually outstanding yet proudly on the fringe.

Here's what you'll hear from us, and only this — no noise:
- New releases and store drops from our artists
- Live Exchange events and how to get tickets
- Stories from behind the work: how the art gets made
- Shack News Network highlights, when the view is worth your time

We're glad you're here. The fringe is better with company.

Warm regards,
Shack Entertainment
info@shackentertainment.co.uk | www.shackentertainment.co.uk""",

'general': """Dear {name},

Thank you for writing to Shack Entertainment — your message has landed with the right people.

I am logging it now and will come back to you personally within two working days. If your note is time-sensitive, reply with URGENT in the subject and it jumps the queue.

Warm regards,
Leo — Chief of Staff, Shack Entertainment
info@shackentertainment.co.uk | www.shackentertainment.co.uk""",
}

def _seen_init():
    con = sqlite3.connect(db_path)
    con.execute('''CREATE TABLE IF NOT EXISTS mail_seen(
        id TEXT PRIMARY KEY, account TEXT, created TEXT)''')
    con.commit()
    con.close()

def _is_seen(mid):
    con = sqlite3.connect(db_path)
    row = con.execute(
        'SELECT 1 FROM mail_seen WHERE id=?', (mid,)).fetchone()
    con.close()
    return bool(row)

def _mark_seen(mid, account):
    con = sqlite3.connect(db_path)
    con.execute(
        'INSERT OR IGNORE INTO mail_seen(id, account, created) VALUES(?,?,?)',
        (mid, account, datetime.now().strftime('%Y-%m-%d %H:%M')))
    con.commit()
    con.close()

def _decode_subject(raw):
    try:
        out = []
        for data, enc in decode_header(raw or ''):
            if isinstance(data, bytes):
                out.append(data.decode(enc or 'utf-8', errors='ignore'))
            else:
                out.append(str(data))
        return ' '.join(out).replace('\n', ' ').strip()
    except Exception:
        return raw or '(no subject)'

def _is_automated(faddr, fname):
    low = (faddr + ' ' + fname).lower()
    return any(k in low for k in SKIP_FROM)

def _body_of(msg):
    text = ''
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        text += payload.decode(errors='ignore')
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                text = payload.decode(errors='ignore')
    except Exception:
        pass
    return text.strip()

def _pick_template(kind, subject, body):
    if kind == 'general':
        head = (subject + ' ' + body[:300]).lower()
        if any(k in head for k in
               ['subscribe', 'mailing list', 'sign up', 'sign me up']):
            return 'fan'
        return 'general'
    return kind

def ping_accounts():
    """Login test for each account."""
    out = []
    host = os.getenv('HOSTINGER_IMAP', 'imap.hostinger.com')
    for key, cfg in ACCOUNTS.items():
        user = os.getenv(cfg['user_env'])
        pwd = os.getenv(cfg['pass_env'])
        if not user or not pwd:
            out.append(f"{key}: MISSING .env VALUES")
            continue
        try:
            M = imaplib.IMAP4_SSL(host, 993)
            M.login(user, pwd)
            M.logout()
            out.append(f"{key}: OK")
        except Exception as e:
            out.append(f"{key}: FAILED — {e}")
    return ' | '.join(out)

def email_message_from(raw):
    import email as _email
    return _email.message_from_bytes(raw)

def _comms_reply(fname, subject, body, kind):
    """[COMMSWIRE] 2026-08-15 — Communications workspace drafts the reply.
    Returns None on ANY failure; caller falls back to approved templates."""
    try:
        import requests
        akey = os.getenv('ANYTHINGLLM_API_KEY', '')
        aurl = os.getenv('ANYTHINGLLM_URL', 'http://localhost:3001')
        if not akey:
            return None
        r = requests.get(aurl + '/api/v1/workspaces',
                         headers={'Authorization': 'Bearer ' + akey},
                         timeout=15)
        slug = None
        for ws in r.json().get('workspaces', []):
            if 'communication' in ws['name'].lower():
                slug = ws['slug']
        if not slug:
            return None
        prompt = (
            "Draft a warm, professional reply email for Shack "
            f"Entertainment. Sender name: {fname}. Subject: {subject}. "
            f"Their message: {body[:1500]}\n\n"
            "Return ONLY the email body text. No subject line, no "
            "quotation marks around it, no sign-off or name at the end, "
            "and no notes about approval or internal process "
            "(the signature is added automatically).")
        r2 = requests.post(aurl + f'/api/v1/workspace/{slug}/chat',
                           headers={'Authorization': 'Bearer ' + akey,
                                    'Content-Type': 'application/json'},
                           json={'message': prompt, 'mode': 'chat'},
                           timeout=60)
        txt = (r2.json().get('textResponse') or '').strip()
        if len(txt) < 40:
            return None
        return txt[:2000]
    except Exception as e:
        print(f"comms draft fallback: {e}")
        return None

def check_mail():
    """Poll all accounts; write PENDING drafts; return digest list."""
    _seen_init()
    host = os.getenv('HOSTINGER_IMAP', 'imap.hostinger.com')
    since = (datetime.now() - timedelta(days=7)).strftime('%d-%b-%Y')
    results = []
    for key, cfg in ACCOUNTS.items():
        user = os.getenv(cfg['user_env'])
        pwd = os.getenv(cfg['pass_env'])
        if not user or not pwd:
            continue
        last_err = None
        for attempt in (1, 2):
            try:
                M = imaplib.IMAP4_SSL(host, 993)
                M.login(user, pwd)
                M.select('INBOX')
                typ, data = M.search(None, '(SINCE ' + since + ')')
                ids = data[0].split()
                seq = 0
                for uid in ids:
                    typ, mdata = M.fetch(uid, '(RFC822)')
                    msg = email_message_from(mdata[0][1])
                    mid = msg.get('Message-ID') or (key + '-' + uid.decode())
                    if _is_seen(mid):
                        continue
                    name_addr = parseaddr(msg.get('From', ''))
                    fname = name_addr[0] or 'there'
                    faddr = name_addr[1]
                    if _is_automated(faddr, fname):
                        _mark_seen(mid, key)
                        continue
                    subject = _decode_subject(msg.get('Subject'))
                    body = _body_of(msg)
                    tpl = _pick_template(cfg['kind'], subject, body)
                    ts = datetime.now().strftime('%y%m%d_%H%M%S')
                    draft_id = ts + '_' + key + '_' + str(seq)
                    seq += 1
                    path = os.path.join(drafts_dir,
                                        'PENDING_' + draft_id + '.md')
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write('TO_NAME: ' + fname + '\n')
                        f.write('TO_ADDR: ' + faddr + '\n')
                        f.write('FROM_ACCOUNT: ' + user + '\n')
                        f.write('SUBJECT: Re: ' + subject + '\n')
                        comms = _comms_reply(fname, subject, body, cfg['kind'])
                        f.write('TEMPLATE: ' + tpl + ('+comms' if comms else '') + '\n')
                        f.write('---BODY---\n')
                        if comms:
                            f.write(comms + '\n')
                        else:
                            f.write(TEMPLATES[tpl].format(name=fname))
                    _mark_seen(mid, key)
                    results.append({'account': key,
                                    'from': fname + ' <' + faddr + '>',
                                    'subject': subject,
                                    'draft_id': draft_id,
                                    'template': tpl})
                M.logout()
                last_err = None
                break
            except Exception as e:
                last_err = e
                time.sleep(3)
        if last_err:
            results.append({'account': key, 'error': str(last_err)})
        time.sleep(2)
    return results

def list_drafts():
    try:
        return sorted(f for f in os.listdir(drafts_dir)
                      if f.startswith('PENDING_'))
    except Exception:
        return []

def send_draft(draft_id):
    """Tier-3 gate: called ONLY by the bot's /senddraft command."""
    match = [f for f in list_drafts() if draft_id in f]
    if not match:
        return "No pending draft matching '" + draft_id + "'"
    path = os.path.join(drafts_dir, match[0])
    with open(path, encoding='utf-8') as f:
        raw = f.read()
    head, body = raw.split('---BODY---', 1)
    meta = {}
    for line in head.strip().splitlines():
        k, v = line.split(': ', 1)
        meta[k] = v
    user = meta['FROM_ACCOUNT']
    key = user.split('@')[0]
    cfg = ACCOUNTS.get(key)
    pwd = os.getenv(cfg['pass_env']) if cfg else None
    if not pwd:
        return 'No password in .env for ' + user
    host = os.getenv('HOSTINGER_SMTP', 'smtp.hostinger.com')
    try:
        msg = MIMEText(body.strip(), 'plain', 'utf-8')
        msg['Subject'] = meta['SUBJECT']
        msg['From'] = user
        msg['To'] = meta['TO_ADDR']
        with smtplib.SMTP_SSL(host, 465) as S:
            S.login(user, pwd)
            S.sendmail(user, [meta['TO_ADDR']], msg.as_string())
        os.rename(path, path.replace('PENDING_', 'SENT_'))
        return 'SENT ✅ ' + meta['TO_ADDR']
    except Exception as e:
        return 'SEND FAILED — ' + e