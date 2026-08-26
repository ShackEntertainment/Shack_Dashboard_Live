"""
SHACK ENTERTAINMENT — shack_snn_mockup.py
[SNN] Today's Shack News Network homepage mockup, full anatomy:
lead + rail, desk tiles, top stories, latest + sidebar, ad rails,
subscribe band, footer. Reads the six desk articles (recursive),
Content Studio voice drafts decks/queries, Unsplash licences images.
"""
import os
import re
import asyncio
import datetime
import httpx
import pypdf

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
ENV = os.path.join(project_root, 'configs', '.env')
DESK = r'C:\Users\Bola\Desktop\Shack Daily News'
OUT = os.path.join(r'C:\Users\Bola\Desktop',
                   'snn_mockup_%s.html' % datetime.date.today())
OLLAMA = 'http://localhost:11434'
MODEL = 'qwen3-vl:4b-instruct'

KEY = ''
if os.path.exists(ENV):
    for ln in open(ENV, encoding='utf-8'):
        if ln.startswith('UNSPLASH_KEY='):
            KEY = ln.split('=', 1)[1].strip()

def doc_text(path):
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

def article_files():
    picked = {}
    allf = []
    for root, _, files in os.walk(DESK):
        for fn in files:
            p = os.path.join(root, fn)
            allf.append((os.path.getmtime(p), p))
    allf.sort(key=lambda t: -t[0])
    for _, p in allf:
        stem, ext = os.path.splitext(os.path.basename(p))
        if ext.lower() not in ('.md', '.txt', '.pdf') or stem in picked:
            continue
        picked[stem] = p
        if len(picked) == 6:
            break
    return list(picked.values())

def section_of(stem):
    s = stem.lower()
    for k, v in (('geo', 'GEOPOLITICS'), ('uk', 'UK NEWS'),
                 ('ai', 'AI & TECHNOLOGY'), ('health', 'HEALTH & WELLBEING'),
                 ('china', 'CHINA'), ('art', 'ARTS')):
        if k in s:
            return v
    return 'SNN'

async def studio(text):
    prompt = ('You are Shack News Network\'s Content Studio. From the '
              'article below produce exactly one line with three '
              'pipe-separated fields: deck | image query | alt text. '
              'deck: one compelling sentence, max 20 words, sober '
              'house style. image query: 3-5 words describing a '
              'photographic scene for the story. alt text: one plain '
              'sentence describing that image. No pipes inside '
              'fields. One line only.\n\nARTICLE:\n' + text[:5000])
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(OLLAMA + '/api/chat', json={
            'model': MODEL, 'stream': False,
            'messages': [{'role': 'user', 'content': prompt}]})
        r.raise_for_status()
        line = r.json()['message']['content'].strip().splitlines()[0]
    parts = [x.strip() for x in line.split('|')]
    while len(parts) < 3:
        parts.append('')
    return parts[:3]

async def unsplash(query, c):
    r = await c.get('https://api.unsplash.com/search/photos',
                    params={'query': query, 'per_page': 1},
                    headers={'Authorization': 'Client-ID ' + KEY})
    r.raise_for_status()
    res = r.json().get('results') or []
    if not res:
        return None
    ph = res[0]
    dl = ph.get('links', {}).get('download_location')
    if dl:
        try:
            await c.get(dl, headers={'Authorization': 'Client-ID ' + KEY})
        except Exception:
            pass
    return {'url': ph['urls']['regular'],
            'credit': ph['user']['name'],
            'page': ph['links']['html']}

def credit(a):
    return ('Photo: <a href="%s">%s</a> / '
            '<a href="https://unsplash.com">Unsplash</a>'
            % (a['page'], a['credit']))

def card(a, cls):
    return ('<article class="%s"><img src="%s" alt="%s">'
            '<span class="tag">%s</span><h2>%s</h2><p>%s</p>'
            '<small>%s</small></article>') % (
        cls, a['img'], a['alt'], a['tag'], a['headline'], a['deck'],
        credit(a))

def latest(a):
    return ('<div class="lrow"><span class="k">%s</span>'
            '<h3>%s</h3><span class="m">%s</span></div>') % (
        a['tag'], a['headline'], a['deck'])

