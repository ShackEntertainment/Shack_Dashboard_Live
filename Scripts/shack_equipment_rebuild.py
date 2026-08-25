"""
SHACK ENTERTAINMENT — shack_equipment_rebuild.py
[EQ-REBUILD] Re-reads every receipt in Data\receipts\processed,
re-extracts with the corrected prompt, validates each field in code,
rewrites Data\equipment.csv. Keeps curated EQ_001-EQ_005.
Backs up to equipment_backup2.csv first.
"""
import os
import re
import base64
import asyncio
import shutil
import httpx
import pypdf

script_dir = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(script_dir), 'Data')
DONE = os.path.join(DATA, 'receipts', 'processed')
CSV = os.path.join(DATA, 'equipment.csv')
BAK = os.path.join(DATA, 'equipment_backup2.csv')

HEADER = ('id,item,category,serial,status,location,purchased,price,'
          'seller,notes')
CATS = ('camera', 'lens', 'lighting', 'audio', 'broadcast',
        'computer', 'rigging', 'other')
IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')
OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'

PROMPT = (
    'You are an inventory clerk. From this purchase receipt extract '
    'exactly one equipment line with 9 comma-separated fields in this '
    'order: item,category,serial,status,location,purchased,price,'
    'seller,notes. category is one of: camera,lens,lighting,audio,'
    'broadcast,computer,rigging,other. status is active. location is '
    'studio. purchased is YYYY-MM-DD. Leave a field blank if unknown '
    '(two commas in a row). Inside a field use spaces, never commas. '
    'No quotes. One line only. Example: Canon R8 body,camera,,active,'
    'studio,2026-08-24,229.99,Amazon EU,')

def receipt_text(path):
    if path.lower().endswith('.pdf'):
        try:
            r = pypdf.PdfReader(path)
            return '\n'.join((p.extract_text() or '') for p in r.pages)
        except Exception:
            return ''
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return ''

async def extract(text, images, nudge):
    prompt = PROMPT
    if nudge == 2:
        prompt += (' Your previous reply had the wrong number of '
                   'fields. Output exactly 8 commas.')
    msg = {'role': 'user', 'content': prompt + '\n\nRECEIPT:\n' + text[:6000]}
    if images:
        msg['images'] = images
    async with httpx.AsyncClient(timeout=300) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False, 'messages': [msg]})
        r.raise_for_status()
        return r.json()['message']['content'].strip()

def clean(f):
    f = [x.strip() for x in f][:9] + [''] * max(0, 9 - len(f))
    item, cat, serial, status, loc, pur, price, seller, notes = f
    PH = ('item', 'category', 'serial', 'status', 'location',
          'purchased', 'price', 'seller', 'notes', '')
    if cat.lower() not in CATS:
        if cat.lower() not in PH:
            item = (item + ' ' + cat).strip()
        cat = 'other'
    if serial.lower() in PH or len(serial) > 40:
        serial = ''
    status = 'active'
    loc = 'studio'
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', pur):
        pur = ''
    if not re.match(r'^\d+(\.\d+)?$', price):
        price = ''
    if seller.lower() in PH:
        seller = ''
    if notes.lower() in PH:
        notes = ''
    if not item:
        item = 'REVIEW - empty item'
    return [item, cat, serial, status, loc, pur, price, seller, notes]

async def main():
    shutil.copy(CSV, BAK)
    with open(CSV, encoding='utf-8') as f:
        old = [l.rstrip('\n') for l in f if l.strip()]
    rows = [HEADER] + [l for l in old[1:] if re.match(r'EQ_00[1-5],', l)]
    nid = 6
    for fn in sorted(os.listdir(DONE)):
        p = os.path.join(DONE, fn)
        if not os.path.isfile(p):
            continue
        images = None
        if fn.lower().endswith(IMG_EXTS):
            with open(p, 'rb') as fh:
                images = [base64.b64encode(fh.read()).decode()]
            text = '(image receipt - read the picture)'
        else:
            text = receipt_text(p)
        if not images and len(text.strip()) < 40:
            rows.append('EQ_%03d,REVIEW - no readable text,,,,,,, '
                        'enter by hand' % nid)
            nid += 1
            continue
        fields = None
        for attempt in (1, 2):
            try:
                out = await extract(text, images, attempt)
            except Exception as e:
                print('error', fn, type(e).__name__)
                continue
            cand = out.splitlines()[0].strip().strip('`').strip()
            parts = cand.split(',')
            if len(parts) == 9:
                fields = parts
                break
        if fields is None:
            rows.append('EQ_%03d,REVIEW - model format fail,,,,,,, '
                        'enter by hand' % nid)
        else:
            rows.append('EQ_%03d,' % nid + ','.join(clean(fields)))
        print('EQ_%03d <- %s' % (nid, fn))
        nid += 1
    with open(CSV, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    print('rebuilt %d data rows' % (len(rows) - 1))

if __name__ == '__main__':
    asyncio.run(main())