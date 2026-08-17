import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Check if any page renders error_msg as a warning/banner
pages_to_check = [
    'dashboards/pages/3_News_Network.py',
    'dashboards/pages/4_Financial_Overview.py',
    'dashboards/pages/7_Command_Center.py',
]

for p in pages_to_check:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    name = p.split('/')[-1]
    # Find any st.warning or st.error that uses error_msg variable or "Cannot" string
    for i, line in enumerate(content.split('\n'), 1):
        s = line.strip()
        if ('st.warning' in s or 'st.error' in s) and 'error_msg' not in s and 'export' not in s.lower() and 'stock' not in s.lower() and 'barcode' not in s.lower():
            print(name + ':' + str(i) + ': ' + s[:150])