async def main():
    if not KEY:
        print('No UNSPLASH_KEY in configs/.env')
        return
    files = article_files()
    print('articles found:', len(files))
    arts = []
    async with httpx.AsyncClient(timeout=30) as c:
        for path in files:
            text = doc_text(path)
            stem = os.path.splitext(os.path.basename(path))[0]
            m = re.search(r'Headline:\s*(.+)', text)
            headline = m.group(1).strip() if m else stem
            deck, query, alt = await studio(text)
            q = ' '.join((query or headline).split()[:4])
            img = await unsplash(q, c)
            if not img:
                img = await unsplash(' '.join(q.split()[:2]), c)
            arts.append({'tag': section_of(stem), 'headline': headline,
                         'deck': deck, 'alt': alt or headline,
                         'img': img['url'] if img else '',
                         'page': img['page'] if img else '#',
                         'credit': img['credit'] if img else 'Unsplash'})
            print('card:', headline[:60])
    if not arts:
        print('No articles found under', DESK)
        return
    while len(arts) < 6:
        arts.append({'tag': 'SNN', 'headline': '', 'deck': '', 'alt': '',
                     'img': '', 'page': '#', 'credit': 'Unsplash'})
    html = HTML.replace('@@HERO@@', card(arts[0], 'hero'))
    html = html.replace('@@RAIL@@',
                        card(arts[1], 'rail') + card(arts[2], 'rail'))
    html = html.replace('@@TOP@@',
                        ''.join(card(a, 'top') for a in arts[3:6]))
    html = html.replace('@@MOST@@', ''.join(
        '<li>%s</li>' % a['headline'] for a in arts if a['headline']))
    html = html.replace('@@LATEST@@', ''.join(
        latest(a) for a in arts if a['headline']))
    html = html.replace('@@DATE@@',
                        datetime.date.today().strftime('%A, %d %B %Y'))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print('mockup saved:', OUT)

