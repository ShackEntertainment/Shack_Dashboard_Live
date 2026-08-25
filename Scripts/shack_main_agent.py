import os
import re
import logging
import traceback
import asyncio
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import gspread
import httpx
import shack_finance_queries as fq
import shack_intake as si
import shack_mail_bridge as mb
import shack_calendar as scl
import shack_ledger as slg
import shack_social as soc
import shack_render as sr
import shack_news_daily as snd
import shack_equipment_ingest as eqi

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
CREDENTIALS = os.path.join(project_root, 'configs', 'service_account.json')
REGISTRY = os.path.join(project_root, 'configs', 'shack_registry.txt')
DESIGN_BRIEF = os.path.join(project_root, 'configs', 'design_brief.txt')
SITE_OPS_BRIEF = os.path.join(project_root, 'configs', 'site_ops_brief.txt')
CS_BRIEF = os.path.join(project_root, 'configs', 'content_studio_brief.txt')
NEWS_BRIEF = os.path.join(project_root, 'configs', 'news_brief.txt')
RA_BRIEF = os.path.join(project_root, 'configs', 'research_brief.txt')
FD_BRIEF = os.path.join(project_root, 'configs', 'film_director_brief.txt')
CD_BRIEF = os.path.join(project_root, 'configs', 'creative_director_brief.txt')
BV_BRIEF = os.path.join(project_root, 'configs', 'brand_vision_brief.txt')
AR_BRIEF = os.path.join(project_root, 'configs', 'artist_relations_brief.txt')
COS_BRIEF = os.path.join(project_root, 'configs', 'chief_of_staff_brief.txt')
COMMS_BRIEF = os.path.join(project_root, 'configs', 'comms_brief.txt')
ANYTHINGLLM_URL = os.getenv('ANYTHINGLLM_URL', 'http://localhost:3001')
ANYTHINGLLM_KEY = os.getenv('ANYTHINGLLM_API_KEY', '')

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def connect():
    gc = gspread.service_account(filename=CREDENTIALS)
    return gc.open_by_key(SHEET_ID)

def _msg_text(update: Update) -> str:
    return update.message.text or update.message.caption or ''

# ============================================================================
# [VOICE] RYAN_PRIMARY — natural British (edge-tts).
# [SPEECH] NATURAL_CLEAN — no symbol ever reaches the voice.
# [CALWIRE] /ev Events Agent + HOLD capture + /cal approvals.
# [FINWIRE] /fin: live SQL data injected into Shack Finance agent.
# [LOGWIRE] /log expense capture into finance_expenses.
# [CABINET] 2026-08-16 — remaining workspaces on call.
# [REGWIRE] 2026-08-16 — Brand & Channel Registry injected into /mk.
# ============================================================================

_audio_on = {'on': True}
TTS_VOICE = 'en-GB-RyanNeural'
TTS_FALLBACK_SAPI = 'David'

