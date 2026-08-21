"""
SHACK ENTERTAINMENT — shack_news_daily.py
[NEWSDAILY] 2026-08-20 — one article per topic per day; md + PDF
(bit-for-bit identical) into Desktop\Shack Daily News for Bola's read.
6 AM daily auto-edition + /dailynews on demand.
Nothing publishes externally. RSS-grounded: no invented facts.
"""
import os
import re
import asyncio
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler
import httpx
from dotenv import load_dotenv

try:
    from fpdf import FPDF
    HAVE_PDF = True
except Exception:
    HAVE_PDF = False

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

ANYTHINGLLM_URL = os.getenv('ANYTHINGLLM_URL', 'http://localhost:3001')
ANYTHINGLLM_KEY = os.getenv('ANYTHINGLLM_API_KEY', '')
BRIEF = os.path.join(project_root, 'configs', 'news_brief.txt')
OUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'Shack Daily News')
os.makedirs(OUT_DIR, exist_ok=True)
LAST_CHAT = os.path.join(project_root, 'configs', 'last_chat.txt')

TOPICS = [
    ('UK Headline News', 'http://feeds.bbci.co.uk/news/uk/rss.xml'),
    ('Headline Geopolitical News', 'http://feeds.bbci.co.uk/news/world/rss.xml'),
    ('Latest AI & Tech News', 'http://feeds.bbci.co.uk/news/technology/rss.xml'),
    ('Creative Arts on the Fringe', None),
    ('Chinese Tech News and Innovation', 'https://www.scmp.com/rss/5/feed'),
    ('Health & Wellness', None),
]

ARTS_GROUND = ("SOURCE MATERIAL: the Shack estate itself — Shack "
    "Entertainment, Artists Unlimited, The Live Exchange, PND FineArt, "
    "Shack News Network. Write a fringe/underground creative arts "
    "feature using ONLY estate facts plus clearly-labelled commentary. "
    "No invented events, people or quotes.")
HEALTH_GROUND = ("Write evergreen performer fitness / wellness / "
    "injury-prevention guidance. No invented studies, statistics or "
    "expert quotes; label all recommendations as editorial guidance.")

_workspace_cache = {}

async def _allm_get(path):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(ANYTHINGLLM_URL + path,
                        headers={'Authorization': f'Bearer {ANYTHINGLLM_KEY}'})
        r.raise_for_status()
        return r.json()

async def _allm_chat(slug, message):
    async with httpx.AsyncClient(timeout=420) as c:
        r = await c.post(
            f'{ANYTHINGLLM_URL}/api/v1/workspace/{slug}/chat',
            headers={'Authorization': f'Bearer {ANYTHINGLLM_KEY}',
                     'Content-Type': 'application/json',
                     'Accept': 'application/json'},
            json={'message': message, 'mode': 'chat'})
        r.raise_for_status()
        return r.json()

async def _find_slug(match):
    global _workspace_cache
    if not _workspace_cache:
        data = await _allm_get('/api/v1/workspaces')
        for ws in data.get('workspaces', []):
            _workspace_cache[ws['name'].lower()] = ws['slug']
    for name, slug in _workspace_cache.items():
        if match in name:
            return slug
    return None

def _last_chat():
    try:
        with open(LAST_CHAT) as f:
            return f.read().strip()
    except Exception:
        return ''

def _feed(url, n=5):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ShackNews/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            root = ET.fromstring(r.read())
        items = []
        for it in root.iter('item'):
            t = (it.findtext('title') or '').strip()
            d = re.sub(r'<[^>]+>', '', it.findtext('description') or '').strip()
            if t:
                items.append('- ' + t + ': ' + d[:300])
            if len(items) >= n:
                break
        return '\n'.join(items) or '(feed empty)'
    except Exception as e:
        return '(feed unavailable: ' + str(e) + ')'

def _shape(text, topic, date_str):
    raw = [l.rstrip() for l in text.strip().splitlines()]
    lines = []
    blank = 0
    for l in raw:
        if not l.strip():
            blank += 1
            if blank <= 1:
                lines.append('')
        else:
            blank = 0
            lines.append(l)
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        lines = [topic]
    if not lines[0].startswith('#'):
        lines = ['# ' + lines[0]] + lines[1:]
    byline = 'By Shack News Editor | ' + date_str + ' | Category: ' + topic
    if len(lines) < 2 or not lines[1].lower().startswith('by shack'):
        lines = [lines[0], byline, ''] + lines[1:]
    return '\n'.join(lines)

def _ascii(t):
    for a, b in (('—', '-'), ('–', '-'), ('‘', "'"), ('’', "'"),
                 ('“', '"'), ('”', '"'), ('…', '...'), ('•', '-'),
                 ('£', 'GBP '), ('€', 'EUR '), ('·', '-')):
        t = t.replace(a, b)
    return t.encode('latin-1', 'replace').decode('latin-1')