HTML = '''<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>
body{margin:0;font-family:'Space Grotesk',Arial,sans-serif;background:#f4f1ea;color:#111}
header{background:#0b1626;color:#fff;text-align:center;padding:38px 10px 30px;border-bottom:3px solid #e2a93b}
header h1{margin:0;font-family:'Archivo Black';font-size:46px;letter-spacing:3px;text-transform:uppercase}
header p{color:#e2a93b;letter-spacing:6px;margin:10px 0 0;font-size:12px}
nav{background:#12213a;text-align:center;padding:12px}
nav a{color:#e2a93b;text-decoration:none;margin:0 16px;font-size:13px;letter-spacing:2px;font-weight:700}
.date{font-size:11px;letter-spacing:1px;text-transform:uppercase;color:#667;padding:12px 26px}
.page{display:grid;grid-template-columns:170px minmax(0,1fr) 170px;gap:20px;max-width:1680px;margin:0 auto;padding:0 14px}
.adrail .ad{border:1px dashed #b9b2a6;background:#ece7dd;color:#9a938a;font-size:10px;letter-spacing:2px;height:600px;display:flex;align-items:center;justify-content:center;text-align:center;margin-top:14px}
.wrap{min-width:0}
.lead{display:grid;grid-template-columns:2fr 1fr;gap:18px;margin-top:14px}
article{background:#0b1626;color:#fff;padding:16px;margin-bottom:18px}
img{width:100%;object-fit:cover;display:block}
.hero img{height:430px}.rail img{height:185px}.top img{height:140px}
.tag{background:#e2a93b;color:#0b1626;font-size:11px;letter-spacing:2px;padding:4px 9px;display:inline-block;margin:12px 0 8px;font-weight:700}
h2{margin:4px 0;font-family:'Archivo Black';font-size:18px;line-height:1.3}
.hero h2{font-size:30px}.rail h2{font-size:16px}
article p{font-size:13px;color:#cfd6e0;line-height:1.5}
small,small a{color:#8fa0b5;font-size:11px}
.desks{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:6px 0 26px}
.desk{background:#12213a;color:#fff;text-align:center;padding:18px 10px}
.desk b{color:#e2a93b;letter-spacing:2px}
.desk span{display:block;font-size:11px;color:#9ab;margin-top:6px}
.sec{font-family:'Archivo Black';letter-spacing:2px;margin:26px 0 12px;font-size:20px}
.sec em{color:#e2a93b;font-style:normal}
.topgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.cols{display:grid;grid-template-columns:2fr 1fr;gap:24px}
.lrow{border-bottom:1px solid #ddd;padding:12px 0}
.k{color:#b0801f;font-size:11px;letter-spacing:2px;font-weight:700}
h3{margin:4px 0;font-family:'Archivo Black';font-size:15px;color:#12213a}
.m{font-size:12px;color:#667}
.ad.hz{border:1px dashed #b9b2a6;background:#ece7dd;color:#9a938a;font-size:10px;letter-spacing:2px;height:250px;display:flex;align-items:center;justify-content:center;text-align:center;margin:18px 0}
.box{background:#fff;border:1px solid #e2ddd2;padding:16px;margin-bottom:18px}
.box h4{margin:0 0 10px;letter-spacing:2px;font-size:12px;border-left:3px solid #e2a93b;padding-left:8px}
.box ol{margin:0;padding-left:18px;font-size:13px;color:#12213a}
.box li{margin:6px 0}
.band{background:#e2a93b;padding:22px 26px;display:flex;justify-content:space-between;align-items:center;margin-top:30px}
.band h3{margin:0;font-size:20px}.band p{margin:4px 0 0;color:#333;font-size:12px}
.band input{padding:10px;width:260px;border:0}
.band button{background:#0b1626;color:#fff;border:0;padding:10px 18px;letter-spacing:2px;font-weight:700}
footer{background:#0b1626;color:#9ab;padding:34px 26px;font-size:12px}
.fgrid{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:20px}
footer h5{color:#fff;letter-spacing:3px;font-family:'Archivo Black';margin:0 0 10px}
footer b{color:#e2a93b;letter-spacing:2px}
footer div div{margin:6px 0}
.fbot{max-width:1280px;margin:24px auto 0;border-top:1px solid #223;padding-top:14px;display:flex;justify-content:space-between}
@media(max-width:1200px){.page{grid-template-columns:1fr}.adrail{display:none}}
</style></head><body>
<header><h1>Shack News Network</h1>
<p>INDEPENDENT &middot; IN-DEPTH &middot; INFORMED</p></header>
<nav><a>HOME</a><a>UK</a><a>WORLD</a><a>AI &amp; TECH</a><a>ARTS</a>
<a>CHINA</a><a>PODCAST</a><a>ABOUT</a></nav>
<div class="date">@@DATE@@ &mdash; London, United Kingdom
&mdash; internal mockup, nothing published</div>
<div class="page">
<aside class="adrail"><div class="ad">ADVERTISEMENT<br>160 &times; 600</div>
<div class="ad">YOUR AD HERE<br>160 &times; 600</div></aside>
<div class="wrap">
<div class="lead"><div>@@HERO@@</div><div>@@RAIL@@</div></div>
<div class="desks">
<div class="desk"><b>UK</b><span>Home Affairs, Politics, Economy</span></div>
<div class="desk"><b>WORLD</b><span>Geopolitics, Conflicts, Diplomacy</span></div>
<div class="desk"><b>AI &amp; TECH</b><span>AI, Science, Innovation</span></div>
<div class="desk"><b>ARTS</b><span>Fringe, Film, Music, Culture</span></div>
<div class="desk"><b>CHINA</b><span>Business, Tech, Geopolitics</span></div>
</div>
<div class="sec">TOP <em>STORIES</em></div>
<div class="topgrid">@@TOP@@</div>
<div class="cols"><div>
<div class="sec">LATEST <em>NEWS</em></div>
@@LATEST@@
<div class="ad hz">ADVERTISEMENT &mdash; 300 &times; 250</div>
</div><div>
<div class="box"><h4>MOST READ</h4><ol>@@MOST@@</ol></div>
<div class="box"><h4>TOPICS</h4><ol><li>UK Politics</li>
<li>AI &amp; Technology</li><li>Geopolitics</li><li>Creative Arts</li>
<li>Chinese Markets</li><li>Science &amp; Health</li></ol></div>
</div></div>
</div>
<aside class="adrail"><div class="ad">ADVERTISEMENT<br>160 &times; 600</div>
<div class="ad">YOUR AD HERE<br>160 &times; 600</div></aside>
</div>
<div class="band"><div><h3>Get the Daily Briefing</h3>
<p>All six stories, every morning. No noise.</p></div>
<div><input placeholder="Your email address">
<button>SUBSCRIBE</button></div></div>
<footer><div class="fgrid">
<div><h5>SHACK NEWS NETWORK</h5>Independent news coverage across UK
politics, global affairs, AI &amp; technology, arts and culture, and
Chinese business.<br>&copy; 2026 Shack News Network. All rights reserved.</div>
<div><b>SECTIONS</b><div>UK News</div><div>World</div><div>AI &amp; Tech</div>
<div>Arts</div><div>China</div></div>
<div><b>COMPANY</b><div>About Us</div><div>Editorial Standards</div>
<div>Advertise</div><div>Careers</div><div>Contact</div></div>
<div><b>LEGAL</b><div>Privacy Policy</div><div>Terms &amp; Conditions</div>
<div>Cookie Policy</div><div>Corrections</div></div>
</div>
<div class="fbot"><span>Shack News Network is part of Shack Entertainment
Group</span><span>Registered in England &amp; Wales</span></div>
</footer>
</body></html>'''

if __name__ == '__main__':
    asyncio.run(main())