"""
SHACK ENTERTAINMENT — shack_render.py
[RENDPIPE] 2026-08-19 — Design Agent autonomy: agent writes the words,
a locked brand template supplies the look, headless Edge renders PNGs
to Telegram for review. Zero subscriptions, fully local.
"""
import os
import asyncio
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler
import httpx
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
out_dir = os.path.join(project_root, 'assets', 'Social_Out')
logo_dir = os.path.join(project_root, 'assets', 'Shack_Logos')
os.makedirs(out_dir, exist_ok=True)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

ANYTHINGLLM_URL = os.getenv('ANYTHINGLLM_URL', 'http://localhost:3001')
ANYTHINGLLM_KEY = os.getenv('ANYTHINGLLM_API_KEY', '')
BRIEF = os.path.join(project_root, 'configs', 'design_brief.txt')

EDGE = None
for _p in (r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
           r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'):
    if os.path.exists(_p):
        EDGE = _p
        break

SIZES = [('IG', 1080, 1350), ('X', 1600, 900)]

LOGOS = {'shack': 'shack_trans.png', 'live': 'live_exchange_trans.png',
         'artists': 'artists_unlimited_trans.png', 'news': 'shack_news_trans.png'}

TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&family=Inter:wght@300;500;600&display=swap');
html,body{margin:0;padding:0}
.card{width:100vw;height:100vh;background:#1e1638;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;box-sizing:border-box;padding:6%;}
.headline{font-family:'Montserrat',sans-serif;font-weight:800;color:#ffffff;font-size:9vh;letter-spacing:1px;margin:0 0 4vh 0;}
.quote{font-family:'Inter',sans-serif;font-weight:500;color:#ffffff;font-size:5vh;line-height:1.4;margin:0 0 4vh 0;max-width:80%;}
.tagline{font-family:'Inter',sans-serif;font-weight:300;color:#f3cc13;font-size:4vh;margin:0 0 6vh 0;}
.logo{height:18vh;}
</style>
</head>
<body>
<div class="card">
  <div class="headline">@@HEADLINE@@</div>
  <div class="quote">@@QUOTE@@</div>
  <div class="tagline">@@TAGLINE@@</div>
  <img class="logo" src="@@LOGO@@">
</div>
</body>
</html>'''

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

def _parse_spec(text):
    spec = {}
    for line in text.splitlines():
        line = line.strip()
        for key in ('HEADLINE', 'QUOTE', 'TAGLINE', 'LOGO'):
            if line.upper().startswith(key + ':'):
                spec[key] = line.split(':', 1)[1].strip()
    return spec

def _render(html_path, out_path, w, h):
    cmd = [EDGE, '--headless=new', '--disable-gpu', '--hide-scrollbars',
           '--force-device-scale-factor=1', '--allow-file-access-from-files',
           '--virtual-time-budget=10000',
           f'--window-size={w},{h}',
           f'--screenshot={out_path}',
           'file:///' + html_path.replace('\\', '/')]
    subprocess.run(cmd, timeout=90, capture_output=True)
    return os.path.exists(out_path)

async def dar(update, context):
    parts = (update.message.text or '').split(' ', 1)
    if len(parts) < 2 or not parts[1].strip():
        await update.message.reply_text("Usage: /dar <design request>")
        return
    await update.message.reply_text("🎨 Design Agent is creating...")
    brief = ''
    if os.path.exists(BRIEF):
        brief = open(BRIEF, encoding='utf-8').read()
    prompt = (brief + '\n\nREQUEST: ' + parts[1].strip() +
              '\nReturn EXACTLY four lines and nothing else:\n'
              'HEADLINE: <short name or title>\n'
              'QUOTE: <one-sentence quote>\n'
              'TAGLINE: <two to four words>\n'
              'LOGO: <shack|live|artists|news>')
    try:
        slug = await _find_slug('design')
        if not slug:
            await update.message.reply_text(
                "No design workspace found in AnythingLLM.")
            return
        data = await asyncio.wait_for(_allm_chat(slug, prompt), timeout=400)
        text = data.get('textResponse') or ''
    except asyncio.TimeoutError:
        await update.message.reply_text(
            "Model stalled (>6 min). Try again or check Ollama.")
        return
    except Exception as e:
        await update.message.reply_text(
            f"Render pipe error: {type(e).__name__}: {e}")
        return
    spec = _parse_spec(text)
    if 'HEADLINE' not in spec:
        await update.message.reply_text(
            "Agent reply missing spec lines:\n" + text[:400])
        return
    logo_file = LOGOS.get(spec.get('LOGO', 'shack').lower().split()[0]
                          if spec.get('LOGO') else 'shack', 'shack_trans.png')
    logo_path = os.path.join(logo_dir, logo_file)
    if not os.path.exists(logo_path):
        logo_path = os.path.join(logo_dir, 'shack_trans.png')
    html = (TEMPLATE
            .replace('@@HEADLINE@@', spec.get('HEADLINE', ''))
            .replace('@@QUOTE@@', spec.get('QUOTE', ''))
            .replace('@@TAGLINE@@', spec.get('TAGLINE', ''))
            .replace('@@LOGO@@', 'file:///' + logo_path.replace('\\', '/')))
    ts = datetime.now().strftime('%y%m%d_%H%M%S')
    html_path = os.path.join(out_dir, 'render_' + ts + '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    if not EDGE:
        await update.message.reply_text("Edge not found; HTML saved: " + html_path)
        return
    for name, w, h in SIZES:
        out_path = os.path.join(out_dir, f'ShackEnt_{name}_{ts}.png')
        ok = await asyncio.to_thread(_render, html_path, out_path, w, h)
        if ok:
            with open(out_path, 'rb') as f:
                await update.message.reply_photo(
                    photo=f, caption=f'{name} {w}x{h} - review')
        else:
            await update.message.reply_text(f'{name} render failed')

def add_handlers(app):
    app.add_handler(CommandHandler('dar', dar))