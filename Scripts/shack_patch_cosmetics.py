import os
script_dir = os.path.dirname(os.path.abspath(__file__))

REPL = {
    'shack_conductor_mcp.py': [
        ("import os, json", "import os, json\nfrom datetime import date"),
        ('"Save your output as a draft in your outputs folder.",',
         '"Date: " + date.today().isoformat(),\n            "Save your output as a draft in your outputs folder.",'),
    ],
    'shack_runstage.py': [
        ("import os, sys, json", "import os, sys, json\nfrom datetime import date"),
        ('"Save your output as a draft in your outputs folder.",',
         '"Date: " + date.today().isoformat(),\n            "Save your output as a draft in your outputs folder.",'),
    ],
    'shack_main_agent.py': [
        ("the asset moves on DA's next tool call", "the gate releases on the next tool call"),
    ],
}
for fn, pairs in REPL.items():
    p = os.path.join(script_dir, fn)
    with open(p, encoding='utf-8') as f:
        t = f.read()
    for old, new in pairs:
        assert t.count(old) >= 1, f'{fn}: anchor not found: {old[:50]}'
        t = t.replace(old, new)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(t)
    print(fn, 'patched')