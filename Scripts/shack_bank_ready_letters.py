"""
SHACK ENTERTAINMENT — shack_bank_ready_letters.py
Banks the three held letters into Mail_Drafts\ready_to_send.
Nothing sends until the MD gives the word.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(script_dir), 'Mail_Drafts', 'ready_to_send')
os.makedirs(OUT, exist_ok=True)

nick = """Subject: Invitation to The Live Exchange — Professional Springboard Roster (Ref: LE-001)

Hi Nick,

We have reviewed your work and would like to invite you to join The Live Exchange roster.

The Live Exchange is not a hobbyist collective; it is a professional production house. We invest significant capital — venue costs, professional sound and lighting, SIA security, and marketing — into a select group of disciplined artists who deserve better infrastructure than the DIY circuit but are not ready (or willing) to sign away their rights to a major label.

The Commitment: We operate on a fixed one-year Rotation. We do not offer try-outs or month-to-month slots. We invest in artists who are organized, reliable and committed to the schedule. In return, we provide infrastructure independent artists rarely access.

The Deal:
- You own your work: your playing, your compositions, your IP. Always.
- We own the production: Shack Entertainment owns the masters, video recordings and archive of the performances we fund and produce. You may use them freely for your promo; we retain the archive.
- The Split: 70% of Shack-calendar revenue to you, 30% to Shack to cover production and platform costs.
- The Exit: you are self-managed outside our calendar. If you land a major label or agency deal during the year, our Graduation Clause lets you leave early (with a modest success fee recouping our investment). Otherwise, we build together for the full year.

If you are looking for a casual slot, this is not it. If you are a disciplined professional seeking a serious launchpad, reply and we will send the Springboard Partnership Agreement and Media Release for your review.

Your ID is LE-001.

Regards,
Bola Kassim, Director, Shack Entertainment Ltd.
"""

pullingers = """Subject: Shack Entertainment x Pullingers — consignment proposal

Dear Pullingers team,

We are a Twickenham entertainment company placing work by our represented artists — greeting cards, prints and textiles among them — in selected independent outlets. We would be glad to start with you.

The model is simple: we consign stock; title stays with the artist; everything sells at the artist's retail price. You report sales through a one-minute monthly form and remit gross proceeds by the 7th; we pay your 25% commission with the same statement, and we handle the artists entirely — you never owe an artist anything directly. Unsold stock returns to us within 30 days, at our cost, whenever you ask.

Enclosed is our one-page Outlet Consignment Agreement — the whole relationship, in plain English. If it reads well, we'll bring a first consignment and let the work sell itself.

Warm regards,
Bola Kassim, Director, Shack Entertainment Ltd.
"""

paul = """Subject: Your new Shack agreement — same 30%, everything else better

Paul,

Further to what I played you the other day: enclosed is the new Shack house agreement, filled with your name and address, ready to sign.

To be plain about what changes: the "in perpetuity" commission dies — it fades to 15/10/5% over three years after the term, then zero. You become non-exclusive — sell direct or through any gallery and we earn nothing on it. The £500 penalty and the 5% monthly interest are deleted. We insure your consigned work and answer for it while it's with us. You're paid within 30 days of every sale even if the buyer is on layaway. And the company signs, not me personally — same people, cleaner paper.

What stays: 30% on what we secure, your trust account, monthly statements, and your ownership of every work. The term becomes 3 years with no auto-renewal — it ends when it ends, and renews only if we both sign again.

Signing this replaces the 14 January paper entirely. If you'd rather keep the old one, say the word and it stands — you're family first. But I'd be signing this one.

When it's signed, I'll load your opening stock (Sunset Mugs, Ocean Prints, Card Packs, Albury Downs, Tea Towels) into the new system and your first statement follows at month-end.

Bola.
"""

for name, text in [('READY_Nick_Marshall_LE001_first_contact.md', nick),
                   ('READY_Pullingers_outlet_pack.md', pullingers),
                   ('READY_Paul_Duncan_supersede.md', paul)]:
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(text)
    print('Banked:', name)