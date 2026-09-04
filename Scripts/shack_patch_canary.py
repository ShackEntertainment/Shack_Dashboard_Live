import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_ops_sweep.py')
with open(p, encoding='utf-8') as f:
    t = f.read()

REPL = []
REPL.append((
"'https://theliveexchange.com'",
"'https://theliveexchange.co.uk'"))
REPL.append((
"r = httpx.get(url, timeout=15, follow_redirects=True)",
"r = httpx.get(url, timeout=15, follow_redirects=True,\n"
"                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ShackSweep/1.0'})"))

for old, new in REPL:
    assert t.count(old) == 1, 'anchor not found: ' + old
    t = t.replace(old, new)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('canary probes fixed')