def _clean_for_speech(text: str) -> str:
    t = text.replace('→', ' goes to ')
    t = re.sub(r'[\u2000-\u2BFF\uFE00-\uFE0F\U0001F000-\U0001FAFF]', ' ', t)
    t = re.sub(r'[*_`#>|\\\[\]{}"/]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t[:1500]

def _tts_to_file(text: str, path: str):
    try:
        import edge_tts
        asyncio.run(edge_tts.Communicate(text, TTS_VOICE).save(path))
        return 'ryan'
    except Exception as e:
        print(f"edge-tts failed ({e}); falling back to SAPI Dave")
        import pyttsx3
        eng = pyttsx3.init()
        for v in eng.getProperty('voices'):
            if TTS_FALLBACK_SAPI.lower() in v.name.lower():
                eng.setProperty('voice', v.id)
                break
        eng.save_to_file(text, path)
        eng.runAndWait()
        return 'dave'

async def send_voice(update: Update, text: str):
    if not _audio_on['on'] or not text:
        return
    try:
        path = os.path.join(tempfile.gettempdir(),
                            f"shack_tts_{update.message.message_id}.mp3")
        engine = await asyncio.to_thread(_tts_to_file, _clean_for_speech(text), path)
        with open(path, 'rb') as f:
            await update.message.reply_audio(f, title=f"Shack reply [{engine}]")
    except Exception as e:
        print(f"TTS error: {e}")

_workspace_cache = {}

async def _allm_get(path):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(ANYTHINGLLM_URL + path,
                        headers={'Authorization': f'Bearer {ANYTHINGLLM_KEY}'})
        r.raise_for_status()
        return r.json()

async def _allm_chat(slug, message):
    async with httpx.AsyncClient(timeout=900) as c:
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

DATA_DIR = os.path.join(project_root, 'Data')
ROSTER_FILES = ['artists.csv', 'partners.csv', 'staff.csv',
                'outlets.csv', 'artist_stock.csv']
ROSTER_MATCHES = ('artist relations', 'marketing', 'content studio',
                  'news editor', 'research analyst')
EQUIP_MATCHES = ('film director', 'content studio')
CHANNELS_FILE = os.path.join(project_root, 'configs', 'media_channels.md')
CHANNEL_MATCHES = ('marketing', 'content studio', 'communication')

def _read_rows(path):
    try:
        with open(path, encoding='utf-8') as f:
            return [l.rstrip() for l in f if l.strip()]
    except Exception:
        return []

def _data_pack(match):
    out = []
    if match in ROSTER_MATCHES:
        for fn in ROSTER_FILES:
            lines = _read_rows(os.path.join(DATA_DIR, fn))
            if len(lines) > 1:
                out.append('## ' + fn + '\n' + '\n'.join(lines))
        if out:
            out.insert(0, 'LIVE ESTATE DATA — single source of truth. '
                          'Use these rows; do not invent beyond them:')
    if match in EQUIP_MATCHES:
        lines = _read_rows(os.path.join(DATA_DIR, 'equipment.csv'))
        if len(lines) > 1:
            out.append('## equipment.csv (real inventory)\n' +
                       '\n'.join(lines))
    if match in CHANNEL_MATCHES and os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, encoding='utf-8') as f:
            out.append('## YouTube channels (real, live)\n' + f.read())
    return '\n\n'.join(out)

QWEN_KEY = os.getenv('QWEN_API_KEY', '')

async def qwen_verify(flags):
    if not QWEN_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                'https://ws-rhaqwof3a8jodd0y.ap-southeast-1.maas.aliyuncs.com/'
                'compatible-mode/v1/chat/completions',
                headers={'Authorization': f'Bearer {QWEN_KEY}',
                         'Content-Type': 'application/json'},
                json={'model': 'qwen-plus',
                      'enable_search': True,
                      'messages': [{'role': 'user', 'content':
                          'You are the verification desk of Shack '
                          'Entertainment. Using live web search, check '
                          'each flagged claim. Reply in at most 3 lines, '
                          'each starting VERIFIED: or UNVERIFIABLE: with '
                          'the truth and one source. Claims:\n' +
                          '\n'.join(flags)}]})
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content'].strip()
    except Exception:
        return '(Qwen verify failed — check key/connection)'

async def qwen_audit(text):
    try:
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                'https://ws-rhaqwof3a8jodd0y.ap-southeast-1.maas.aliyuncs.com/'
                'compatible-mode/v1/chat/completions',
                headers={'Authorization': f'Bearer {QWEN_KEY}',
                         'Content-Type': 'application/json'},
                json={'model': 'qwen-plus',
                      'enable_search': True,
                      'messages': [{'role': 'user', 'content':
                          'You are Shack Entertainment\'s verification '
                          'desk. Brand lock: Shack Entertainment\'s '
                          'in-house news publication is Shack News '
                          'Network (SNN); Shacknews (shacknews.com) is '
                          'an unrelated third party. The draft below may '
                          'contain wrong '                          'registry numbers, dates, emails or prices. '
                          'Using live web search, check every such '
                          'specific claim. Reply in up to 5 lines, each '
                          'starting CORRECT: or WRONG: <claim> -> '
                          '<truth + source>. If nothing is wrong, reply '
                          'one line: ALL CLAIMS CHECKED OK. Never invent '
                          'URLs, sources or access dates; if you have no '
                          'live search result for a claim, start that line '
                          'UNVERIFIABLE:. Only mark WRONG when your live '
                          'snippet explicitly names the same organisation; '
                          'never correct a curated internal value using a '
                          'snippet about a different entity. Draft:\n' +
                          text[:3000]}]})
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content'].strip()
    except Exception:
        return '(Qwen audit failed — check key/connection)'

