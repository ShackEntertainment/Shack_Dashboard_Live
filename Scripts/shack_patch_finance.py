"""
SHACK ENTERTAINMENT — shack_patch_finance.py
Rewires the brief's expenses branch from the stale SQLite table
to Data\expenses.csv (live, clerk-fed).
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(script_dir, 'shack_finance_queries.py')
with open(p, encoding='utf-8') as f:
    t = f.read()

OLD = r"""        elif 'expense' in q or 'spend' in q:
            cursor.execute("SELECT category, description, amount FROM finance_expenses LIMIT 10")
            rows = cursor.fetchall()
            if rows:
                out = "💸 **Recent Expenses:**\n\n"
                for r in rows:
                    out += f"• {r[0]}: {r[1]} — £{parse_currency(r[2]):,.2f}\n\n"
                return out
            return "No expense data available yet.\""""

NEW = r"""        elif 'expense' in q or 'spend' in q:
            csv_path = os.path.join(project_root, 'Data', 'expenses.csv')
            rows = []
            if os.path.exists(csv_path):
                with open(csv_path, encoding='utf-8') as f:
                    lines = [l.rstrip() for l in f if l.strip()]
                for l in lines[1:][-3:]:
                    parts = l.split(',')
                    if len(parts) >= 5:
                        rows.append((parts[5] if len(parts) > 5 else 'other',
                                     parts[3], parts[4]))
            if rows:
                out = "💸 **Recent Expenses:**\n\n"
                for cat, desc, amt in rows:
                    out += f"• {cat}: {desc} — £{parse_currency(amt):,.2f}\n\n"
                return out
            return "No expense data available yet.\""""

assert OLD in t, 'anchor not found'
t = t.replace(OLD, NEW)
with open(p, 'w', encoding='utf-8') as f:
    f.write(t)
print('patched: expenses now read Data\\expenses.csv live')