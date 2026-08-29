"""
SHACK ENTERTAINMENT — shack_generate_b2b_paper.py
Banks the B2B commercial paper: Partnership Venue, Sponsorship,
Advertising & Marketing, Charity & Community, and the Rate Card shell.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(os.path.dirname(script_dir), 'Legal', 'Templates')
os.makedirs(T, exist_ok=True)

doc6 = """# DOCUMENT 6 — PARTNERSHIP VENUE AGREEMENT (B2B)

**BETWEEN:** (1) SHACK ENTERTAINMENT LIMITED ("the Company"); and (2) [VENUE NAME], of [address] ("the Venue").

**1. NETWORK** — The Venue joins the Company's partnership venue network. Non-exclusive on both sides.
**2. TERM** — Twelve (12) months; renewal by agreement; either party on 30 days' notice.
**3. EVENTS** — Each event is confirmed by a one-page Event Order (date, capacity, ticket price, revenue split).
**4. VENUE OBLIGATIONS** — Premises; FOH and bar staff; premises licence and alcohol licensing; venue health, safety and capacity compliance; dressing room access; reasonable power.
**5. COMPANY OBLIGATIONS** — Acts; production to the house standard; promotion through Shack media; ticketing operations unless the Order states otherwise.
**6. MONEY** — Net ticket revenue split per the Event Order (default per the Rate Card). Bar and catering revenue is the Venue's. **Artist merchandise revenue is the Artist's; neither party takes a cut.** Settlement: statement within 7 days of the event, payment with the statement.
**7. INSURANCE** — The Venue holds public liability for the premises; the Company holds public liability for production; each owns and insures its own equipment.
**8. BRANDING & MEDIA** — The Venue may use the Shack name and logo per brand guidelines. The Company owns the archive.
**9. CONDUCT** — Breach of licensing or safeguarding law is a material breach.
**10. GENERAL** — Clauses 9.1-9.8 of Document 1 apply as if repeated here.

**SIGNED** for the Company: BOLA KASSIM, Director ………… **for the Venue:** ………… Date …………
"""

doc7 = """# DOCUMENT 7 — SPONSORSHIP AGREEMENT

**BETWEEN:** (1) SHACK ENTERTAINMENT LIMITED ("the Company"); and (2) [SPONSOR NAME], of [address] ("the Sponsor").

**1. GRANT** — Sponsorship of [season/event] per the Schedule. Category exclusivity only where the Schedule grants it.
**2. BENEFITS** — As scheduled: logo placement, mentions, hospitality allocations, co-branded content.
**3. FEE** — [£ amount]; 50% on signing, 50% no later than 30 days before the sponsored event. No benefits activate until funds clear.
**4. MEDIA & ARCHIVE** — The Company owns all archive and media. The Sponsor receives a non-exclusive licence over approved co-branded content during the Term; approvals within 5 business days. **No use of any artist's name or likeness without that artist's separate written consent.**
**5. HONESTY** — Audience and reach figures quoted are good-faith estimates; no warranty of exposure is given.
**6. VALUES** — The Company may decline or remove sponsor categories inconsistent with its values (including exploitative lending or marketing targeting minors), with a pro-rata refund of the unearned fee.
**7. TERM & TERMINATION** — Per the Schedule; material breach curable within 14 days; cancellation by the Company refunds the unearned fee and no more.
**8. GENERAL** — Clauses 9.1-9.8 of Document 1 apply as if repeated here.

**SIGNED** for the Company: BOLA KASSIM, Director ………… **for the Sponsor:** ………… Date …………
"""

doc8 = """# DOCUMENT 8 — ADVERTISING & MARKETING SERVICES AGREEMENT

**BETWEEN:** (1) SHACK ENTERTAINMENT LIMITED ("the Company"); and (2) [CLIENT NAME], of [address] ("the Client").

**1. SERVICES** — Per the written brief and Schedule. Two revision rounds included; further rounds billed per the Rate Card.
**2. FEES** — Per Schedule / Rate Card; 50% upfront; balance on delivery.
**3. CLIENT MATERIALS** — The Client warrants it holds all rights in materials supplied. Client delays extend deadlines day for day.
**4. INTELLECTUAL PROPERTY** — Produced creative is owned by the Company until paid in full, then assigned to the Client. The Company retains a perpetual right to display the work in its portfolio and retains campaign production assets in its archive. The Client's materials remain the Client's.
**5. NO GUARANTEES** — Reach and conversion figures are good-faith estimates; no performance warranty is given.
**6. TERMINATION** — Either party on written notice; the Client pays for all work completed to the notice date.
**7. GENERAL** — Clauses 9.1-9.8 of Document 1 apply as if repeated here.

**SIGNED** for the Company: BOLA KASSIM, Director ………… **for the Client:** ………… Date …………
"""

doc9 = """# DOCUMENT 9 — CHARITY & COMMUNITY ASSOCIATION

**BETWEEN:** (1) SHACK ENTERTAINMENT LIMITED ("the Company"); and (2) [CHARITY NAME], registered charity no. [number] ("the Charity").

**1. NATURE** — A framework for community collaboration, not a revenue contract. Each activity is confirmed by a simple written order.
**2. SHACK OFFERS** — Discounted or pro-bono performance slots; promotional support; approved archive content for the Charity's campaigns.
**3. CHARITY OFFERS** — Community outreach; co-promotion; consent to use of its name and logo per approved campaign only.
**4. VALUES & SAFEGUARDING** — Both parties comply with applicable safeguarding law. The Charity warrants its registered status where claimed.
**5. NO EXCLUSIVITY** — Neither party is bound beyond confirmed orders; no financial obligation arises from this framework.
**6. EXIT** — Either party on 30 days' notice; all brand and logo use ceases immediately on exit.
**7. STATUS** — Nothing creates a partnership, joint venture or employment.

**SIGNED** for the Company: BOLA KASSIM, Director ………… **for the Charity:** ………… Date …………
"""

doc0 = """# 00 — SHACK RATE CARD (SHELL — TO BE PRICED WITH THE RA)

**Principle (immutable):** Shack never charges an artist to play. No pay-to-play, no vanity slots, now or ever.

**Lanes to price:**
- Partnership Venue splits, by capacity band: [__/% ]
- Sponsorship tiers (season / event / category exclusive): [£ __ ]
- Advertising & Marketing day rates and packages: [£ __ ]
- Extra revision rounds (Doc 8): [£ __ ]
- Charity discount schedule: [__ % off standard]

Pricing authority: MD with the RA, once the platform is operational.
"""

for name, text in [('06_B2B_Partnership_Venue_Agreement.md', doc6),
                   ('07_Sponsorship_Agreement.md', doc7),
                   ('08_Advertising_Marketing_Services_Agreement.md', doc8),
                   ('09_Charity_Community_Association.md', doc9),
                   ('00_Rate_Card_Shell.md', doc0)]:
    with open(os.path.join(T, name), 'w', encoding='utf-8') as f:
        f.write(text)
    print('Banked:', name)