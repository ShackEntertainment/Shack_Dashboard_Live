"""
SHACK ENTERTAINMENT — shack_conductor_mcp.py
Conductor v1: reads Deal Cards, packs stages into per-agent instructions,
advances gates only on Bola's token. Never fires agents itself (v1).
"""
import os, json
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
DEALS = os.path.join(project_root, 'Data', 'deals')
APDIR = os.path.join(project_root, 'Data', 'approvals')
PACKS = os.path.join(DEALS, 'packs')
os.makedirs(PACKS, exist_ok=True)

mcp = FastMCP('ShackConductor')

def _card(code):
    p = os.path.join(DEALS, code + '.json')
    if not os.path.exists(p):
        return None, p
    with open(p, encoding='utf-8') as f:
        return json.load(f), p

@mcp.tool()
def deal_status(code: str) -> str:
    """Current stage, gates passed, and next stage tasks of a deal."""
    c, _ = _card(code)
    if not c:
        return f"No deal card {code}."
    s = c['status']
    nxt = s['current_stage'] + 1
    stages = {st['stage']: st for st in c['stages']}
    tasks = stages.get(nxt, {}).get('tasks', [])
    return (f"{code} | stage {s['current_stage']} done | gates {s['gates_passed']} | "
            f"next stage {nxt}: " + '; '.join(f"{t['agent']}:{t['action']}" for t in tasks))

@mcp.tool()
def stage_pack(code: str) -> str:
    """Write per-agent instruction files for the next stage; returns paths."""
    c, _ = _card(code)
    if not c:
        return f"No deal card {code}."
    nxt = c['status']['current_stage'] + 1
    st = next((s for s in c['stages'] if s['stage'] == nxt), None)
    if not st:
        return 'All stages packed — deal complete pending review.'
    out = []
    for t in st['tasks']:
        fn = os.path.join(PACKS, f"{code}_S{nxt}_{t['agent']}.md")
        body = '\n'.join([
            f"# {code} — Stage {nxt} task for {t['agent'].upper()}",
            f"Action: {t['action']}",
            f"Params: {json.dumps(t['params'])}",
            "Deal constraints:",
            *['- ' + x for x in c['constraints']],
            f"Client: {c['client']} — {c['summary']}",
            "Save your output as a draft in your outputs folder.",
            "End with the question it answers and the approval it awaits.",
            "Report only what you produce. No moves, no publishing.",
        ])
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(body)
        out.append(os.path.basename(fn))
    return 'Packed stage ' + str(nxt) + ': ' + ', '.join(out)

@mcp.tool()
def advance_gate(code: str) -> str:
    """Advance the deal one stage. Requires Bola's /approve token for the stage."""
    c, p = _card(code)
    if not c:
        return f"No deal card {code}."
    nxt = c['status']['current_stage'] + 1
    tok = os.path.join(APDIR, f"approved_{code}-S{nxt}.token")
    if not os.path.exists(tok):
        return f"PENDING — no token for {code}-S{nxt}. Reply /approve {code}-S{nxt} to release."
    c['status']['gates_passed'].append(nxt)
    c['status']['current_stage'] = nxt
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(c, f, indent=2)
    os.remove(tok)
    return f"GATE S{nxt} PASSED — {code} now at stage {nxt}. Pack the next stage when ready."

if __name__ == '__main__':
    mcp.run()