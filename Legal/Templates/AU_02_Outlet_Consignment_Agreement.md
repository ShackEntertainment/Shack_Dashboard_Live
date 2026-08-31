"""
SHACK ENTERTAINMENT — shack_generate_au02.py
Banks the Outlet Consignment Agreement.
"""
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(os.path.dirname(script_dir), 'Legal', 'Templates')
os.makedirs(T, exist_ok=True)

au02 = """# AU_02 — OUTLET CONSIGNMENT AGREEMENT

**BETWEEN:** (1) SHACK ENTERTAINMENT LIMITED ("the Company"); and (2) [OUTLET NAME], of [address] ("the Outlet").

**1. NATURE** — The Outlet stocks and sells artists' works consigned through the Company. Non-exclusive on both sides.
**2. STOCK** — Each consignment is logged by SKU, title and retail price. Title remains the artist's until sold.
**3. PRICING** — Works sell at the artist's retail price. Discounts above 10% require the Company's written approval.
**4. MONEY** — The Outlet remits gross sale proceeds to the Company's client account by the 7th of each month. The Outlet's commission ([25]% of gross) is paid by the Company with the same statement. The artist's 70% share is untouchable and paid by the Company under AU_01.
**5. REPORTING** — Every sale is logged via the Company's sales form within 7 days; stock is reconciled monthly.
**6. CARE** — The Outlet is liable for loss, theft or damage while works are in its possession and shall insure them.
**7. UNSOLD STOCK** — Returned within 30 days of request or termination; return shipping borne by the Company.
**8. IP & CREDIT** — Artists retain copyright. Works display with the artist's credit; no reproduction without the artist's consent.
**9. PAYMENT CHAIN** — The Outlet remits proceeds to the Company only, never to an artist directly.
**10. TERM** — Twelve (12) months; 30 days' notice either way; no automatic renewal.
**11. GENERAL** — Clauses 9.1-9.9 of AU_01 apply as if repeated here.

**SIGNED** for the Company: BOLA KASSIM, Director ………… **for the Outlet:** ………… Date …………
"""

with open(os.path.join(T, 'AU_02_Outlet_Consignment_Agreement.md'), 'w', encoding='utf-8') as f:
    f.write(au02)
print('Banked: AU_02_Outlet_Consignment_Agreement.md')