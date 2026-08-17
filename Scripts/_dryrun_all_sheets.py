"""Dry-run: test all four sheet loads"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock st.secrets absent so OAuth path is used
class NoSecrets:
    def __getitem__(self, key): raise KeyError(key)
    def __contains__(self, key): return False
    def get(self, *a, **kw): return None
import types
fake_st = types.ModuleType('streamlit')
fake_st.secrets = NoSecrets()
fake_st.cache_data = lambda *a, **kw: (lambda f: f)
sys.modules['streamlit'] = fake_st

from data_sync import (
    load_live_exchange_data,
    load_artists_unlimited_data,
    load_news_network_data,
    load_financial_overview_data,
)

print("=" * 60)
print("1. Live Exchange")
print("=" * 60)
r = load_live_exchange_data()
e, b, a, f, o, snap, err = r
print(f"Error: {err}")
print(f"Events:    {len(e)} rows | {list(e.columns)[:5] if not e.empty else 'EMPTY'}")
print(f"Bookings:  {len(b)} rows")
print(f"Artists:   {len(a)} rows")
print(f"Financial: {len(f)} rows")
print(f"Snapshot:  {snap}")

print("\n" + "=" * 60)
print("2. Artists Unlimited")
print("=" * 60)
r = load_artists_unlimited_data()
if len(r) == 6:
    a2, inv, out, sal, par, err = r
    print(f"Error: {err}")
    print(f"Artists:    {len(a2)} rows | {list(a2.columns)[:6] if not a2.empty else 'EMPTY'}")
    print(f"Inventory: {len(inv)} rows | {list(inv.columns)[:6] if not inv.empty else 'EMPTY'}")
    print(f"Outlets:   {len(out)} rows")
    print(f"Sales:     {len(sal)} rows")
    print(f"Partners:  {len(par)} rows")
    if not inv.empty:
        print(f"  Inv row 1: {inv.iloc[0].to_dict()}")
else:
    print(f"UNEXPECTED: {r}")

print("\n" + "=" * 60)
print("3. News Network")
print("=" * 60)
r = load_news_network_data()
if len(r) == 7:
    c, y, s, ref, cam, snap2, err = r
    print(f"Error: {err}")
    print(f"Content:   {len(c)} rows")
    print(f"YouTube:   {len(y)} rows")
    print(f"Social:    {len(s)} rows")
    print(f"Referral:  {len(ref)} rows | {list(ref.columns)[:5] if not ref.empty else 'EMPTY'}")
    print(f"Campaign:  {len(cam)} rows")
    print(f"Snapshot:  {snap2}")
else:
    print(f"UNEXPECTED: {r}")

print("\n" + "=" * 60)
print("4. Financial Overview")
print("=" * 60)
r = load_financial_overview_data()
if len(r) == 5:
    rev, exp, cf, snap3, err = r
    print(f"Error: {err}")
    print(f"Revenue:  {len(rev)} rows")
    print(f"Expenses: {len(exp)} rows")
    print(f"CashFlow: {len(cf)} rows")
    print(f"Snapshot: {snap3}")
else:
    print(f"UNEXPECTED: {r}")

print("\n=== ALL TESTS COMPLETE ===")
