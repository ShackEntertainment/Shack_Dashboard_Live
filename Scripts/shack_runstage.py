"""
SHACK ENTERTAINMENT — shack_runstage.py
Fires the deal's current stage packs into each agent's AnythingLLM workspace,
banks replies into outputs\{deal}\, returns the summary for the bot.
Retry bone: one automatic re-fire on error. Per-deal folders throughout.
"""
import os, sys, re, json, time
import httpx
from datetime import date
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
load_dotenv(os.path.join(script_dir, '.env'))

ALLM = os.getenv('ANYTHINGLLM_BASE', 'http://localhost:3001')
KEY = os.getenv('ANYTHINGLLM_API_KEY', '')
DEALS = os.path.join(project_root, 'Data', 'deals')
PACKS = os.path.join(DEALS, 'packs')
OUT = os.path.join(DEALS, 'outputs')
os.makedirs(OUT, exist_ok=True)

NAMES = {"da": "design agent", "content": "content studio", "comms": "communications",
         "marketing": "marketing agent", "snn": "shack news", "ra": "research analyst",
         "le": "the live exchange", "au": "artists unlimited", "cos": "chief of staff",
         "ryan": "finance",
         "film": "film director"}

def _workspaces():
    r = httpx.get(ALLM + '/api/v1/workspaces',
                  headers={'Authorization': f'Bearer {KEY}'}, timeout=15)
    return {w['name'].lower(): w['slug'] for w in r.json().get('workspaces', [])}

def _chat(slug, text):
    out = '(error: no attempt)'
    for attempt in (1, 2):
        try:
            r = httpx.post(f'{ALLM}/api/v1/workspace/{slug}/chat',
                           headers={'Authorization': f'Bearer {KEY}'},
                           json={'message': text, 'mode': 'chat'}, timeout=600)
            out = r.json().get('textResponse', '(no textResponse)')
        except Exception as e:
            out = f'(error: {e})'
        if not out.startswith('(error'):
            break
        time.sleep(5)
    return out

def _pack(card, nxt, t):
    sub = os.path.join(PACKS, card['deal'])
    os.makedirs(sub, exist_ok=True)
    fn = os.path.join(sub, f"{card['deal']}_S{nxt}_{t['agent']}.md")
    if not os.path.exists(fn):
        body = '\n'.join([
            f"# {card['deal']} — Stage {nxt} task for {t['agent'].upper()}",
            f"Action: {t['action']}",
            f"Params: {json.dumps(t['params'])}",
            "Deal constraints:",
            *['- ' + x for x in card['constraints']],
            f"Client: {card['client']} — {card['summary']}",
            "Date: " + date.today().isoformat(),
            "Save your output as a draft in your outputs folder.",
            "End with the question it answers and the approval it awaits.",
            "Report only what you produce. No moves, no publishing.",
        ])
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(body)
    return fn

def run(code):
    m = re.match(r'^(DEAL-[A-Z0-9]+)(?:-S\d+)?$', code.strip().upper())
    if not m:
        return f'Unrecognised deal code: {code}'
    code = m.group(1)
    p = os.path.join(DEALS, code + '.json')
    if not os.path.exists(p):
        return f'No deal card {code}.json'
    with open(p, encoding='utf-8') as f:
        card = json.load(f)
    nxt = card['status']['current_stage'] + 1
    stage = next((s for s in card['stages'] if s['stage'] == nxt), None)
    if stage is None:
        return f'{code}: no stage {nxt} — card complete or malformed.'
    wsmap = _workspaces()
    sub_out = os.path.join(OUT, code)
    os.makedirs(sub_out, exist_ok=True)
    lines = [f'🎼 RUNSTAGE {code} S{nxt}']
    for t in stage['tasks']:
        want = NAMES.get(t['agent'], t['agent'])
        slug = next((v for k, v in wsmap.items() if want in k), None)
        if slug is None:
            lines.append(f"* {t['agent']}: UNMATCHED — no workspace")
            continue
        _pack(card, nxt, t)
        with open(os.path.join(PACKS, code, f"{code}_S{nxt}_{t['agent']}.md"), encoding='utf-8') as f:
            text = f.read()
        reply = _chat(slug, text)
        fn = os.path.join(sub_out, f"{code}_S{nxt}_{t['agent']}_reply.md")
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(reply)
        lines.append(f"* {t['agent']}: reply banked -> {os.path.relpath(fn, DEALS)}")
    return ('\n'.join(lines) +
            f"\nReview replies, then /approve {code}-S{nxt} to release the gate.")

if __name__ == '__main__':
    print(run(sys.argv[1]))