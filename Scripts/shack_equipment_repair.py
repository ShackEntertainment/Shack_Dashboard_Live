"""
SHACK ENTERTAINMENT — shack_equipment_repair.py
One-off repair: re-splits blob rows in Data\equipment.csv into the
ten proper columns. Backs up to equipment_backup.csv first.
"""
import os
import re
import shutil

script_dir = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(script_dir), 'Data')
CSV = os.path.join(DATA, 'equipment.csv')
BAK = os.path.join(DATA, 'equipment_backup.csv')

CATS = r'camera|lens|lighting|audio|broadcast|computer|rigging|other'
BLOB = re.compile(
    r'^(.*)\b(' + CATS + r')\b\s*(?:status\s+)?active\s+studio\s+'
    r'(\d{4}-\d{2}-\d{2})\s+([\d.]+)\s*(.*)$', re.I)

def fix(blob):
    b = blob.strip()
    if len(b) < 8 or b.lower() in ('item', 'mouse', 'cable'):
        return [b, '', '', '', '', '', '', '',
                'REVIEW - junk row, re-enter by hand']
    m = BLOB.match(b)
    if not m:
        return [b, '', '', '', '', '', '', '',
                'REVIEW - could not split, check by hand']
    item, cat, date, price, rest = m.groups()
    rest = rest.strip()
    serial = ''
    notes = ''
    if 'no serial' in rest.lower():
        notes = 'no serial'
        rest = re.sub(r'no serial', '', rest, flags=re.I).strip()
    if len(rest) > 60:
        seller = rest[:60].strip()
        notes = (notes + ' ' + rest[60:].strip()).strip()
    else:
        seller = rest
    return [item.strip(), cat.lower(), serial, 'active', 'studio',
            date, price, seller, notes]

def main():
    shutil.copy(CSV, BAK)
    with open(CSV, encoding='utf-8') as f:
        rows = [l.rstrip('\n') for l in f if l.strip()]
    out = [rows[0]]
    kept = fixed = junk = 0
    for r in rows[1:]:
        parts = r.split(',')
        if len(parts) == 10:
            out.append(r); kept += 1; continue
        if len(parts) > 10:
            parts = parts[:9] + [','.join(parts[9:])]
            out.append(','.join(parts)); kept += 1; continue
        eid = parts[0]
        blob = ','.join(parts[1:])
        f9 = fix(blob)
        junk += 1 if f9[8].startswith('REVIEW') else 0
        fixed += 1 if not f9[8].startswith('REVIEW') else 0
        out.append(eid + ',' + ','.join(f9))
    with open(CSV, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print('kept %d, fixed %d, review %d' % (kept, fixed, junk))

if __name__ == '__main__':
    main()