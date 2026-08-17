import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Search EVERY .py file in the project for st.warning or st.error with "Cannot find" or "Cannot access"
search_root = 'C:/Users/Bola/Documents/Shack_Project'
for root, dirs, files in os.walk(search_root):
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.streamlit', 'node_modules', '.git']]
    for f in files:
        if not f.endswith('.py'): continue
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, search_root)
        with open(fp, 'r', encoding='utf-8') as fh:
            lines = fh.readlines()
        for i, line in enumerate(lines, 1):
            s = line.strip()
            if ('st.warning' in s or 'st.error' in s):
                if any(x in s for x in ['Cannot find', 'Cannot access', 'invalid_scope', 'spreadsheet']):
                    print(rel + ':' + str(i) + ': ' + s[:180])
