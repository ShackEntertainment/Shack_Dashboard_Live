import re, os

# Check data_sync.py for the spreadsheet resolution logic
with open('data_sync.py', 'r', encoding='utf-8') as f:
    content = f.read()

print('=== data_sync.py - Spreadsheet Name Logic ===')
# Find all references to spreadsheet names
for line in content.split('\n'):
    if 'spreadsheet' in line.lower() or 'Shack_' in line:
        print(line.strip())

print('\n=== Page imports from data_sync ===')
pages_dir = 'dashboards/pages'
for fname in sorted(os.listdir(pages_dir)):
    if not fname.endswith('.py'):
        continue
    fpath = os.path.join(pages_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Check what function they call from data_sync
    funcs = re.findall(r'(?:from|import)\s+data_sync.*?(\w+)', content, re.DOTALL)
    calls = re.findall(r'(\w+)\s*\(', content)
    ds_calls = [c for c in calls if any(x in c for x in ['load_', 'get_', 'fetch', 'sync'])]
    # Also look for load_live_exchange or similar
    specific = re.findall(r'(data_sync\.\w+|from\s+data_sync\s+import\s+.*)', content)
    if specific:
        print(fname + ': ' + str(specific))
