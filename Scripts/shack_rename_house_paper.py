"""
SHACK ENTERTAINMENT — shack_rename_house_paper.py
Renames Templates to lane-prefixed names and patches cross-references.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(os.path.dirname(script_dir), 'Legal', 'Templates')

RENAMES = [
    ('01_AU_Fine_Art_Agency_Agreement.md', 'AU_01_Fine_Art_Agency_Agreement.md'),
    ('02_LE_Springboard_Partnership_Agreement.md', 'LE_01_Springboard_Partnership_Agreement.md'),
    ('03_LE_Engagement_Order.md', 'LE_02_Engagement_Order.md'),
    ('04_LE_First_Contact_Letter.md', 'LE_03_First_Contact_Letter.md'),
    ('05_LE_Media_Release_Acknowledgement.md', 'LE_04_Media_Release_Acknowledgement.md'),
    ('06_B2B_Partnership_Venue_Agreement.md', 'B2B_01_Partnership_Venue_Agreement.md'),
    ('07_Sponsorship_Agreement.md', 'B2B_02_Sponsorship_Agreement.md'),
    ('08_Advertising_Marketing_Services_Agreement.md', 'B2B_03_Advertising_Marketing_Services_Agreement.md'),
    ('09_Charity_Community_Association.md', 'B2B_04_Charity_Community_Association.md'),
]

PATCHES = [
    ('# DOCUMENT 1 — ', '# AU_01 — '),
    ('# DOCUMENT 2 — ', '# LE_01 — '),
    ('# DOCUMENT 3 — ', '# LE_02 — '),
    ('# DOCUMENT 4 — ', '# LE_03 — '),
    ('# DOCUMENT 5 — ', '# LE_04 — '),
    ('# DOCUMENT 6 — ', '# B2B_01 — '),
    ('# DOCUMENT 7 — ', '# B2B_02 — '),
    ('# DOCUMENT 8 — ', '# B2B_03 — '),
    ('# DOCUMENT 9 — ', '# B2B_04 — '),
    ('Document 1', 'AU_01'),
    ('Document 2', 'LE_01'),
    ('Document 3', 'LE_02'),
    ('Document 4', 'LE_03'),
    ('Document 5', 'LE_04'),
]

for old, new in RENAMES:
    op = os.path.join(T, old)
    if not os.path.exists(op):
        print('missing:', old)
        continue
    with open(op, encoding='utf-8') as f:
        t = f.read()
    for a, b in PATCHES:
        t = t.replace(a, b)
    with open(os.path.join(T, new), 'w', encoding='utf-8') as f:
        f.write(t)
    os.remove(op)
    print('renamed:', old, '->', new)