async def agent_query(update: Update, context, match: str, label: str,
                      emoji: str, context_file: str = None):
    try:
        if not ANYTHINGLLM_KEY:
            await update.message.reply_text(
                "❌ ANYTHINGLLM_API_KEY missing in configs/.env")
            return

        parts = _msg_text(update).split(' ', 1)
        prompt = parts[1].strip() if len(parts) > 1 else ''
        if not prompt:
            await update.message.reply_text(
                f"Usage: {parts[0]} <your request>\n"
                f"Example: {parts[0]} Pitch a poster concept for a jazz night. Navy/Gold.")
            return

        if context_file and os.path.exists(context_file):
            with open(context_file, encoding='utf-8') as f:
                prompt = ("GROUND TRUTH — Shack Brand & Channel Registry:\n"
                          + f.read() + "\n\nRequest: " + prompt)
        pack = _data_pack(match)
        if pack:
            prompt = prompt + "\n\n" + pack

        thinking = await update.message.reply_text(f"{emoji} {label} is thinking...")
        slug = await _find_slug(match)
        if not slug:
            raise ValueError(f'No workspace matching "{match}" found in AnythingLLM')
        data = await _allm_chat(slug, prompt)
        answer = data.get('textResponse') or '(no response)'
        if len(answer) > 4000:
            answer = answer[:4000] + '\n…(truncated)'

        flags = [l.strip() for l in answer.splitlines()
                 if '[UNVERIFIED' in l.upper()]
        if flags:
            verdict = await qwen_verify(flags)
            if verdict:
                answer = answer + '\n\n🔎 Qwen check:\n' + verdict
            else:
                answer = (answer + '\n\n🔎 QWEN CHECK NEEDED — no API '
                          'key in .env; paste flagged lines to Qwen.')

        if match == 'research analyst' and QWEN_KEY:
            audit = await qwen_audit(answer)
            if audit:
                answer = answer + '\n\n🔎 Qwen audit:\n' + audit

        holds = re.findall(
            r'HOLD:\s*(.+?)\s*\|\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s*\|\s*(\d+)',
            answer)
        if holds:
            notes = []
            for t, s, m in holds:
                hid = scl.add_hold(t.strip(), s, m, source=label)
                notes.append(f"📅 Held #{hid}: {t.strip()} ({s}, {m} min)")
            answer = (answer + '\n\n' + '\n'.join(notes) +
                      '\nReview: /cal pending — book: /cal confirm <id>')
        alerts = re.findall(r'SITEALERT:\s*(.+)', answer)
        if alerts:
            anotes = []
            for a in alerts:
                anotes.append(await asyncio.to_thread(
                    mb.send_site_alert, a.strip()))
            answer = answer + '\n\n' + '\n'.join(anotes)

        await context.bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=thinking.message_id,
            text=f"{emoji} {label}\n\n{answer}")
        await send_voice(update, answer)
    except Exception as e:
        traceback.print_exc()
        try:
            await update.message.reply_text(
                f"❌ {label} error: {type(e).__name__}: {e}")
        except Exception:
            pass

async def cd(update: Update, context):
    await agent_query(update, context, 'creative director', 'Creative Director', '🎨')

async def pa(update: Update, context):
    await agent_query(update, context, 'partnership', 'Partnership Agent', '🤝')

async def ev(update: Update, context):
    await agent_query(update, context, 'events', 'Events Agent', '🎪')

async def finance_cmd(update: Update, context):
    try:
        parts = _msg_text(update).split(' ', 1)
        if len(parts) < 2 or not parts[1].strip():
            await update.message.reply_text(
                "Usage: /finance <question>\nExample: /finance What's our total revenue?")
            return
        thinking = await update.message.reply_text("🔍 Querying database...")
        answer = fq.query_database(parts[1].strip())
        if len(answer) > 4000:
            answer = answer[:4000] + "\n…(truncated)"
        await context.bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=thinking.message_id,
            text=answer)
        await send_voice(update, answer)
    except Exception as e:
        traceback.print_exc()
        try:
            await update.message.reply_text(f"❌ Finance error: {e}")
        except Exception:
            pass

