import os, re
script_dir = os.path.dirname(os.path.abspath(__file__))

CHAT_NEW = '''def _chat(slug, text):
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
    return out'''

def splice(t, pred, new_block):
    lines = t.split('\n')
    s = next(i for i, l in enumerate(lines) if pred(l))
    e = next(i for i in range(s + 1, len(lines)) if lines[i].startswith('def '))
    lines[s:e] = new_block.split('\n')
    return '\n'.join(lines)

p = os.path.join(script_dir, 'shack_runstage.py')
t = open(p, encoding='utf-8').read()
t = splice(t, lambda l: l.startswith('def _chat'), CHAT_NEW)
lines = t.split('\n')
for i, l in enumerate(lines):
    if 'fn = os.path.join(PACKS' in l and "card['deal']" in l:
        ind = l[:len(l) - len(l.lstrip())]
        lines[i] = (ind + "os.makedirs(os.path.join(PACKS, card['deal']), exist_ok=True)\n" +
                    ind + 'fn = os.path.join(PACKS, card[\'deal\'], f"{card[\'deal\']}_S{nxt}_{t[\'agent\']}.md")')
        break
else:
    raise AssertionError('runstage pack line not found')
t = '\n'.join(lines)
m = re.search(r'os\.path\.join\(OUT, f"(.+?)_reply\.md"\)', t)
assert m, 'reply write not found'
inner = m.group(1)
deal_expr = inner.split('_S')[0]
t = t.replace(m.group(0),
    f'(os.makedirs(os.path.join(OUT, {deal_expr}), exist_ok=True) '
    f'or os.path.join(OUT, {deal_expr}, f"{inner}_reply.md"))')
open(p, 'w', encoding='utf-8').write(t)
print('shack_runstage.py patched')

p = os.path.join(script_dir, 'shack_conductor_mcp.py')
t = open(p, encoding='utf-8').read()
lines = t.split('\n')
for i, l in enumerate(lines):
    if 'fn = os.path.join(PACKS' in l and 'code' in l:
        ind = l[:len(l) - len(l.lstrip())]
        lines[i] = (ind + "os.makedirs(os.path.join(PACKS, code), exist_ok=True)\n" +
                    ind + 'fn = os.path.join(PACKS, code, f"{code}_S{nxt}_{t[\'agent\']}.md")')
        break
else:
    raise AssertionError('conductor pack line not found')
t = '\n'.join(lines)
open(p, 'w', encoding='utf-8').write(t)
print('shack_conductor_mcp.py patched')