def _make_pdf(md_text, out_path):
    if not HAVE_PDF:
        return False
    fam = 'Helvetica'
    try:
        pdf = FPDF()
        pdf.add_font('Arial', '', r'C:\Windows\Fonts\arial.ttf')
        pdf.add_font('Arial', 'B', r'C:\Windows\Fonts\arialbd.ttf')
        pdf.add_font('Arial', 'I', r'C:\Windows\Fonts\ariali.ttf')
        fam = 'Arial'
        body = md_text
    except Exception:
        pdf = FPDF()
        body = _ascii(md_text)
    lines = body.splitlines()
    pdf.add_page()
    pdf.set_font(fam, 'B', 16)
    pdf.multi_cell(0, 8, lines[0].lstrip('#').strip() if lines else '')
    pdf.ln(2)
    if len(lines) > 1:
        pdf.set_font(fam, 'I', 10)
        pdf.multi_cell(0, 5, lines[1])
        pdf.ln(4)
    pdf.set_font(fam, '', 11)
    para = []
    for l in lines[2:]:
        if l.strip():
            para.append(l.strip())
        else:
            if para:
                pdf.multi_cell(0, 6, ' '.join(para))
                pdf.ln(3)
                para = []
    if para:
        pdf.multi_cell(0, 6, ' '.join(para))
    pdf.output(out_path)
    return True

async def _produce(only='', send=None):
    picks = [t for t in TOPICS if only and only in t[0].lower()]
    if not picks and not only:
        picks = list(TOPICS)
    brief = ''
    if os.path.exists(BRIEF):
        brief = open(BRIEF, encoding='utf-8').read()
    slug = await _find_slug('news')
    if not slug:
        return ['❌ No news workspace found.']
    date_str = datetime.now().strftime('%d %B %Y')
    filedate = datetime.now().strftime('%Y-%m-%d')
    done = []
    for topic, url in picks:
        try:
            material = _feed(url) if url else (
                ARTS_GROUND if 'Arts' in topic else HEALTH_GROUND)
            prompt = (brief + '\n\nTOPIC: ' + topic +
                      '\nSOURCE MATERIAL (real, fetched now):\n' + material +
                      '\n\nWrite ONE 400-500 word article using ONLY the '
                      'source material above plus estate knowledge from the '
                      'brief. Start with "# <headline>", then the byline '
                      'line, then body paragraphs separated by blank lines. '
                      'No invented facts, quotes or statistics. UK spelling.')
            data = await asyncio.wait_for(_allm_chat(slug, prompt), timeout=400)
            text = data.get('textResponse') or ''
            if not text.strip():
                done.append('⏳ ' + topic + ': empty reply — skipped')
                continue
            safe = text.encode('cp1252', 'replace').decode('cp1252')
            md = _shape(safe, topic, date_str)
            slugname = re.sub(r'[^A-Za-z0-9]+', '-', topic).strip('-')
            base = filedate + '_' + slugname
            with open(os.path.join(OUT_DIR, base + '.md'), 'w',
                      encoding='cp1252') as f:
                f.write(md)
            pdf_ok = _make_pdf(md, os.path.join(OUT_DIR, base + '.pdf'))
            headline = md.splitlines()[0].lstrip('#').strip()
            line = (('✅ ' if pdf_ok else '📄 ') + topic + ' saved' +
                    (' + PDF' if pdf_ok else ' (PDF skipped)') +
                    ': ' + headline)
            done.append(line)
            if send:
                await send(line)
        except asyncio.TimeoutError:
            done.append('⏳ ' + topic + ': stalled — skipped')
        except Exception as e:
            done.append('❌ ' + topic + ': ' + type(e).__name__)
    return done

async def dailynews(update, context):
    parts = (update.message.text or '').split()
    only = parts[1].lower() if len(parts) > 1 else ''
    if only and not [t for t in TOPICS if only in t[0].lower()]:
        await update.message.reply_text("No topic matches. Topics: " +
                                        ' | '.join(t[0] for t in TOPICS))
        return
    n = len([t for t in TOPICS if only and only in t[0].lower()]) or len(TOPICS)
    await update.message.reply_text(
        f"📰 Newsroom is writing {n} article(s)...")
    done = await _produce(only, send=update.message.reply_text)
    await update.message.reply_text(
        'Daily desk complete. Folder: Desktop\\Shack Daily News\n' +
        '\n'.join(done) +
        '\nNothing published externally — awaiting your read.')

async def news_loop(app):
    while True:
        now = datetime.now()
        target = now.replace(hour=6, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        await asyncio.sleep((target - now).total_seconds())
        chat = _last_chat()
        if not chat:
            continue
        try:
            await app.bot.send_message(
                int(chat), "📰 6 AM edition — newsroom writing the six...")
            done = await _produce(
                send=lambda t: app.bot.send_message(int(chat), t))
            await app.bot.send_message(
                int(chat),
                'Daily desk complete. Folder: Desktop\\Shack Daily News\n' +
                '\n'.join(done) +
                '\nNothing published externally — awaiting your read.')
        except Exception as e:
            print(f"news_loop error: {e}")

def start_news_loop(app):
    asyncio.create_task(news_loop(app))

def add_handlers(app):
    app.add_handler(CommandHandler('dailynews', dailynews))