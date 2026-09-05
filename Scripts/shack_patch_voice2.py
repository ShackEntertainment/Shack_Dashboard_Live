import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    lines = f.read().split('\n')

SAY = '''def _sayable(t):
    import re
    t = re.sub(r'```.*?```', ' ', t, flags=re.S)
    for a, b in [('**', ''), ('*', ''), ('`', ''), ('#', ''), ('[', ''), (']', ''),
                 ('→', ' to '), ('->', ' to '), ('✅', ' done. '), ('🟡', ' pending. '),
                 ('🔴', ' blocked. '), ('🟢', ' '), ('📊', ' '), ('🎯', ' '), ('🔒', ' '),
                 ('📝', ' '), ('💰', ' '), ('🎼', ' '), ('|', ', '), ('---', ' '),
                 ('.md', ' '), ('_', ' '), ('&', ' and ')]:
        t = t.replace(a, b)
    t = re.sub(r'^\\s*-\\s+', '', t, flags=re.M)
    t = re.sub(r'\\n+', '. ', t)
    t = re.sub(r'\\s+', ' ', t)
    return t.strip()

'''

i = next(i for i, l in enumerate(lines) if l.startswith('async def _tts_send'))
lines[i:i] = SAY.split('\n')

i = next(i for i, l in enumerate(lines) if 'edge_tts.Communicate(text[:6000]' in l)
lines[i] = lines[i].replace('Communicate(text[:6000', 'Communicate(_sayable(text)[:6000')

with open(p, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('sayable patch applied')