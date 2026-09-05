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

RS_PACK_REPL = ('    os.makedirs(os.path.join(PACKS, card[\'deal\']), exist_ok=True)\n'
                '    fn = os.path.join(PACKS, card[\'deal\'], f"{card[\'deal\']}_S{nxt}_{t[\'agent\']}.md")')
C_PACK_REPL = ('        os.makedirs(os.path.join(PACKS, code), exist_ok=True)\n'
               '        fn = os.path.join(PACKS, code, f"{code}_S{nxt}_{t[\'agent\']}.md")')

p = os.path.join(script_dir, 'shack_runstage.py')
t = open(p, encoding='utf-8').read()
t, n1 = re.subn(r'def _chat\(slug, text\):.*?return r\.json\(\)\.get\(\'textResponse\', \'\(no textResponse\)\'\)',
                lambda m: CHAT_NEW, t, flags=re.S)
assert n1 == 1, '_chat not found'
t, n2 = re.subn(r'[ \t]*fn = os\.path\.join\(PACKS, f"\{card\[.deal.\]\}_S\{nxt\}_\{t\[.agent.\]\}\.md"\)',
                lambda m: RS_PACK_REPL, t)
assert n2 == 1, 'runstage pack line not found'
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
t, n3 = re.subn(r'[ \t]*fn = os\.path\.join\(PACKS, f"\{code\[?}?_S\{nxt\}_\{t\[.agent.\]\}\.md"\)',
                lambda m: C_PACK_REPL, t)
assert n3 == 1, 'conductor pack line not found'
open(p, 'w', encoding='utf-8').write(t)
print('shack_conductor_mcp.py patched')