import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

pages_to_check = [
    'dashboards/pages/2_Live_Exchange.py',
    'dashboards/pages/3_News_Network.py', 
    'dashboards/pages/4_Financial_Overview.py',
    'dashboards/pages/7_Command_Center.py',
]

for p in pages_to_check:
    with open(p, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    name = p.split('/')[-1]
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if 'error_msg' in stripped and ('st.' in stripped or 'warning' in stripped or 'error' in stripped.lower()):
            print(name + ':' + str(i) + ': ' + stripped[:150])
