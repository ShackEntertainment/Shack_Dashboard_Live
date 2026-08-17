import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Search ALL python files for st.warning or st.error that could show the scope message
search_root = 'dashboards'
for root, dirs, files in os.walk(search_root):
    for fname in files:
        if not fname.endswith('.py'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        rel = os.path.relpath(fpath, search_root)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if ('st.warning' in stripped or 'st.error' in stripped) and 'export' not in stripped.lower() and 'stock' not in stripped.lower():
                print(rel + ':' + str(i) + ': ' + stripped[:150])

# Also check data_sync.py
print('\n--- data_sync.py ---')
with open('data_sync.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if 'st.warning' in stripped or 'st.error' in stripped:
        print(str(i) + ': ' + stripped[:150])
