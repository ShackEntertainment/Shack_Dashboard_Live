"""
SHACK ENTERTAINMENT — shack_intake.py
# [SUMMARY] DETAILS_FIRST_2026-08-13 — input details first, then placement.
# [PHONE] COLLECT_ALL_2026-08-13 — phone numbers captured for ALL departments.
# [FIX3] 2026-08-13 — provider email fix (thecoolatgmail -> thecool@gmail),
#   phone anchor widened, single band line in spoken audio.
Voice / text intake registration. Talent/partner keywords WIN;
subscriber is the fallback only. Transcription 100% local (faster-whisper).
"""
import re
import sqlite3
import os
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
db_path = os.path.join(script_dir, 'executive_cache.db')
if not os.path.exists(db_path):
    db_path = os.path.join(project_root, 'executive_cache.db')

_model = None

def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel('base', device='cpu', compute_type='int8')
    return _model

def transcribe(file_path: str) -> str:
    model = _get_model()
    segments, _ = model.transcribe(file_path, language='en')
    return ' '.join(seg.text for seg in segments).strip()

# ------------------------------------------------------------------ parsing
def normalize(text: str) -> str:
    # TheCoolAtGmail -> TheCool@Gmail (capital At glued on)
    t = re.sub(r'(?<=[A-Za-z0-9])[Aa]t(?=[A-Z])', '@', text)
    t = t.lower()
    # thecoolatgmail.com -> thecool@gmail.com (provider-aware)
    t = re.sub(r'([a-z0-9])at(gmail|hotmail|yahoo|outlook|icloud)', r'\1@\2', t)
    t = re.sub(r'\s+at\s+', '@', t)      # spaced "at" -> @
    t = re.sub(r'\s+dot\s+', '.', t)     # spaced "dot" -> .
    return t

def extract_email(text: str):
    m = re.search(r"[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}", normalize(text))
    return m.group(0) if m else None

def extract_phone(text: str):
    """Anchored first ('my number is...'), then any long digit run."""
    t = normalize(text)
    m = re.search(
        r'(?:phone number is|my number is|our number is|number is|phone is|mobile is|contact is)\s*'
        r'(\+?\d[\d\s]{6,}\d)', t)
    if not m:
        m = re.search(r'(\+?\d[\d\s]{9,}\d)', t)
    return m.group(1).strip() if m else None

def extract_name(text: str):
    m = re.search(
        r'my name is ([a-z0-9 .\'-]+?)(?:,|\.| my email| our email| my phone| my number| i am| we are| i would| we would|$)',
        normalize(text))
    return m.group(1).strip().title() if m else None

def extract_website(text: str):
    m = re.search(r'website\s+(?:[a-z\s]*?is\s+)?([a-z0-9.-]+\.[a-z]{2,}[a-z0-9./-]*)',
                  normalize(text))
    if m:
        return m.group(1)
    m = re.search(r'(?:band url|url) is (www\.[a-z0-9.-]+\.[a-z]{2,}[a-z0-9./-]*|[a-z0-9.-]+\.[a-z]{2,}[a-z0-9./-]*)',
                  normalize(text))
    return m.group(1) if m else None

def extract_band(text: str):
    m = re.search(r'band (?:called|named)\s+([a-z0-9 .\'-]+?)(?:\.|,| our| we|$)',
                  normalize(text))
    return m.group(1).strip().title() if m else None

def route(text: str) -> str:
    """Talent/partner keywords WIN; subscriber is the fallback only."""
    t = normalize(text)
    if any(k in t for k in ['artists unlimited', 'impressionist', 'surrealist',
                            'painter', 'visual artist', 'sculptor', 'art roster']):
        return 'artists_unlimited'
    if any(k in t for k in ['live exchange', 'band', 'musician', 'singer',
                            'style of music', 'rock', 'blues']):
        return 'live_exchange'
    if any(k in t for k in ['shack news', 'writer', 'journalist',
                            'reporter', 'broadcaster']):
        return 'shack_news_network'
    if any(k in t for k in ['b2b', 'business card', 'partnership',
                            'partner', 'leaflet', 'sponsor', 'company called']):
        return 'partnerships'
    return 'subscriber'

# ------------------------------------------------------------- registration
def register(text: str, source: str = 'voice') -> dict:
    kind = route(text)
    name = extract_name(text) or 'Unknown Intake'
    email = extract_email(text)
    phone = extract_phone(text)
    site = extract_website(text)
    band = extract_band(text)
    fields = {k: v for k, v in
              {'email': email, 'phone': phone, 'website': site,
               'band': band, 'source': source}.items() if v}

    if kind == 'subscriber':
        con = sqlite3.connect(db_path)
        con.execute('''CREATE TABLE IF NOT EXISTS shack_subscribers(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT,
            phone TEXT, source TEXT, created TEXT)''')
        con.execute('''INSERT INTO shack_subscribers
                       (name, email, phone, source, created)
                       VALUES (?,?,?,?,?)''',
                    (name, email, phone, source,
                     datetime.now().strftime('%Y-%m-%d %H:%M')))
        con.commit()
        con.close()
        return {'route': 'subscriber', 'name': name, 'email': email,
                'phone': phone, 'website': site, 'band': band}

    import shack_assets_handler as h
    k = 'partner' if kind == 'partnerships' else 'talent'
    r = h.onboard(k, kind, name, fields)
    return {'route': kind, 'name': name, 'email': email, 'phone': phone,
            'website': site, 'band': band, 'card': r['card']}

# ------------------------------------------------------------------ outputs
def summary(res: dict) -> str:
    """Text bubble: input details FIRST, then database placement."""
    lines = [f"Name: {res['name']}"]
    if res.get('email'):
        lines.append(f"Email: {res['email']}")
    if res.get('phone'):
        lines.append(f"Phone: {res['phone']}")
    if res.get('band'):
        lines.append(f"Band: {res['band']}")
    if res.get('website'):
        lines.append(f"Website: {res['website']}")
    lines.append(f"Registered to: {res['route']}")
    if res.get('card'):
        lines.append(f"Card: {res['card']}")
    else:
        lines.append("Added to the mailing list")
    lines.append("Follow-up draft queued for your approval. Nothing sent automatically.")
    return '\n'.join(lines)

def spoken(res: dict) -> str:
    """Audio version: one plain natural sentence stream. No symbols."""
    bits = [f"Intake registered. Name, {res['name']}."]
    if res.get('email'):
        bits.append(f"Email, {res['email']}.")
    if res.get('phone'):
        bits.append(f"Phone, {res['phone']}.")
    if res.get('band'):
        bits.append(f"Band, {res['band']}.")
    if res.get('website'):
        bits.append(f"Website, {res['website']}.")
    bits.append(f"Filed under, {res['route'].replace('_', ' ')}.")
    if res.get('card'):
        bits.append("Card saved to the database.")
    else:
        bits.append("Added to the mailing list.")
    bits.append("Follow-up draft queued for your approval.")
    return ' '.join(bits)