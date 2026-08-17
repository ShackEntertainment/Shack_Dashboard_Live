with open('dashboards/pages/1_Artists_Unlimited.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'warning' in line.lower() or 'Cannot access' in line or 'st.error' in line.lower():
        print(str(i) + ': ' + line.rstrip())
