"""
SHACK ENTERTAINMENT — shack_generate_house_paper.py
[LEGAL] Creates the Legal architecture and drops the three house papers
into the Templates folder.
"""
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

templates_dir = os.path.join(project_root, 'Legal', 'Templates')
executed_dir = os.path.join(project_root, 'Legal', 'Executed')
archive_dir = os.path.join(project_root, 'Legal', 'Archive')

for d in [templates_dir, executed_dir, archive_dir]:
    os.makedirs(d, exist_ok=True)

doc1 = """# DOCUMENT 1 — ARTISTS UNLIMITED FINE ART AGENCY AGREEMENT

**THIS AGREEMENT** is made on [date]

**BETWEEN:**
(1) **SHACK ENTERTAINMENT LIMITED**, company no. 14628241, of 25 Fielding Avenue, Twickenham, England, TW2 5LX ("the Company"); and
(2) **[ARTIST NAME]**, of [address] ("the Artist").

**1. APPOINTMENT**
1.1 The Artist appoints the Company as its agent to place, exhibit, market and sell the Artist's works through the Company's stores, partner outlets, exhibitions and online channels ("the Channels").
1.2 The appointment is **non-exclusive**. Nothing prevents the Artist from selling, consigning or licensing works directly or through third parties, and no commission is payable on any sale not secured by the Company.

**2. TERM**
2.1 This Agreement runs for **three (3) years** from the date above and expires automatically on its third anniversary. There is **no automatic renewal or extension** of any kind.
2.2 Renewal requires a further written agreement signed by both parties.
2.3 Either party may terminate on **three (3) months'** written notice, or immediately for material breach not cured within **14 days** of written notice.

**3. COMMISSION**
3.1 The Company is entitled to **30%** of the gross sale price of each work sold through the Channels ("Commission"). No other fee is payable.
3.2 After termination, Commission on works consigned during the Term and sold post-termination reduces to **15% (year 1), 10% (year 2), 5% (year 3)** and then ceases.

**4. MONEY & TRUST**
4.1 All sale proceeds received by the Company are held **in trust for the Artist** in the Company's designated client account (currently held at Santander plc) until disbursed.
4.2 The Company shall issue a written statement within **7 days** of each month-end and pay the Artist's share no later than **30 days after each sale**, regardless of any instalment or layaway arrangement with the buyer; the buyer's credit risk is the Company's alone.
4.3 Layaway or instalment sales exceeding **6 months** require the Artist's prior written consent.
4.4 Company expenses exceeding **£50 per month** relating to the Artist require the Artist's prior written consent.

**5. CONSIGNMENT & TITLE**
5.1 The Artist retains **title and copyright** in every work until it is sold and paid for in full.
5.2 Consigned works are held **in trust**, are not the Company's property, and are **not subject to the Company's creditors**.
5.3 The Company is **liable for loss, theft or damage** to consigned works while in its possession or control and shall insure them accordingly.
5.4 Each work is logged in a consignment schedule (SKU, title, retail price) mirroring the Company's inventory records; a schedule entry is conclusive as to the work's retail price.
5.5 Retail prices and any discount above 10% require the Artist's written approval.
5.6 The Company may place works at partner outlets and exhibitions on the same trust terms and remains liable for them.
5.7 The Company shall notify buyers that the Artist retains all reproduction rights.

**6. SHIPPING**
6.1 The Artist bears the cost of delivering works to the Company. The Company bears **return shipping and insurance** for unsold or withdrawn works.

**7. INTELLECTUAL PROPERTY**
7.1 The Artist owns all intellectual property in the works absolutely. The Company holds a limited licence to photograph and reproduce the works for promotion during the Term only.

**8. TERMINATION EFFECTS**
8.1 Within **30 days** of termination the Company shall return all unsold works and issue a final statement and payment.

**9. GENERAL**
9.1 The parties are independent contractors; nothing creates a partnership, employment or agency of law. The Company holds **no power of attorney** over the Artist's affairs.
9.2 Each party keeps the other's confidential information confidential.
9.3 Notices are in writing and deemed given on delivery or verified email.
9.4 No variation is effective unless in writing and signed.
9.5 If any provision is unenforceable it is severed; the remainder stands.
9.6 The Contracts (Rights of Third Parties) Act 1999 is excluded.
9.7 Disputes go first to good-faith mediation; failing settlement within 30 days, to the exclusive jurisdiction of the courts of England and Wales. This Agreement is governed by English law.
9.8 The Artist confirms having had the opportunity to take independent legal advice.

**SIGNED** for and on behalf of SHACK ENTERTAINMENT LIMITED by **BOLA KASSIM, Director** ………… Date …………
**SIGNED by the ARTIST** ………… Date …………
"""

