import re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data_sync.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all function definitions
funcs = re.findall(r'def (\w+)\s*\([^)]*\)\s*:', content)
print('All functions in data_sync.py:')
for fn in funcs:
    print('  ' + fn)

# Find load_news_data, load_finance_data, load_command_data
for target in ['load_news_data', 'load_finance_data', 'load_command_data']:
    idx = content.find('def ' + target)
    if idx >= 0:
        # Get 80 lines from this function
        snippet = content[idx:idx+3000]
        lines = snippet.split('\n')[:60]
        print('\n=== ' + target + ' ===')
        for line in lines:
            print(line.rstrip())