async def fin(update: Update, context):
    """[FINWIRE] Live SQL data first, then Shack Finance interprets it."""
    try:
        parts = _msg_text(update).split(' ', 1)
        if len(parts) < 2 or not parts[1].strip():
            await update.message.reply_text(
                "Usage: /fin <question>\nExample: /fin How healthy is this month's margin?")
            return
        q = parts[1].strip()
        thinking = await update.message.reply_text(
            "📊 Finance Agent is reading the books...")
        data = await asyncio.to_thread(fq.query_database, q)
        answer = data
        slug = await _find_slug('finance')
        if slug:
            try:
                resp = await _allm_chat(
                    slug,
                    "Live data pulled from the Shack database just now:\n"
                    + data +
                    "\n\nMy question: " + q +
                    "\n\nAnswer concisely as Shack's finance lead, using only "
                      "the data above. If it is insufficient, say exactly what "
                      "is missing. Never invent figures.")
                answer = resp.get('textResponse') or data
            except Exception as e:
                print(f"fin agent fallback: {e}")
        if len(answer) > 4000:
            answer = answer[:4000] + "\n…(truncated)"
        await context.bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=thinking.message_id,
            text=f"📊 Finance Agent\n\n{answer}")
        await send_voice(update, answer)
    except Exception as e:
        traceback.print_exc()
        try:
            await update.message.reply_text(f"❌ Finance Agent error: {e}")
        except Exception:
            pass

async def _fq_direct(update: Update, context, question: str):
    try:
        answer = fq.query_database(question)
        if len(answer) > 4000:
            answer = answer[:4000] + "\n…(truncated)"
        await update.message.reply_text(answer)
        await send_voice(update, answer)
    except Exception as e:
        traceback.print_exc()
        try:
            await update.message.reply_text(f"❌ Finance error: {e}")
        except Exception:
            pass

async def f_events(update: Update, context):
    await _fq_direct(update, context, "What events do we have?")

async def f_tickets(update: Update, context):
    await _fq_direct(update, context, "How many tickets sold?")

async def f_artists(update: Update, context):
    await _fq_direct(update, context, "Show me artists on roster")

async def f_products(update: Update, context):
    await _fq_direct(update, context, "What products in stock?")

async def f_revenue(update: Update, context):
    await _fq_direct(update, context, "What's our total revenue?")

async def f_expenses(update: Update, context):
    await _fq_direct(update, context, "What expenses do we have?")

# ============================================================================
# [LOGWIRE] /log expense capture into finance_expenses
# ============================================================================

async def log_cmd(update: Update, context):
    parts = _msg_text(update).split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text(
            "Usage: /log expense <what> | <amount> | [category]\n"
            "Example: /log expense Uber to venue | 14.50 | travel")
        return
    rest = parts[1].strip()
    if not rest.lower().startswith('expense '):
        await update.message.reply_text(
            "Usage: /log expense <what> | <amount> | [category]")
        return
    bits = [b.strip() for b in rest[8:].split('|')]
    if len(bits) < 2:
        await update.message.reply_text(
            "Usage: /log expense <what> | <amount> | [category]")
        return
    desc = bits[0]
    amt = bits[1].replace('£', '').replace(',', '')
    cat = bits[2] if len(bits) > 2 and bits[2] else 'general'
    try:
        out = await asyncio.to_thread(slg.add_expense, desc, amt, cat)
    except ValueError:
        await update.message.reply_text("Amount must be a number, e.g. 14.50")
        return
    except Exception as e:
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ledger error: {e}")
        return
    await update.message.reply_text(out)

# ============================================================================
# [CABINET] 2026-08-16 — remaining workspaces on call
# ============================================================================

AGENTS = [
    ('cos',  'chief of staff',  'Chief of Staff',     '🧠', COS_BRIEF),
    ('ar',   'artist relations','Artist Relations',   '🎤', AR_BRIEF),
    ('mk',   'marketing',       'Marketing Agent',    '📣', REGISTRY),
    ('cs',   'content studio',  'Content Studio',     '🎬', CS_BRIEF),
    ('news', 'news editor',     'Shack News Editor',  '📰', NEWS_BRIEF),
    ('ra',   'research analyst','Research Analyst',   '🔬', RA_BRIEF),
    ('ops',  'site ops',        'Site Ops Agent',     '🛠️', SITE_OPS_BRIEF),
    ('da',   'design agent',    'Design Agent',       '✏️', DESIGN_BRIEF),
    ('bv',   'brand vision',    'Brand Vision',       '🧭', BV_BRIEF),
    ('fd',   'film director',   'Film Director',      '🎥', FD_BRIEF),
    ('cd',   'creative director','Creative Director', '🎭', CD_BRIEF),
    ('comms','communication',   'Communications',     '💬', COMMS_BRIEF),
]

def _make_agent(match, label, emoji, context_file=None):
    async def h(update, context):
        await agent_query(update, context, match, label, emoji, context_file)
    return h

# ============================================================================
# [CALWIRE] /cal — pending holds, confirm, add, today, week
# ============================================================================

