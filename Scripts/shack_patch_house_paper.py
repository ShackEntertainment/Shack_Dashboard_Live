"""
SHACK ENTERTAINMENT — shack_patch_house_paper.py
Applies the audit's final directions to Legal\Templates and the
roster clerk prefixes. Reports hit-counts per file.
"""
import os, glob
script_dir = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(script_dir)
T = os.path.join(ROOT, 'Legal', 'Templates')

def patch(fn, pairs):
    p = os.path.join(T, fn)
    with open(p, encoding='utf-8') as f:
        t = f.read()
    hits = 0
    for a, b in pairs:
        hits += t.count(a)
        t = t.replace(a, b)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(t)
    print('%-45s %d hit(s)' % (fn, hits))

patch('AU_01_Fine_Art_Agency_Agreement.md', [
    ("9.8 The Artist confirms having had the opportunity to take independent legal advice.",
     "9.8 The Artist confirms having had the opportunity to take independent legal advice.\n9.9 Neither party is liable for failure or delay in performance (other than payment obligations) caused by events beyond its reasonable control, including fire, flood, strike, industrial action, war, government action or utility failure; the affected party shall give prompt notice and its obligation is suspended while the event continues; if the event continues beyond 60 days either party may terminate on written notice with accounts settled."),
    ("and no commission is payable on any sale not secured by the Company.",
     "and no commission is payable on any sale not secured by the Company.\n1.3 Gallery placements, exhibitions and art-related shows are programmed under the Artists Unlimited banner."),
])

patch('LE_01_Springboard_Partnership_Agreement.md', [
    ("through Shack media.",
     "through Shack media.\n1.3 The Company's live lane is limited to live and music performance; visual-art programming sits with Artists Unlimited."),
])

patch('LE_03_First_Contact_Letter.md', [("[ART-xxx]", "[LE-xxx]")])

patch('LE_04_Media_Release_Acknowledgement.md', [
    ("- [ ] I am a disciplined professional and will adhere to the roster's scheduling and production standards.",
     "- [ ] I am a disciplined professional and will adhere to the roster's scheduling and production standards.\n- [ ] Renewal, exit and termination terms are governed by LE_01; this release is the media-consent schedule to it."),
])

patch('B2B_01_Partnership_Venue_Agreement.md', [
    ("Artist merchandise revenue is the Artist's; neither party takes a cut.",
     "Artist merchandise revenue is the Artist's; neither party takes a cut; merchandise is sold, tracked and settled by the Artist directly and forms no part of the Event Order's accounts."),
    ("Breach of licensing or safeguarding law is a material breach.",
     "Breach of licensing or safeguarding law is a material breach and entitles the Company to terminate immediately and recover its reasonable committed costs."),
])

patch('B2B_02_Sponsorship_Agreement.md', [
    ("cancellation by the Company refunds the unearned fee and no more.",
     "cancellation by the Company refunds the unearned fee and no more. Material breach includes non-payment of any fee, breach of clause 6 (values) or use of an artist's name or likeness without the consent required by clause 4."),
])

patch('B2B_04_Charity_Community_Association.md', [
    ("Each activity is confirmed by a simple written order.",
     "Each activity is confirmed by a simple written order. A written order is a confirmation of an activity (email suffices) stating its date, scope and approved brand use."),
])

patch('SNN_01_Talent_Springboard_Agreement.md', [
    ("trading as Shack Daily News / SNN",
     "trading as Shack News Network (SNN), publisher of Shack Daily News"),
    ('("the Talent").',
     '("the Talent"), SNN ID [SNN-xxx].'),
])

patch('SNN_02_Engagement_Commission_Order.md', [
    ("| Contributor name | |",
     "| Contributor name | |\n| Contributor ID (SNN-xxx) | |"),
])

# The 9.9 ripple: every incorporating paper now cites the full general block.
for p in glob.glob(os.path.join(T, '*.md')):
    with open(p, encoding='utf-8') as f:
        t = f.read()
    if '9.1-9.8' in t:
        t = t.replace('9.1-9.8', '9.1-9.9')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(t)
        print('ripple:', os.path.basename(p))

# Roster clerk prefixes: departments wear their own badges.
cp = os.path.join(ROOT, 'Scripts', 'shack_roster_clerk.py')
with open(cp, encoding='utf-8') as f:
    t = f.read()
t = t.replace("'au': '', 'le_art': 'ART-'", "'au': 'ART-', 'le_art': 'LE-'")
with open(cp, 'w', encoding='utf-8') as f:
    f.write(t)
print('clerk prefixes patched: au=ART-, le_art=LE-')
print('PATCH PASS COMPLETE')