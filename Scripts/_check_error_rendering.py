import re, sys
sys.stdout.reconfigure(encoding='utf-8')

targets = [
    ('dashboards/pages/3_News_Network.py', 'load_news_data'),
    ('dashboards/pages/4_Financial_Overview.py', 'load_finance_data'),
    ('dashboards/pages/7_Command_Center.py', 'load_command_data'),
]

for p, loader in targets:
    with open(p, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    name = p.split('/')[-1]
    print('=== ' + name + ' ===')
    
    # Find lines around the load call and error handling
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if loader in s or (i > 1 and loader in lines[i-2] if i >= 2 else False):
            # Print context: 5 lines before to 5 after
            start = max(0, i-3)
            end = min(len(lines), i+5)
            for j in range(start, end):
                marker = '>>>' if j == i-1 else '   '
                print(marker + str(j+1) + ': ' + lines[j].rstrip())
            print('---')
    print()
