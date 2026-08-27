"""
SHACK ENTERTAINMENT — shack_roster_clerk.py
[ROSTER] Watches roster_drops folders, extracts artist/event data,
appends to Google Sheets (AU Artists, LE Artists, LE Events).
Reads text, PDFs, and images. Auto-assigns next IDs.
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
for d in [AU_DROP, LE_ART_DROP, LE_EVT_DROP]:
    os.makedirs(d, exist_ok=True)

AU_WB = '1XuiEI9Hf2G23ZO3gu6DoBrj1zuWEp-rhP2pWDUOPlYE'
LE_WB = '1WBsT69FpseHJKxk4ryDrvyQfvpByc8GUYoEfFaLy0kg'

SA_FILE = os.path.join(project_root, 'configs', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'
IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')

def get_text_and_images(path):
    fn = os.path.basename(path).lower()
    if fn.endswith(IMG_EXTS):
        im = Image.open(path)
        im.thumbnail((1024, 1024))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=85)
        return '(image)', [base64.b64encode(buf.getvalue()).decode()]
    elif fn.endswith('.pdf'):
        text = ''
        try:
            r = pypdf.PdfReader(path)
            text = '\n'.join((p.extract_text() or '') for p in r.pages)
        except Exception:
            pass
        if len(text.strip()) < 40:
            try:
                doc = fitz.open(path)
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
                img.thumbnail((1024, 1024))
                buf = io.BytesIO()
                img.save(buf, 'JPEG', quality=85)
                doc.close()
                return '(PDF rendered)', [base64.b64encode(buf.getvalue()).decode()]
            except Exception:
                return None, None
        return text[:6000], None
    else:
        try:
            with open(path, encoding='utf-8', errors='replace') as f:
                return f.read()[:6000], None
        except Exception:
            return None, None

PROMPTS = {
    'au': ('You are an agency clerk. Extract artist data for the AU roster. '
           'Return ONLY one CSV line, fields in this order: Artist ID,First Name,'
           'Last Name,Stage Name,Email,Phone,Genre,Status,Notes. Status: Active/Pending.'),
    'le_art': ('You are an agency clerk. Extract artist data for the LE roster. '
               'Return ONLY one CSV line: Artist ID,Artist Name,Genre,Contact Email,'
               'Contact Phone,Manager/Agent,Status,Notes. Status: Active/Pending.'),
    'le_evt': ('You are an agency clerk. Extract event data for the LE master. '
               'Return ONLY one CSV line: Event ID,Event Name,Date,Venue,Capacity,'
               'Ticket Price,Status,Headliner,Support Acts,Notes. Date: YYYY-MM-DD.')
}

async def extract(text, images, prompt):
    full_prompt = prompt + '\n\nDOCUMENT:\n' + text
    msg = {'role': 'user', 'content': full_prompt}
    if images:
        msg['images'] = images
    async with httpx.AsyncClient(timeout=600) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False, 'messages': [msg]})
        r.raise_for_status()
        return r.json()['message']['content'].strip()

async def ingest_all():
    creds = Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)
    
    au_wb = gc.open_by_key(AU_WB)
    le_wb = gc.open_by_key(LE_WB)
    
    def ws_by_part(wb, part):
        for ws in wb.worksheets():
            if part.lower() in ws.title.lower():
                return ws
        raise Exception('no tab matching ' + part)
    au_sheet = ws_by_part(au_wb, 'artists')
    le_art_sheet = ws_by_part(le_wb, 'artist_talent')
    le_evt_sheet = ws_by_part(le_wb, 'events_master')
    
    added = []
    targets = [
        (AU_DROP, 'au', au_sheet, '', 9),
        (LE_ART_DROP, 'le_art', le_art_sheet, 'ART-', 8),
        (LE_EVT_DROP, 'le_evt', le_evt_sheet, 'EVT-2026-', 10)
    ]
    
    for drop_dir, drop_type, sheet, prefix, expected_cols in targets:
        files = [f for f in os.listdir(drop_dir) if os.path.isfile(os.path.join(drop_dir, f))]
        if not files: continue
        
        for fn in sorted(files):
            path = os.path.join(drop_dir, fn)
            text, images = get_text_and_images(path)
            if not text and not images:
                print(f"SKIP (unreadable): {fn}")
                continue
            
            try:
                line = await extract(text, images, PROMPTS[drop_type])
                line = line.splitlines()[0].strip().strip('`').strip()
                parts = line.split(',')
                
                # Always assign the ID ourselves; never trust the model
                records = sheet.col_values(1)
                max_n = 0
                for val in records:
                    m = re.search(r'(\d+)\s*$', str(val).strip())
                    if m: max_n = max(max_n, int(m.group(1)))
                for a in added:
                    m = re.search(r'(\d+)$', a.split(':')[0])
                    if m: max_n = max(max_n, int(m.group(1)))
                parts[0] = ('%s%03d' % (prefix, max_n + 1)) if prefix else str(max_n + 1)
                
                # Pad or trim CSV fields to match sheet columns
                if len(parts) > expected_cols:
                    parts = parts[:expected_cols-1] + [','.join(parts[expected_cols-1:])]
                elif len(parts) < expected_cols:
                    parts += [''] * (expected_cols - len(parts))
                
                sheet.append_row(parts)
                added.append(f"{parts[0]}: {fn}")
                
                done_dir = os.path.join(drop_dir, 'processed')
                os.makedirs(done_dir, exist_ok=True)
                shutil.move(path, os.path.join(done_dir, fn))
                print(f"Added {parts[0]} from {fn}")
            except Exception as e:
                print(f"SKIP (error): {fn} - {e}")
                
    return added

async def roster_cmd(update, context):
    await update.message.reply_text('📋 Roster clerk reading drops...')
    try:
        added = await ingest_all()
        if added:
            await update.message.reply_text('Roster updated:\n' + '\n'.join(added))
        else:
            await update.message.reply_text('No new drops found.')
    except Exception as e:
        await update.message.reply_text(f'❌ Error: {e}')

def add_handlers(app):
    app.add_handler(CommandHandler('roster', roster_cmd))

if __name__ == '__main__':
    asyncio.run(ingest_all())