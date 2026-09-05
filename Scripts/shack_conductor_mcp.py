"""
SHACK ENTERTAINMENT — shack_conductor_mcp.py
Conductor v2: reads Deal Cards, packs stages into per-agent instructions,
advances gates on approval tokens. Per-deal packs folders.
"""
import os, re, json
from datetime import date
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DEALS = os.path.join(project_root, 'Data', 'deals')
PACKS = os.path.join(DEALS, 'packs')
APDIR = os.path.join(project_root, 'Data', 'approvals')

mcp = FastMCP('ShackConductor')

def _card(code):
    p = os.path.join(DEALS, code + '.json')
    if not os.path.exists(p):
        return None, p
    with open(p, encoding='utf-8') as f:
        return json.load(f), p

def _clean(code):
    m = re.match(r'^(DEAL-[A-Z0-9]+)(?:-S\d+)?$', code.strip().upper())
    return m.group(1) if m else code.strip()

def _packbody(card, nxt, t):
    return '\n'.join([
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

@mcp.tool()
def stage_pack(code: str) -> str:
    """Build pack files for the deal's next stage; returns their paths."""
    code = _clean(code)
    card, _ = _card(code)
    if card is None:
        return f'No deal card {code}.json'
    nxt = card['status']['current_stage'] + 1
    stage = next((s for s in card['stages'] if s['stage'] == nxt), None)
    if stage is None:
        return f'{code}: no stage {nxt} — card complete or malformed.'
    sub = os.path.join(PACKS, code)
    os.makedirs(sub, exist_ok=True)
    paths = []
    for t in stage['tasks']:
        fn = os.path.join(sub, f"{code}_S{nxt}_{t['agent']}.md")
        if not os.path.exists(fn):
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(_packbody(card, nxt, t))
        paths.append(fn)
    return f"Stage {nxt} packs ready:\n" + '\n'.join(paths)

@mcp.tool()
def advance_gate(code: str) -> str:
    """Consume the approval token and pass the next gate."""
    code = _clean(code)
    card, p = _card(code)
    if card is None:
        return f'No deal card {code}.json'
    nxt = card['status']['current_stage'] + 1
    tok = os.path.join(APDIR, f'approved_{code}-S{nxt}.token')
    if not os.path.exists(tok):
        return f'PENDING — no approval token for {code}-S{nxt}. Reply /approve {code}-S{nxt} to release.'
    os.remove(tok)
    card['status']['gates_passed'].append(nxt)
    card['status']['current_stage'] = nxt
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(card, f, indent=2)
    return f'GATE S{nxt} PASSED — {code} now at stage {nxt}. Pack the next stage when ready.'

@mcp.tool()
def card_status(code: str) -> str:
    """Report a deal card's stage state."""
    code = _clean(code)
    card, _ = _card(code)
    if card is None:
        return f'No deal card {code}.json'
    st = card['status']
    return (f"{code}: stage {st['current_stage']}, gates {st['gates_passed']}, "
            f"next S{st['current_stage'] + 1}.")

if __name__ == '__main__':
    mcp.run()