"""
SHACK ENTERTAINMENT — shack_runstage.py
Step 4b: fire the current stage's packs into each agent's AnythingLLM
workspace; bank replies; Telegram summary. Drafts only; gates stay Bola's.
Usage: py shack_runstage.py DEAL-SPIRITCO
"""
import os, sys, json
import httpx
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, script_dir)
load_dotenv(os.path.join(project_root, 'configs', '.env'), override=True)

ALLM = os.getenv('ANYTHINGLLM_BASE', 'http://localhost:3001')
KEY = os.getenv('ANYTHINGLLM_API_KEY', '')
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER = os.getenv('TELEGRAM_OWNER_CHAT_ID', '')
DEALS = os.path.join(project_root, 'Data', 'deals')
PACKS = os.path.join(DEALS, 'packs')
OUT = os.path.join(DEALS, 'outputs')
os.makedirs(OUT, exist_ok=True)

NAMES = {"da": "design agent", "content": "content studio", "comms": "communications",
         "marketing": "marketing agent", "snn": "shack news", "ra": "research analyst",
         "le": "events agent", "au": "artists unlimited", "cos": "chief of staff",
         "ryan": "finance"}

def _workspaces():
    r = httpx.get(ALLM + '/api/v1/workspaces',
                  headers={'Authorization': f'Bearer {KEY}'}, timeout=15)
    return {w['name'].lower(): w['slug'] for w in r.json().get('workspaces', [])}

def _chat(slug, text):
    r = httpx.post(f"{ALLM}/api/v1/workspace/{slug}/chat",
                   headers={'Authorization': f'Bearer {KEY}'},
                   json={'message': text, 'mode': 'chat'}, timeout=600)
    return r.json().get('textResponse', '(no textResponse)')

def _pack(card, nxt, t):
    fn = os.path.join(PACKS, f"{card['deal']}_S{nxt}_{t['agent']}.md")
    if not os.path.exists(fn):
        body = '\n'.join([
            f"# {card['deal']} — Stage {nxt} task for {t['agent'].upper()}",
            f"Action: {t['action']}",
            f"Params: {json.dumps(t['params'])}",
            "Deal constraints:",
            *['- ' + x for x in card['constraints']],
            f"Client: {card['client']} — {card['summary']}",
            "Save your output as a draft in your outputs folder.",
            "End with the question it answers and the approval it awaits.",
            "Report only what you produce. No moves, no publishing.",
        ])
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(body)
    return fn

def run(code):
    with open(os.path.join(DEALS, code + '.json'), encoding='utf-8') as f:
        card = json.load(f)
    nxt = card['status']['current_stage'] + 1
    st = next((s for s in card['stages'] if s['stage'] == nxt), None)
    if not st:
        return 'All stages done — deal awaits final review.'
    ws = _workspaces()
    lines = []
    for t in st['tasks']:
        agent = t['agent']
        _pack(card, nxt, t)
        want = NAMES.get(agent, '')
        slug = next((s for n, s in ws.items() if want and want in n), None)
        if not slug:
            lines.append(f"* {agent}: UNMATCHED — no workspace; handle manually")
            continue
        with open(os.path.join(PACKS, f"{code}_S{nxt}_{agent}.md"), encoding='utf-8') as f:
            body = f.read()
        try:
            reply = _chat(slug, body)
        except Exception as e:
            reply = f'(error: {e})'
        outp = os.path.join(OUT, f"{code}_S{nxt}_{agent}_reply.md")
        with open(outp, 'w', encoding='utf-8') as f:
            f.write(reply)
        lines.append(f"* {agent}: reply banked -> {os.path.basename(outp)}")
    summary = (f"🎼 RUNSTAGE {code} S{nxt}\n" + '\n'.join(lines) +
               f"\nReview replies, then /approve {code}-S{nxt} to release the gate.")
    try:
        if TOKEN and OWNER:
            httpx.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                       json={'chat_id': int(OWNER), 'text': summary}, timeout=15)
    except Exception:
        pass
    print(summary)

if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv) > 1 else 'DEAL-SPIRITCO')