async def cal_cmd(update: Update, context):
    parts = _msg_text(update).split()
    sub = parts[1].lower() if len(parts) > 1 else ''
    try:
        if sub == 'pending':
            rows = scl.list_holds()
            if not rows:
                await update.message.reply_text("No pending holds.")
                return
            await update.message.reply_text('Pending holds:\n' + '\n'.join(
                f"#{i} {t} — {s} ({m} min)" for i, t, s, m in rows))
        elif sub == 'confirm':
            if len(parts) < 3:
                await update.message.reply_text("Usage: /cal confirm <id>")
                return
            res = await asyncio.to_thread(scl.confirm_hold, int(parts[2]))
            if not res:
                await update.message.reply_text("No hold with that id.")
                return
            await update.message.reply_text(f"Booked ✅ {res[0]} — {res[1]}")
        elif sub == 'add':
            rest = _msg_text(update).split(' ', 2)
            if len(rest) < 3 or rest[2].count('|') < 2:
                await update.message.reply_text(
                    "Usage: /cal add <title> | <YYYY-MM-DD HH:MM> | <minutes>")
                return
            b = [x.strip() for x in rest[2].split('|')]
            await asyncio.to_thread(scl.add_event, b[0], b[1], b[2])
            await update.message.reply_text(f"Booked ✅ {b[0]} — {b[1]}")
        elif sub in ('today', 'week'):
            days = 1 if sub == 'today' else 7
            evs = await asyncio.to_thread(scl.list_events, days)
            if not evs:
                await update.message.reply_text(
                    f"Nothing in the next {days} day(s).")
                return
            lines = [f"{s[11:16]}  {t}" for s, t in evs]
            head = 'Today:' if sub == 'today' else 'This week:'
            await update.message.reply_text(head + '\n' + '\n'.join(lines))
        else:
            await update.message.reply_text(
                'Usage: /cal pending | confirm <id> | '
                'add <t> | <date> | <min> | today | week')
    except Exception as e:
        traceback.print_exc()
        await update.message.reply_text(f"❌ Calendar error: {e}")

# ============================================================================
# [MAILWIRE] bridge polling + Tier-3 approval commands
# ============================================================================

LAST_CHAT = os.path.join(project_root, 'configs', 'last_chat.txt')

async def remember(update: Update, context):
    try:
        with open(LAST_CHAT, 'w') as f:
            f.write(str(update.effective_chat.id))
    except Exception:
        pass

def _last_chat():
    try:
        with open(LAST_CHAT) as f:
            return f.read().strip()
    except Exception:
        return ''

async def mail_tick(application):
    results = await asyncio.to_thread(mb.check_mail)
    chat = _last_chat()
    if not chat or not results:
        return
    shown = 0
    for r in results:
        if shown >= 10:
            await application.bot.send_message(
                int(chat), f"📬 …and {len(results) - 10} more — see /drafts")
            break
        if 'error' in r:
            await application.bot.send_message(
                int(chat), f"⚠️ Mail bridge {r['account']}: {r['error']}")
        else:
            await application.bot.send_message(
                int(chat),
                f"📬 New mail — {r['account']}@\nFrom: {r['from']}\n"
                f"Subject: {r['subject']}\n"
                f"Draft: {r['draft_id']} ({r['template']})\n"
                f"Review: /drafts — send: /senddraft {r['draft_id']}")
        shown += 1

async def mail_loop(application):
    while True:
        try:
            await asyncio.sleep(15)
            await mail_tick(application)
            await asyncio.sleep(285)
        except Exception as e:
            print(f"mail_loop error: {e}")
            await asyncio.sleep(60)

async def post_init(application):
    asyncio.create_task(mail_loop(application))
    snd.start_news_loop(application)

async def drafts(update: Update, context):
    pend = mb.list_drafts()
    if not pend:
        await update.message.reply_text("No pending drafts.")
        return
    lines = [p.replace('PENDING_', '').replace('.md', '') for p in pend]
    await update.message.reply_text("Pending drafts:\n" + '\n'.join(lines))

async def senddraft(update: Update, context):
    parts = _msg_text(update).split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: /senddraft <draft_id>")
        return
    result = await asyncio.to_thread(mb.send_draft, parts[1].strip())
    await update.message.reply_text(result)

# ============================================================================
# [INTAKE] VOICE + TEXT REGISTRATION
# ============================================================================

