"""
SHACK ENTERTAINMENT — shack_update_house_paper.py
Rewrites Doc 2 as the Springboard Investment model; banks the
First Contact Letter and Media Release as Docs 4-5.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(os.path.dirname(script_dir), 'Legal', 'Templates')
os.makedirs(T, exist_ok=True)

doc2 = """# DOCUMENT 2 — THE LIVE EXCHANGE SPRINGBOARD PARTNERSHIP AGREEMENT

**THIS AGREEMENT** is made on [date]

**BETWEEN:** (1) **SHACK ENTERTAINMENT LIMITED**, company no. 14628241, of 25 Fielding Avenue, Twickenham, England, TW2 5LX ("the Company"); and (2) **[ARTIST NAME]**, of [address] ("the Artist").

**1. NATURE OF THE RELATIONSHIP**
1.1 This is a partnership and development arrangement, not a management contract. The Artist remains self-managed and free to work outside the Shack calendar; the Company takes no share of income earned outside this Agreement.
1.2 The Company's purpose is a springboard: booking, producing and promoting the Artist at partnership venues and through Shack media.

**2. TERM & GRADUATION**
2.1 This Agreement runs for a fixed term of one (1) year ("the Rotation Year"). There is no automatic renewal and no right to terminate early without cause.
2.2 Graduation: if during the Rotation Year the Artist signs a recording, publishing or representation agreement with a major label or established agency, the Artist may terminate on 60 days' written notice and shall pay a Success Fee of 15% of any advance or guaranteed minimum earnings received from the new deal, within 30 days of receipt.
2.3 Either party may terminate immediately for material breach not cured within 14 days of written notice. Repeated unexcused failure to attend confirmed engagements is a material breach.

**3. THE ROTATION**
3.1 The Artist shall make themselves reasonably available for the Shack calendar rotation at partnership venues, studio sessions for Shack media, and related promotional appearances.
3.2 Confirmed engagements are capped at six (6) per calendar quarter unless more are agreed in writing.
3.3 No slot is binding until an Engagement Order (Document 3) is signed.

**4. THE COMPANY'S OBLIGATIONS**
4.1 Book the rotation; produce each engagement to professional standard; promote the Artist through Shack media; account transparently as below.

**5. MONEY**
5.1 Default split: 70% of gross ticket revenue to the Artist, 30% to the Company, unless an Engagement Order specifies a fixed fee, door deal or revenue share.
5.2 All Artist monies are held in trust in the Company's client account (Santander plc). A written statement issues within 7 days of each month-end; payment follows with the statement.
5.3 Company expenses over £50 per month relating to the Artist require the Artist's prior written consent.

**6. PRODUCTION STANDARDS**
6.1 The Company provides: venue; backline per Schedule 2; sound, lighting, staff and power; a suitable dressing room; catering per rider; SIA-accredited security; public liability insurance for the event.

**7. THE ARTIST'S OBLIGATIONS**
7.1 Perform a professional 90-120 minute set; provide promotional materials; warrant all performed material is non-infringing; comply with venue health and safety rules; and conduct themselves with the professionalism and reliability the rotation requires.

**8. CANCELLATION**
8.1 By the Company: 15+ days before the engagement, 50% of the scheduled fee or split guarantee; 7 days or less, 100%.
8.2 By the Artist for illness or force majeure: reschedule in good faith, no liability.
8.3 Other cancellation by the Artist within 14 days of a confirmed engagement: forfeiture of the fee and reimbursement of the Company's reasonable committed production costs.

**9. INTELLECTUAL PROPERTY & THE ARCHIVE**
9.1 Underlying Rights: the Artist retains 100% ownership of their Underlying Works (songs, scripts, compositions, art).
9.2 Shack Productions: the Company is the sole and exclusive owner of all rights in all audio-visual recordings, masters, photographs and promotional materials produced, funded or captured by or on behalf of the Company during the Term.
9.3 By signing, the Artist grants the Company the irrevocable right to capture, record and exploit Shack Productions. The Company grants the Artist a perpetual, non-exclusive, royalty-free licence to use Shack Productions solely for self-promotion.

**10. TERMINATION EFFECTS**
10.1 All accounts settle within 30 days. The Artist's self-promotion licence survives for materials already issued to them.

**11. GENERAL**
11.1 Clauses 9.1-9.8 of Document 1 apply as if repeated here.

**SIGNED** for and on behalf of SHACK ENTERTAINMENT LIMITED by **BOLA KASSIM, Director** ………… Date …………
**SIGNED by the ARTIST** ………… Date …………
"""

doc4 = """# DOCUMENT 4 — LIVE EXCHANGE FIRST CONTACT LETTER

**Subject: Invitation to The Live Exchange — Professional Springboard Roster (Ref: [ART-xxx])**

Hi [Name],

We have reviewed your work and would like to invite you to join **The Live Exchange** roster.

The Live Exchange is not a hobbyist collective; it is a professional production house. We invest significant capital — venue costs, professional sound and lighting, SIA security, and marketing — into a select group of disciplined fringe artists who have outgrown the DIY circuit but are not ready (or willing) to sign away their rights to a major label.

**The Commitment:** We operate on a fixed one-year Rotation. We do not offer try-outs or month-to-month slots. We invest in artists who are organized, reliable and committed to the schedule. In return, we provide infrastructure independent artists rarely access.

**The Deal:**
- You own your work: your songs, your art, your IP. Always.
- We own the production: Shack Entertainment owns the masters, video recordings and archive of the performances we fund and produce. You may use them freely for your promo; we retain the archive.
- The Split: 70% of Shack-calendar revenue to you, 30% to Shack to cover production and platform costs.
- The Exit: you are self-managed outside our calendar. If you land a major label or agency deal during the year, our Graduation Clause lets you leave early (with a modest success fee recouping our investment). Otherwise, we build together for the full year.

If you are looking for a casual slot, this is not it. If you are a disciplined professional seeking a serious launchpad, reply and we will send the Springboard Partnership Agreement and Media Release for your review.

Your ID is **[ART-xxx]**.

Regards, **Bola Kassim**, Director, Shack Entertainment Ltd.

*Bola approves before send: name and ID correct; folder path correct; nothing invented; no promises of fees, slots or exposure.*
"""

doc5 = """# DOCUMENT 5 — MEDIA RELEASE & ACKNOWLEDGEMENT
*Signed once, alongside the Springboard Partnership Agreement.*

- [ ] I have read the Springboard Partnership Agreement and understand it is a fixed one-year commitment.
- [ ] I understand Shack Entertainment Ltd owns the copyright in all audio/video recordings and photographs ("Shack Productions") made during my engagement.
- [ ] I grant Shack the irrevocable right to capture, film and record my performances for the Shack Archive and promotion.
- [ ] I retain ownership of my underlying songs/art; Shack owns the recordings of those works made at Shack events.
- [ ] I am a disciplined professional and will adhere to the roster's scheduling and production standards.

Signed (Artist) ………… Date …………
"""

for name, text in [('02_LE_Springboard_Partnership_Agreement.md', doc2),
                   ('04_LE_First_Contact_Letter.md', doc4),
                   ('05_LE_Media_Release_Acknowledgement.md', doc5)]:
    with open(os.path.join(T, name), 'w', encoding='utf-8') as f:
        f.write(text)
    print('Banked:', name)