doc2 = """# DOCUMENT 2 — THE LIVE EXCHANGE SPRINGBOARD PARTNERSHIP AGREEMENT

**THIS AGREEMENT** is made on [date]

**BETWEEN:** (1) **SHACK ENTERTAINMENT LIMITED** (as above) ("the Company"); and (2) **[ARTIST NAME]**, of [address] ("the Artist").

**1. NATURE OF THE RELATIONSHIP**
1.1 This is a **partnership and development arrangement, not a management contract**. The Artist remains **self-managed** and free to negotiate and perform engagements outside the Shack calendar; the Company takes **no commission or share** of any income earned outside this Agreement.
1.2 The Company's purpose is to act as a springboard: booking, producing and promoting the Artist at partnership venues and through Shack media.

**2. TERM**
2.1 This Agreement runs for **one (1) year** ("the Rotation Year") and expires automatically. No renewal except by signed written agreement.
2.2 **Graduation:** if during the Rotation Year the Artist signs a recording, publishing or representation agreement with a label or agency, the Artist may terminate on **60 days'** written notice with all accounts settled.
2.3 Either party may terminate immediately for material breach not cured within **14 days** of written notice.

**3. THE ROTATION**
3.1 The Artist shall make themselves reasonably available for the Shack calendar rotation of acts at partnership venues, studio recording sessions for Shack media, and related marketing and promotion appearances.
3.2 Rotation slots are capped at **six (6) confirmed engagements per calendar quarter** unless more are agreed in writing.
3.3 No slot is binding until an **Engagement Order** (Document 3) is signed by both parties.

**4. THE COMPANY'S OBLIGATIONS**
4.1 Book the rotation at partnership venues; produce each engagement to professional standard; promote the Artist through Shack media platforms; and account transparently as set out below.

**5. MONEY**
5.1 Default split: **70% of gross ticket revenue to the Artist, 30% to the Company** per engagement, unless the Engagement Order specifies a fixed fee, door deal or revenue share.
5.2 All Artist monies are held **in trust** in the Company's client account (Santander plc). A written statement issues within **7 days** of each month-end and payment follows with the statement.
5.3 Company expenses exceeding **£50 per month** relating to the Artist require the Artist's prior written consent.

**6. PRODUCTION STANDARDS** (per Engagement Order)
6.1 The Company provides: venue; backline per Schedule 2; sound, lighting, staff and power; a suitable dressing room; catering per the rider; **SIA-accredited security**; and **public liability insurance** for the event.

**7. THE ARTIST'S OBLIGATIONS**
7.1 Perform a professional set of **90–120 minutes** (unless the Order states otherwise); provide promotional materials (biography, photographs, set details); warrant that all performed material is non-infringing; and comply with venue health and safety regulations.

**8. CANCELLATION**
8.1 Cancellation by the Company: **15+ days** before the engagement, 50% of the scheduled fee or split guarantee; **7 days or less**, 100%.
8.2 Cancellation by the Artist for illness or force majeure: reschedule in good faith, no liability. Other cancellation by the Artist within 7 days: forfeiture of fee only.

**9. INTELLECTUAL PROPERTY & MEDIA**
9.1 The Artist owns their works absolutely. The Artist grants the Company a non-exclusive licence, during and after the Term, to use recordings and photographs made **at Shack events** for Shack media promotion.

**10. TERMINATION EFFECTS**
10.1 All accounts settle within **30 days** of termination. The media licence survives for material already published.

**11. GENERAL**
11.1 Clauses 9.1–9.8 of Document 1 apply as if repeated here.

**SIGNED** for and on behalf of SHACK ENTERTAINMENT LIMITED by **BOLA KASSIM, Director** ………… Date …………
**SIGNED by the ARTIST** ………… Date …………
"""

doc3 = """# DOCUMENT 3 — LIVE EXCHANGE ENGAGEMENT ORDER

**Order ref:** [EVT-2026-XXX] — issued under the Springboard Partnership Agreement dated [date] between Shack Entertainment Limited and [Artist].

| Field | Detail |
|---|---|
| Event name | |
| Venue, address, capacity | |
| Date; doors; set time | |
| Fee type (split / fixed / door / revenue share) | |
| Fee / split amount | |
| Backline (Schedule 2 summary) | |
| Rider (catering/hospitality) | |
| Travel & accommodation | Company-provided as scheduled / Artist's own |
| Accompanying musicians & crew | |

By signing, both parties confirm the engagement on the terms of the Springboard Agreement, including the cancellation ladder (8.1/8.2) and production standards (6.1).

**For the Company:** BOLA KASSIM, Director ………… **For the Artist:** ………… Date …………
"""

docs = [
    ('01_AU_Fine_Art_Agency_Agreement.md', doc1),
    ('02_LE_Springboard_Partnership_Agreement.md', doc2),
    ('03_LE_Engagement_Order.md', doc3)
]

for name, text in docs:
    path = os.path.join(templates_dir, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'Banked: Legal\\Templates\\{name}')

print('\nArchitecture ready:')
print(' - Legal\\Templates\\ (House paper)')
print(' - Legal\\Executed\\ (Signed copies)')
print(' - Legal\\Archive\\  (Old templates)')