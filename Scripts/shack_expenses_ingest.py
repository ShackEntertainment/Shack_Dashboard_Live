"""
SHACK ENTERTAINMENT — shack_expenses_ingest.py
[EXP] Reads incidental receipts from Data\finance_receipts, asks the
local 4B for one CSV row each, appends to Data\expenses.csv, moves the
receipt to Data\finance_receipts\processed. Human reviews afterwards.
Vision-enabled for PNG/JPG receipts.
"""
from telegram.ext import CommandHandler
import os
import re
import shutil
import asyncio
import base64
import httpx
import pypdf

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DATA = os.path.join(project_root, 'Data')
REC = os.path.join(DATA, 'finance_receipts')
DONE = os.path.join(REC, 'processed')
CSV = os.path.join(DATA, 'expenses.csv')
os.makedirs(DONE, exist_ok=True)

HEADER = 'id,date,party,description,amount,category,notes'
OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'
IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')

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

async def extract(text, images=None):
    prompt = (
        'You are an expenses clerk. From this receipt extract exactly '
        'one line with 6 comma-separated fields in this order: '
        'date,party,description,amount,category,notes. '
        'date is YYYY-MM-DD. party is who was paid. description is '
        'short item text. amount is a number with 2 decimals. '
        'category is one of: meals,travel,office,client,other. '
        'notes blank unless a business purpose is obvious (example: '
        'client meeting). Inside a field use spaces, never commas. '
        'One line only. Example: 2026-08-26,Costa Coffee,Client '
        'meeting - coffee and pastries,14.60,meals,client meeting'
        '\n\nRECEIPT:\n' + text[:6000])
    msg = {'role': 'user', 'content': prompt}
    if images:
        msg['images'] = images
    async with httpx.AsyncClient(timeout=300) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False, 'messages': [msg]})
        r.raise_for_status()
        return r.json()['message']['content'].strip()

def next_id(rows):
    n = 0
    for l in rows:
        m = re.match(r'EX_(\d+)', l)
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
        images = None
        if fn.lower().endswith(IMG_EXTS):
            with open(p, 'rb') as f:
                images = [base64.b64encode(f.read()).decode()]
            text = '(image receipt - read the picture)'
        else:
            text = receipt_text(p)
        if len(text.strip()) < 20 and not images:
            print('SKIP (no readable text - enter by hand):', fn)
            continue
        try:
            line = await extract(text, images)
        except Exception as e:
            print('SKIP (model error):', fn, e)
            continue
        line = line.splitlines()[0].strip().strip('`').strip()
        rows.append('EX_%03d,%s' % (nid, line))
        added.append('%s -> EX_%03d' % (fn, nid))
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

async def exp_cmd(update, context):
    await update.message.reply_text('🧾 Expenses clerk reading receipts...')
    try:
        added = await main()
    except PermissionError:
        await update.message.reply_text(
            '❌ Excel is holding expenses.csv — close it and tap /exp again.')
        return
    if added:
        await update.message.reply_text(
            'Expenses logged:\n' + '\n'.join(added) +
            '\nReview the rows in Data\\expenses.csv.')
    else:
        await update.message.reply_text(
            'No new readable receipts in finance_receipts.')

def add_handlers(app):
    app.add_handler(CommandHandler('exp', exp_cmd))