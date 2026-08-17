import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('dashboards/Home.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'load_' in line or 'st.warning' in line or 'st.error' in line or 'error_msg' in line or 'Cannot' in line:
        print(str(i) + ': ' + line.rstrip()[:150])
