import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_main_agent.py')
with open(p, encoding='utf-8') as f:
    lines = f.read().split('\n')

NEW = '''def _sayable(t):
    import re
    t = re.sub(r'```.*?```', ' ', t, flags=re.S)
    for a, b in [('**', ''), ('*', ''), ('`', ''), ('#', ''), ('[', ''), (']', ''),
                 ('\\\\', ' '), ('->', ' to '), ('→', ' to '), ('✅', ' done. '),
                 ('🟡', ' pending. '), ('🔴', ' blocked. '), ('🟢', ' '), ('📊', ' '),
                 ('🎯', ' '), ('🔒', ' '), ('📝', ' '), ('💰', ' '), ('🎼', ' '),
                 ('|', ', '), ('---', ' '), ('.md', ' '), ('_', ' '), ('&', ' and ')]:
        t = t.replace(a, b)
    SAY_NAMES = {'cos': 'Chief of Staff', 'le': 'The Live Exchange',
                 'au': 'Artists Unlimited', 'snn': 'Shack News',
                 'da': 'Design Agent', 'ra': 'Research Analyst',
                 'film': 'Film Director', 'comms': 'Communications'}
    for k, v in SAY_NAMES.items():
        t = re.sub(r'\\b' + re.escape(k) + r'\\b', v, t, flags=re.I)
    t = re.sub(r'^\\s*-\\s+', '', t, flags=re.M)
    t = re.sub(r'\\n+', '. ', t)
    t = re.sub(r'\\s+', ' ', t)
    return t.strip()

'''

s = next(i for i, l in enumerate(lines) if l.startswith('def _sayable'))
e = next(i for i in range(s + 1, len(lines)) if lines[i].startswith('async def _tts_send'))
lines[s:e] = NEW.split('\n')

with open(p, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('sayable v3 applied')