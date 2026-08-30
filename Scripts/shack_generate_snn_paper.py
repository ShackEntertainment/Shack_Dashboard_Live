"""
SHACK ENTERTAINMENT — shack_generate_snn_paper.py
Banks the SNN Talent springboard paper and updates the Rate Card shell.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(os.path.dirname(script_dir), 'Legal', 'Templates')
os.makedirs(T, exist_ok=True)

snn1 = """# SNN_01 — SNN TALENT SPRINGBOARD AGREEMENT (ROSTER)

**THIS AGREEMENT** is made on [date]

**BETWEEN:** (1) **SHACK ENTERTAINMENT LIMITED**, company no. 14628241, of 25 Fielding Avenue, Twickenham, England, TW2 5LX, trading as Shack Daily News / SNN ("the Company"); and (2) **[TALENT NAME]**, of [address] ("the Talent").

**1. NATURE**
1.1 A development and contribution arrangement, not employment. The Talent remains freelance and may work for others outside scheduled assignments.

**2. TERM & GRADUATION**
2.1 Fixed term of one (1) year; no automatic renewal; no early termination without cause.
2.2 Graduation: if the Talent accepts a staff or exclusive role with a broadcaster or publisher, they may terminate on 60 days' written notice with accounts settled. No success fee is payable.
2.3 Either party may terminate immediately for material breach not cured within 14 days.

**3. THE ROTATION**
3.1 The Talent shall make themselves reasonably available for scheduled assignments: presenting, anchoring, long-form interviews, blog commissions and related promotional appearances.
3.2 Confirmed assignments are capped at eight (8) per calendar quarter unless more are agreed in writing.
3.3 No assignment is binding until an SNN_02 Engagement & Commission Order is signed.

**4. THE COMPANY'S OBLIGATIONS**
4.1 Schedule assignments; pay fees on time; provide production facilities; publish with byline or presenter credit; maintain the SNN Archive; promote the Talent's published work through SNN platforms.

**5. MONEY**
5.1 Fees per assignment at the Rate Card (presenter/anchor rates, commission fees). Payment within 7 days of recording or publication, as the Order specifies.
5.2 Any Company expense recharged to the Talent exceeding £50 requires the Talent's prior written consent.

**6. EDITORIAL STANDARDS**
6.1 The Talent shall comply with the SNN editorial code: accuracy, honesty, disclosure of conflicts of interest. The Talent warrants all contributions are original, non-defamatory and non-infringing.
6.2 The Company retains final editorial control and final cut over all material published under the SNN brand.

**7. INTELLECTUAL PROPERTY & THE ARCHIVE**
7.1 The Talent owns their pre-existing works and personal brand.
7.2 The Company owns all recordings, broadcasts and published pieces produced under assignments (the SNN Archive).
7.3 The Company grants the Talent a perpetual, royalty-free licence to use clips and copies of their assigned work for portfolio, showreel, CV and self-promotion.
7.4 The Talent shall receive byline or presenter credit in a form approved by the Company.

**8. CONDUCT & CANCELLATION**
8.1 Repeated unexcused failure to attend confirmed assignments is a material breach.
8.2 Cancellation by the Company within 48 hours of a confirmed assignment: the full fee is payable. Cancellation by the Talent within 48 hours without good reason: the fee for that assignment is forfeit.

**9. TERMINATION EFFECTS**
9.1 Accounts settle within 30 days. The showreel licence survives for materials already issued to the Talent.

**10. GENERAL**
10.1 Clauses 9.1-9.8 of AU_01 apply as if repeated here.

**SIGNED** for and on behalf of SHACK ENTERTAINMENT LIMITED by **BOLA KASSIM, Director** ………… Date …………
**SIGNED by the TALENT** ………… Date …………
"""

snn2 = """# SNN_02 — SNN ENGAGEMENT & COMMISSION ORDER

**Order ref:** [SNN-2026-XXX] — issued under SNN_01 (roster talent) or standalone (guests, speakers, crew).

| Field | Detail |
|---|---|
| Contributor name | |
| Role type (presenter / anchor / invited guest / speaker / journalist / camera / sound / specialist) | |
| Programme or piece | |
| Date(s) | |
| Fee type (appearance fee / commission fee / day rate) | |
| Fee amount | |
| Credit / byline (if any) | |
| Payment trigger (recording / publication / completion) — paid within 7 days thereof | |

**Terms confirmed by signing:**
1. The Company owns all output recorded or published under this Order; the contributor receives the personal-promotion licence of SNN_01 clause 7.3.
2. The contributor warrants their contribution is original, non-defamatory and non-infringing, that they hold the right to give it, and consents to recording and publication.
3. Editorial control and final cut rest with the Company.
4. The contributor is self-employed for this engagement and is responsible for their own tax and National Insurance on the fee.
5. Standalone signatories (guests, speakers, crew) confirm no employment or ongoing relationship arises from this Order.

**For the Company:** BOLA KASSIM, Director ………… **For the Contributor:** ………… Date …………
"""

rate = """# 00 — SHACK RATE CARD (SHELL — TO BE PRICED WITH THE RA)

**Principle (immutable):** Shack never charges an artist to play. No pay-to-play, no vanity slots, now or ever.
**Principle (immutable):** Shack pays its talent on time. Seven days, every time.

**Lanes to price:**
- Partnership Venue splits, by capacity band: [__ %]
- Sponsorship tiers (season / event / category exclusive): [£ __]
- Advertising & Marketing day rates and packages: [£ __]
- Extra revision rounds (B2B_03): [£ __]
- Charity discount schedule: [__ % off standard]
- SNN presenter / anchor day rates: [£ __]
- SNN longform interview commission fee: [£ __]
- SNN blog commission fee (per piece): [£ __]
- Invited guest / speaker appearance fees: [£ __]
- Crew day rates (camera / sound / specialist): [£ __]

Pricing authority: MD with the RA, once the platform is operational.
"""

for name, text in [('SNN_01_Talent_Springboard_Agreement.md', snn1),
                   ('SNN_02_Engagement_Commission_Order.md', snn2),
                   ('00_Rate_Card_Shell.md', rate)]:
    with open(os.path.join(T, name), 'w', encoding='utf-8') as f:
        f.write(text)
    print('Banked:', name)