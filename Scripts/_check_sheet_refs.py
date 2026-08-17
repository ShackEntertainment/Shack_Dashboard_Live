import re, os

pages_dir = 'dashboards/pages'
for fname in sorted(os.listdir(pages_dir)):
    if not fname.endswith('.py'):
        continue
    fpath = os.path.join(pages_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    pat = r'(?:spreadsheet_name|gc\.open)\s*[\(=]\s*["\']([\w\s_]+)'
    matches = re.findall(pat, content)
    if matches:
        unique = list(set(matches))
        print(fname + ': ' + str(unique))
    else:
        print(fname + ': NO SPREADSHEET REFERENCE FOUND')

print('\n--- Home.py ---')
with open('dashboards/Home.py', 'r', encoding='utf-8') as f:
    content = f.read()
matches = re.findall(pat, content)
if matches:
    unique = list(set(matches))
    print(str(unique))
else:
    print('NO SPREADSHEET REFERENCE')
