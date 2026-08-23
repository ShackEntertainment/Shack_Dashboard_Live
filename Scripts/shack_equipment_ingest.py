"""
SHACK ENTERTAINMENT — shack_equipment_ingest.py
[EQUIP] Reads receipts from Data\receipts, asks the local 4B for
one CSV row each, appends to Data\equipment.csv, moves the receipt
to Data\receipts\processed. Human reviews the rows afterwards.
"""
from telegram.ext import CommandHandler
import os
import re
import shutil
import asyncio
import httpx
import pypdf

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DATA = os.path.join(project_root, 'Data')
REC = os.path.join(DATA, 'receipts')
DONE = os.path.join(REC, 'processed')
CSV = os.path.join(DATA, 'equipment.csv')
os.makedirs(DONE, exist_ok=True)

HEADER = ('id,item,category,serial,status,location,purchased,price,'
          'seller,notes')
OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'

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

async def extract(text):
    prompt = (
        'You are an inventory clerk. From this purchase receipt extract '
        'exactly one equipment line. Return ONLY one CSV line, fields in '
        'this order: item,category,serial,status,location,purchased,price,'
        'seller,notes. category is one of: camera,lens,lighting,audio,'
        'broadcast,computer,rigging,other. purchased is YYYY-MM-DD. '
        'serial blank if absent. status is active. location is studio. '
        'No commas inside fields - use spaces. No quotes. One line only.'
        '\n\nRECEIPT:\n' + text[:6000])
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False,
            'messages': [{'role': 'user', 'content': prompt}]})
        r.raise_for_status()
        return r.json()['message']['content'].strip()

def next_id(rows):
    n = 0
    for l in rows:
        m = re.match(r'EQ_(\d+)', l)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1

async def main():
    if not os.path.exists(CSV):
        with open(CSV, 'w', encoding='utf-8') as f:
            f.write(HEADER + '\n')
    with open(CSV, encoding='utf-8') as f:
        rows = [l.rstrip() for l in f if l.strip()]
    if not rows or not rows[0].startswith('id,'):
        rows.insert(0, HEADER)
    nid = next_id(rows)
    added = []
    for fn in sorted(os.listdir(REC)):
        p = os.path.join(REC, fn)
        if not os.path.isfile(p):
            continue
        text = receipt_text(p)
        if len(text.strip()) < 40:
            print('SKIP (no readable text - enter by hand):', fn)
            continue
        try:
            line = await extract(text)
        except Exception as e:
            print('SKIP (model error):', fn, e)
            continue
        line = line.splitlines()[0].strip().strip('`').strip()
        rows.append('EQ_%03d,%s' % (nid, line))
        added.append('%s -> EQ_%03d' % (fn, nid))
        nid += 1
        shutil.move(p, os.path.join(DONE, fn))
    with open(CSV, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    print('added %d row(s):' % len(added))
    for a in added:
        print(' ', a)
    return added

if __name__ == '__main__':
    asyncio.run(main())

async def equip_cmd(update, context):
    await update.message.reply_text('🔧 Clerk reading receipts...')
    try:
        added = await main()
    except PermissionError:
        await update.message.reply_text(
            '❌ Excel is holding equipment.csv — close it and tap /equip again.')
        return
    if added:
        await update.message.reply_text(
            'Equipment logged:\n' + '\n'.join(added) +
            '\nReview the rows in Data\\equipment.csv.')
    else:
        await update.message.reply_text(
            'No new readable receipts in the folder.')

def add_handlers(app):
    app.add_handler(CommandHandler('equip', equip_cmd))