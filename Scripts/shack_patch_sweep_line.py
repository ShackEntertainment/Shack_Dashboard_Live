import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_ops_sweep.py')
with open(p, encoding='utf-8') as f:
    t = f.read()
old = "lines.append('🔒 Subscriber path — PAUSED pending rebuild (Door 4)')"
new = "lines.append('🟢 Subscriber path — OPEN inbound (intake only); outbound dispatch frozen')"
assert t.count(old) == 1, 'sweep line not found'
t = t.replace(old, new)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('sweep line updated')