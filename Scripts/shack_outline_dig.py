r"""
SHACK ENTERTAINMENT — shack_outline_dig.py
[DIG] Reads long documents from Data\dig_drops, chews them into a
one-page structured digest (.md) in Data\dig_out, moves the source to
processed. Handles PDF, Word (.doc/.docx via LibreOffice), text and
images. Long texts are chunked, outlined per chunk, then merged.
"""
import os
import shutil
import asyncio
import base64
import io
import datetime
import subprocess
import tempfile
import httpx
import fitz
import pypdf
from PIL import Image
from telegram.ext import CommandHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DATA = os.path.join(project_root, 'Data')
DROPS = os.path.join(DATA, 'dig_drops')
OUT = os.path.join(DATA, 'dig_out')
DONE = os.path.join(DROPS, 'processed')
for d in (DROPS, OUT, DONE):
    os.makedirs(d, exist_ok=True)

OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'
IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')
CHUNK = 9000
OVERLAP = 400
MAX_PAGES = 8

HEADINGS = ('PARTIES, MONEY, DATES & DEADLINES, OBLIGATIONS, '
            'RISKS & RED FLAGS, KEY TERMS, ACTION ITEMS FOR MD, '
            'OPEN QUESTIONS (bullets; if the document leaves nothing '
            'unclear write "none")')

SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.com'
if not os.path.exists(SOFFICE):
    SOFFICE = r'C:\Program Files\LibreOffice\program\soffice.exe'

async def ask(prompt, images=None):
    msg = {'role': 'user', 'content': prompt}
    if images:
        msg['images'] = images
    async with httpx.AsyncClient(timeout=600) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False, 'messages': [msg]})
        r.raise_for_status()
        return r.json()['message']['content'].strip()

def office_text(path):
    tmp = tempfile.mkdtemp()
    try:
        subprocess.run([SOFFICE, '--headless', '--convert-to', 'txt:Text',
                        '--outdir', tmp, path],
                       capture_output=True, timeout=180)
        tp = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + '.txt')
        if os.path.exists(tp):
            with open(tp, encoding='utf-8', errors='replace') as f:
                return f.read()
    except Exception as e:
        print('office convert failed:', path, e)
    return ''

def page_images(path):
    doc = fitz.open(path)
    out = []
    for i in range(min(len(doc), MAX_PAGES)):
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=85)
        out.append(base64.b64encode(buf.getvalue()).decode())
    doc.close()
    return out

async def doc_text(path):
    fn = path.lower()
    if fn.endswith(IMG_EXTS):
        im = Image.open(path)
        im.thumbnail((1024, 1024))
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=85)
        return await ask('Transcribe all text on this page verbatim.',
                         [base64.b64encode(buf.getvalue()).decode()])
    if fn.endswith(('.doc', '.docx')):
        return office_text(path) or None
    if fn.endswith('.pdf'):
        text = ''
        try:
            r = pypdf.PdfReader(path)
            text = '\n'.join((p.extract_text() or '') for p in r.pages)
        except Exception:
            pass
        if len(text.strip()) >= 40:
            return text
        joined = ''
        for img in page_images(path):
            joined += await ask('Transcribe all text on this page verbatim.',
                                [img]) + '\n'
        return joined or None
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception:
        return None

def chunkify(text):
    text = text.strip()
    if len(text) <= CHUNK:
        return [text]
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i + CHUNK])
        i += CHUNK - OVERLAP
    return chunks

async def digest(text):
    chunks = chunkify(text)
    if len(chunks) == 1:
        single = ('You are a paralegal clerk. Produce a one-page digest of '
                  'this document. Use these headings exactly: SUMMARY (one '
                  'paragraph), ' + HEADINGS + '. Bullets concise. Where a '
                  'heading has nothing, write "none".\n\nDOCUMENT:\n'
                  + chunks[0])
        try:
            return await ask(single)
        except Exception:
            await asyncio.sleep(5)
            return await ask(single)
    parts = []
    for k, ch in enumerate(chunks, 1):
        prompt = ('You are a paralegal clerk. From this PART of a document '
                  'extract concise bullets under: ' + HEADINGS +
                  '. Nothing -> "none".\n\nPART %d/%d:\n' % (k, len(chunks))
                  + ch)
        try:
            parts.append(await ask(prompt))
        except Exception:
            print('  part %d failed - retrying once' % k)
            await asyncio.sleep(5)
            try:
                parts.append(await ask(prompt))
            except Exception:
                parts.append('(part %d unreadable)' % k)
        print('  chewed part %d/%d' % (k, len(chunks)))
    merge_prompt = ('You are a paralegal clerk. Merge these part-outlines of '
                    'one document into a single coherent digest. Use these '
                    'headings exactly: SUMMARY (one paragraph inferred from '
                    'the parts), ' + HEADINGS +
                    '. Deduplicate.\n\nPART OUTLINES:\n'
                    + '\n\n---\n\n'.join(parts))
    try:
        return await ask(merge_prompt)
    except Exception:
        return '\n\n---\n\n'.join(parts)

async def main():
    done = []
    for fn in sorted(os.listdir(DROPS)):
        p = os.path.join(DROPS, fn)
        if not os.path.isfile(p):
            continue
        print('digging:', fn)
        try:
            text = await doc_text(p)
        except Exception as e:
            print('SKIP (read error):', fn, e)
            continue
        if not text or len(text.strip()) < 40:
            print('SKIP (no readable text):', fn)
            continue
        try:
            dig = await digest(text)
        except Exception as e:
            print('SKIP (model error):', fn, e)
            continue
        outname = os.path.splitext(fn)[0] + '_digest.md'
        with open(os.path.join(OUT, outname), 'w', encoding='utf-8') as f:
            f.write('# Digest — %s\n_Chewed %s by the local 4B._\n\n%s\n'
                    % (fn, datetime.date.today().isoformat(), dig))
        shutil.move(p, os.path.join(DONE, fn))
        done.append(outname)
        print('digested:', fn, '->', outname)
    print('digested %d document(s)' % len(done))
    return done

async def dig_cmd(update, context):
    await update.message.reply_text('🦴 Dig chewing dropped documents...')
    try:
        done = await main()
    except Exception as e:
        await update.message.reply_text('❌ Error: ' + str(e))
        return
    if done:
        await update.message.reply_text(
            'Digests ready in Data\\dig_out:\n' + '\n'.join(done))
    else:
        await update.message.reply_text('Nothing new in dig_drops.')

def add_handlers(app):
    app.add_handler(CommandHandler('dig', dig_cmd))

if __name__ == '__main__':
    asyncio.run(main())