async def voice_intake(update: Update, context):
    thinking = await update.message.reply_text("🎙️ Transcribing intake...")
    try:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        tmp = os.path.join(tempfile.gettempdir(),
                           f"intake_{voice.file_unique_id}.ogg")
        await file.download_to_drive(tmp)
        text = await asyncio.to_thread(si.transcribe, tmp)
        res = await asyncio.to_thread(si.register, text, 'voice')
        out = si.summary(res) + f'\n\n📝 Heard: "{text}"'
        await context.bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=thinking.message_id,
            text=out)
        await send_voice(update, si.spoken(res))
    except Exception as e:
        traceback.print_exc()
        try:
            await context.bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=thinking.message_id,
                text=f"❌ Intake error: {e}")
        except Exception:
            pass

async def text_intake(update: Update, context):
    try:
        parts = _msg_text(update).split(' ', 1)
        if len(parts) < 2 or not parts[1].strip():
            await update.message.reply_text(
                "Usage: /intake <spoken-style text>\n"
                "Or simply send a voice note — the bot transcribes it locally.")
            return
        res = si.register(parts[1].strip(), 'text')
        await update.message.reply_text(si.summary(res))
        await send_voice(update, si.spoken(res))
    except Exception as e:
        traceback.print_exc()
        try:
            await update.message.reply_text(f"❌ Intake error: {e}")
        except Exception:
            pass

async def audio(update: Update, context):
    parts = _msg_text(update).split(' ', 1)
    state = parts[1].strip().lower() if len(parts) > 1 else ''
    if state in ('on', 'off'):
        _audio_on['on'] = (state == 'on')
        await update.message.reply_text(
            "🔊 Audio playback ON — replies will also arrive as playable audio."
            if _audio_on['on'] else "🔇 Audio playback off.")
    else:
        await update.message.reply_text("Usage: /audio on | /audio off")

async def sales(update: Update, context):
    try:
        sheet = connect()
        tab_data = None
        for tab in sheet.worksheets():
            if 'form' in tab.title.lower():
                tab_data = tab
                break
        if not tab_data:
            await update.message.reply_text("No sales tab found")
            return
        all_values = tab_data.get_all_values()
        if len(all_values) < 2:
            await update.message.reply_text("No data")
            return
        headers = all_values[0]
        rows = all_values[-5:]
        msg = "Sales:\n\n"
        for i, row in enumerate(rows, 1):
            msg += "Row " + str(i) + ":\n"
            for j, val in enumerate(row):
                if j < len(headers):
                    msg += "  " + str(headers[j]) + ": " + str(val) + "\n"
            msg += "\n"
        await update.message.reply_text(msg)
    except Exception as e:
        traceback.print_exc()
        await update.message.reply_text("ERROR: " + str(e))

async def status(update: Update, context):
    await update.message.reply_text("Bot running")

if __name__ == '__main__':
    app = (Application.builder().token(TELEGRAM_TOKEN)
           .post_init(post_init).build())
    app.add_handler(MessageHandler(filters.ALL, remember), group=-1)
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("sales", sales))
    app.add_handler(CommandHandler("cd", cd))
    app.add_handler(CommandHandler("pa", pa))
    app.add_handler(CommandHandler("ev", ev))
    app.add_handler(CommandHandler("cal", cal_cmd))
    app.add_handler(CommandHandler("fin", fin))
    app.add_handler(CommandHandler("log", log_cmd))
    app.add_handler(CommandHandler("finance", finance_cmd))
    app.add_handler(CommandHandler("events", f_events))
    app.add_handler(CommandHandler("tickets", f_tickets))
    app.add_handler(CommandHandler("artists", f_artists))
    app.add_handler(CommandHandler("products", f_products))
    app.add_handler(CommandHandler("revenue", f_revenue))
    app.add_handler(CommandHandler("expenses", f_expenses))
    app.add_handler(CommandHandler("intake", text_intake))
    app.add_handler(MessageHandler(filters.VOICE, voice_intake))
    app.add_handler(CommandHandler("audio", audio))
    app.add_handler(CommandHandler("drafts", drafts))
    app.add_handler(CommandHandler("senddraft", senddraft))
    for _row in AGENTS:
        app.add_handler(CommandHandler(_row[0], _make_agent(*_row[1:])))

    soc.add_handlers(app)
    sr.add_handlers(app)
    snd.add_handlers(app)
    eqi.add_handlers(app)
    print("Bot started...")
    app.run_polling()