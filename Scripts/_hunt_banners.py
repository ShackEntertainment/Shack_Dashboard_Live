import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# These 3 pages still show yellow banners - find EVERY st.warning/st.error call
targets = [
    'dashboards/pages/3_News_Network.py',
    'dashboards/pages/4_Financial_Overview.py',
    'dashboards/pages/7_Command_Center.py',
]

for p in targets:
    with open(p, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    name = p.split('/')[-1]
    print('=== ' + name + ' ===')
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if 'st.warning' in s or 'st.error' in s:
            # Skip benign ones
            if any(x in s for x in ['export', 'stock', 'barcode', 'coming soon']):
                continue
            print(str(i) + ': ' + s[:180])
    print()
