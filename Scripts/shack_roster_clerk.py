"""
SHACK ENTERTAINMENT — shack_roster_clerk.py
[ROSTER] Watches roster_drops folders, extracts artist/event data,
appends to Google Sheets (AU Artists, LE Artist_Talent, LE Events).
All IDs are minted by the clerk (ART-, LE-, EVT-2026-); writes are
explicit A-column updates at the first empty row — no append_row.
"""
import os
import re
import shutil
import asyncio
import base64
import io
import httpx
import fitz
from PIL import Image
import pypdf
from telegram.ext import CommandHandler
import gspread
from google.oauth2.service_account import Credentials

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DATA = os.path.join(project_root, 'Data')
DROPS = os.path.join(DATA, 'roster_drops')

AU_DROP = os.path.join(DROPS, 'au_artists')
LE_ART_DROP = os.path.join(DROPS, 'le_artists')
LE_EVT_DROP = os.path.join(DROPS, 'le_events')
for d in (AU_DROP, LE_ART_DROP, LE_EVT_DROP):
    os.makedirs(d, exist_ok=True)

AU_WB = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'
LE_WB = '1WBsT69FpseHJKxk4ryDrvyQfvpByc8GUYoEfFaLy0kg'

SA_FILE = os.path.join(project_root, 'configs', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'
IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')

MODEL_COLS = {'au': 4, 'le_art': 6, 'le_evt': 8}

PROMPTS = {
    'au': ('You are an agency clerk. From the document extract the artist. '
           'Return ONLY one CSV line with exactly 4 fields separated by commas: '
           'Artist Name,Art Type/Discipline,Contact Email,Tier. '
           'Tier one of: Emerging, Established, Headliner. '
           'Inside a field use spaces, never commas.'),
    'le_art': ('You are an agency clerk. From the document extract the artist. '
               'Return ONLY one CSV line with exactly 6 fields separated by commas: '
               'Artist Name,Discipline,Contact Email,Contact Phone,'
               'Fee_Type,Fee_Amount. Fee_Type one of: Fixed, '
               '% Split (70/30), Door Deal, Revenue Share. '
               'Inside a field use spaces, never commas.'),
    'le_evt': ('You are an agency clerk. From the document extract the event. '
               'Return ONLY one CSV line with exactly 8 fields separated by commas: '
               'Event Name,Event Type,Venue Name,Venue Address,Event Date,'
               'Doors Open,Show Start,Capacity Total. Date YYYY-MM-DD, '
               'times HH:MM. Inside a field use spaces, never commas.')
}

def get_text_and_images(path):
    fn = os.path.basename(path).lower()
    if fn.endswith(IMG_EXTS):
        im = Image.open(path)
        im.thumbnail((1024, 1024))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=85)
        return '(image)', [base64.b64encode(buf.getvalue()).decode()]
    if fn.endswith('.pdf'):
        text = ''
        try:
            r = pypdf.PdfReader(path)
            text = '\n'.join((p.extract_text() or '') for p in r.pages)
        except Exception:
            pass
        if len(text.strip()) < 40:
            try:
                doc = fitz.open(path)
                pix = doc[0].get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes('RGB', pix.width, pix.height, pix.samples)
                img.thumbnail((1024, 1024))
                buf = io.BytesIO()
                im2 = img.convert('RGB')
                im2.save(buf, 'JPEG', quality=85)
                doc.close()
                return '(PDF rendered)', [base64.b64encode(buf.getvalue()).decode()]
            except Exception:
                return None, None
        return text[:6000], None
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()[:6000], None
    except Exception:
        return None, None

async def extract(text, images, prompt):
    msg = {'role': 'user', 'content': prompt + '\n\nDOCUMENT:\n' + text}
    if images:
        msg['images'] = images
    async with httpx.AsyncClient(timeout=600) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False, 'messages': [msg]})
        r.raise_for_status()
        return r.json()['message']['content'].strip()

