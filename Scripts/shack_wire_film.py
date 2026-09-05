import os
script_dir = os.path.dirname(os.path.abspath(__file__))
for fn in ('shack_runstage.py', 'shack_conductor_mcp.py'):
    p = os.path.join(script_dir, fn)
    t = open(p, encoding='utf-8').read()
    t = t.replace('"ryan": "finance"', '"ryan": "finance",\n         "film": "film director"')
    open(p, 'w', encoding='utf-8').write(t)
print('film director wired into NAMES map')