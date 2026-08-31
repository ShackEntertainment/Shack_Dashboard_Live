"""
SHACK ENTERTAINMENT — shack_patch_finance2.py
Line-based splice: expenses branch now reads Data\expenses.csv live.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_finance_queries.py')
with open(p, encoding='utf-8') as f:
    lines = f.read().splitlines(True)

start = end = None
for i, l in enumerate(lines):
    if "elif 'expense' in q or 'spend' in q:" in l:
        start = i
    if start is not None and i > start and 'No expense data available yet.' in l:
        end = i
        break
assert start is not None and end is not None, 'branch not found'

NEW = '''        elif 'expense' in q or 'spend' in q:
            csv_path = os.path.join(project_root, 'Data', 'expenses.csv')
            rows = []
            if os.path.exists(csv_path):
                with open(csv_path, encoding='utf-8') as f:
                    csv_lines = [x.rstrip() for x in f if x.strip()]
                for x in csv_lines[1:][-3:]:
                    parts = x.split(',')
                    if len(parts) >= 5:
                        rows.append((parts[5] if len(parts) > 5 else 'other',
                                     parts[3], parts[4]))
            if rows:
                out = "💸 **Recent Expenses:**\\n\\n"
                for cat, desc, amt in rows:
                    out += f"• {cat}: {desc} — £{parse_currency(amt):,.2f}\\n\\n"
                return out
            return "No expense data available yet."
'''
lines[start:end + 1] = [NEW]
with open(p, 'w', encoding='utf-8') as f:
    f.write(''.join(lines))
print('patched v2: expenses read Data\\expenses.csv live')