import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

targets = [
    'dashboards/pages/3_News_Network.py',
    'dashboards/pages/4_Financial_Overview.py',
    'dashboards/pages/7_Command_Center.py',
]

for p in targets:
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    name = p.split('/')[-1]
    print('=== ' + name + ' ===')
    
    # Find all imports from data_sync
    imports = re.findall(r'(?:from|import).*?data_sync.*', content)
    if imports:
        print('IMPORTS: ' + str(imports))
    
    # Find function calls
    calls = re.findall(r'(\w+)\s*=\s*(?:load_\w+|get_\w+|fetch_\w+|sync_\w+)\s*\(', content)
    if calls:
        print('CALLS: ' + str(calls))
    
    # Find where error_msg is used
    for i, line in enumerate(content.split('\n'), 1):
        s = line.strip()
        if 'error_msg' in s or 'Cannot find' in s or 'Cannot access' in s:
            print(str(i) + ': ' + s[:150])
    
    # Check if they call a DIFFERENT loader than load_live_exchange_data
    all_funcs = re.findall(r'(\w[\w_]*\s*\([^)]*\))', content)
    ds_funcs = [f for f in all_funcs if any(x in f for x in ['load_', 'get_', 'fetch_', 'sync_'])]
    if ds_funcs:
        print('ALL DS FUNCS: ' + str(ds_funcs[:10]))
    print()
