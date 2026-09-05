import os, re
script_dir = os.path.dirname(os.path.abspath(__file__))

CHAT_OLD = """def _chat(slug, text):
    r = httpx.post(f'{ALLM}/api/v1/workspace/{slug}/chat',
                   headers={'Authorization': f'Bearer {KEY}'},
                   json={'message': text, 'mode': 'chat'}, timeout=600)
    return r.json().get('textResponse', '(no textResponse)')"""

CHAT_NEW = """def _chat(slug, text):
    import time
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
    return out"""

PACK_RS_OLD = '    fn = os.path.join(PACKS, f"{card[\'deal\']}_S{nxt}_{t[\'agent\']}.md")'
PACK_RS_NEW = ('    os.makedirs(os.path.join(PACKS, card[\'deal\']), exist_ok=True)\n'
               '    fn = os.path.join(PACKS, card[\'deal\'], f"{card[\'deal\']}_S{nxt}_{t[\'agent\']}.md")')

PACK_C_OLD = '        fn = os.path.join(PACKS, f"{code}_S{nxt}_{t[\'agent\']}.md")'
PACK_C_NEW = ('        os.makedirs(os.path.join(PACKS, code), exist_ok=True)\n'
              '        fn = os.path.join(PACKS, code, f"{code}_S{nxt}_{t[\'agent\']}.md")')

# runstage: retry + per-deal packs
p = os.path.join(script_dir, 'shack_runstage.py')
t = open(p, encoding='utf-8').read()
for old, new in [(CHAT_OLD, CHAT_NEW), (PACK_RS_OLD, PACK_RS_NEW)]:
    assert t.count(old) == 1, 'runstage anchor missing: ' + old[:50]
    t = t.replace(old, new)
# runstage: per-deal outputs (regex, inline makedirs)
m = re.search(r'os\.path\.join\(OUT, f"(.+?)_reply\.md"\)', t)
assert m, 'reply write not found'
inner = m.group(1)
deal_expr = inner.split('_S')[0]
t = t.replace(m.group(0),
    f'(os.makedirs(os.path.join(OUT, {deal_expr}), exist_ok=True) '
    f'or os.path.join(OUT, {deal_expr}, f"{inner}_reply.md"))')
open(p, 'w', encoding='utf-8').write(t)
print('shack_runstage.py patched')

# conductor: per-deal packs
p = os.path.join(script_dir, 'shack_conductor_mcp.py')
t = open(p, encoding='utf-8').read()
assert t.count(PACK_C_OLD) == 1, 'conductor anchor missing'
t = t.replace(PACK_C_OLD, PACK_C_NEW)
open(p, 'w', encoding='utf-8').write(t)
print('shack_conductor_mcp.py patched')