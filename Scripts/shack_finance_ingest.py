"""
SHACK ENTERTAINMENT - shack_finance_ingest.py
[FIN] Reads invoices/receipts from Data\finance_receipts, asks the
local 4B for one CSV row each, appends to Data\finance.csv, moves the
file to Data\finance_receipts\processed. Human reviews rows after.
"""
import os
import re
import shutil
import asyncio
import httpx
import pypdf

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DATA = os.path.join(project_root, 'Data')
REC = os.path.join(DATA, 'finance_receipts')
DONE = os.path.join(REC, 'processed')
CSV = os.path.join(DATA, 'finance.csv')
os.makedirs(DONE, exist_ok=True)

HEADER = 'id,date,party,description,amount,kind,ref,notes'
OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'

def doc_text(path):
    if path.lower().endswith('.pdf'):
        try:
            r = pypdf.PdfReader(path)
            return '\n'.join((p.extract_text() or '') for p in r.pages)
        except Exception:
            return ''
    try:
        with open(path, encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ''

def next_id(rows):
    top = 0
    for r in rows:
        m = re.match(r'FN_(\d+)', r.split(',')[0])
        if m:
            top = max(top, int(m.group(1)))
    return 'FN_%04d' % (top + 1)

def load():
    rows = []
    if os.path.exists(CSV):
        with open(CSV, encoding='utf-8') as f:
            rows = [l.rstrip('\n') for l in f if l.strip()]
    if not rows or not rows[0].startswith('id,'):
        rows.insert(0, HEADER)
    return rows

async def extract(text):
    body = {'model': MODEL, 'stream': False,
            'messages': [{'role': 'user', 'content':
                'Read this invoice or receipt. Reply with exactly ONE '
                'csv row and nothing else, no quotes: '
                'date,party,description,amount,kind,ref where '
                'date=YYYY-MM-DD, party=who issued or paid, '
                'description=short item text, amount=number 2dp, '
                'kind=expense (money out) or income (money in), '
                'ref=invoice or order number. If unreadable reply '
                'SKIP.' + '\n\n' + text[:6000]}]}
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(OLLAMA + '/api/chat', json=body)
        r.raise_for_status()
        out = r.json()['message']['content'].strip()
    line = out.splitlines()[0].strip() if out else ''
    if not line or 'SKIP' in line.upper():
        return None
    return line

async def main():
    rows = load()
    added = []
    for fn in sorted(os.listdir(REC)):
        p = os.path.join(REC, fn)
        if not os.path.isfile(p):
            continue
        text = doc_text(p)
        if len(text) < 40:
            print('skip (no text):', fn)
            shutil.move(p, os.path.join(DONE, fn))
            continue
        try:
            line = await extract(text)
        except Exception as e:
            print('error on', fn, type(e).__name__)
            continue
        if not line:
            print('skip (model):', fn)
            shutil.move(p, os.path.join(DONE, fn))
            continue
        fid = next_id(rows)
        rows.append(fid + ',' + line + ',')
        added.append(fid + ' <- ' + fn)
        print(fid, '<-', fn, '::', line)
        shutil.move(p, os.path.join(DONE, fn))
    with open(CSV, 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    print('added %d row(s)' % len(added))
    return added

if __name__ == '__main__':
    asyncio.run(main())