def build_row(drop_type, parts, new_id):
    if drop_type == 'au':
        name, disc, email, tier = parts
        return ([new_id, name, disc, email, 'Yes', tier, '', '',
                 'Active', '', '', ''], name)
    if drop_type == 'le_art':
        name, disc, email, phone, fee_type, fee_amount = parts
        return ([new_id, name, disc, email, phone, fee_type, fee_amount,
                 '', '', '', ''], name)
    name, etype, venue, addr, edate, doors, start, cap = parts
    return ([new_id, name, etype, venue, addr, edate, doors, start,
             cap, '', cap, 'Planning', 'Bola', '', ''], name)

def first_empty_row(sheet):
    return len(sheet.col_values(2)) + 1

async def ingest_all():
    creds = Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)

    def ws_by_part(wb, part):
        for ws in wb.worksheets():
            if part.lower() in ws.title.lower():
                return ws
        raise Exception('no tab matching ' + part)

    au_wb = gc.open_by_key(AU_WB)
    le_wb = gc.open_by_key(LE_WB)
    sheets = {'au': ws_by_part(au_wb, 'artists'),
              'le_art': ws_by_part(le_wb, 'artist_talent'),
              'le_evt': ws_by_part(le_wb, 'events_master')}
    dirs = {'au': AU_DROP, 'le_art': LE_ART_DROP, 'le_evt': LE_EVT_DROP}
    prefixes = {'au': 'ART-', 'le_art': 'LE-', 'le_evt': 'EVT-2026-'}

    added = []
    for drop_type in ('au', 'le_art', 'le_evt'):
        drop_dir = dirs[drop_type]
        sheet = sheets[drop_type]
        for fn in sorted(os.listdir(drop_dir)):
            p = os.path.join(drop_dir, fn)
            if not os.path.isfile(p):
                continue
            text, images = get_text_and_images(p)
            if not text and not images:
                print('SKIP (unreadable):', fn)
                continue
            try:
                line = await extract(text, images, PROMPTS[drop_type])
            except Exception as e:
                print('SKIP (model error):', fn, e)
                continue
            parts = [x.strip() for x in
                     line.splitlines()[0].strip().strip('`').split(',')]
            n = MODEL_COLS[drop_type]
            if len(parts) > n:
                parts = parts[:n - 1] + [', '.join(parts[n - 1:])]
            while len(parts) < n:
                parts.append('')
            max_n = 0
            for val in sheet.col_values(1):
                m = re.search(r'(\d+)\s*$', str(val).strip())
                if m:
                    max_n = max(max_n, int(m.group(1)))
            for a in added:
                m = re.search(r'(\d+)$', a.split(':')[0])
                if m:
                    max_n = max(max_n, int(m.group(1)))
            new_id = '%s%03d' % (prefixes[drop_type], max_n + 1)
            row, label = build_row(drop_type, parts, new_id)
            try:
                nxt = first_empty_row(sheet)
                sheet.update('A%d' % nxt, [row], value_input_option='RAW')
            except Exception as e:
                print('SKIP (sheet error):', fn, e)
                continue
            added.append('%s: %s' % (new_id, fn))
            done = os.path.join(drop_dir, 'processed')
            os.makedirs(done, exist_ok=True)
            shutil.move(p, os.path.join(done, fn))
            print('added', added[-1])
    return added

async def roster_cmd(update, context):
    await update.message.reply_text('📋 Roster clerk reading drops...')
    try:
        added = await ingest_all()
    except Exception as e:
        await update.message.reply_text('❌ Error: ' + str(e))
        return
    if added:
        await update.message.reply_text('Roster updated:\n' + '\n'.join(added))
    else:
        await update.message.reply_text('No new drops found.')

def add_handlers(app):
    app.add_handler(CommandHandler('roster', roster_cmd))

if __name__ == '__main__':
    asyncio.run(ingest_all())
