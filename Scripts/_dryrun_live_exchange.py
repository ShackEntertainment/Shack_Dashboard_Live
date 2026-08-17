"""Dry-run: simulate exactly what 2_Live_Exchange.py sees from data_sync"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

# Properly mock st.secrets as absent so data_sync falls back to local OAuth
class NoSecrets:
    """Behaves as if st.secrets does not exist — raises KeyError on any access."""
    def __getitem__(self, key):
        raise KeyError(key)
    def __contains__(self, key):
        return False
    def get(self, *a, **kw):
        return None

import types
fake_st = types.ModuleType('streamlit')
fake_st.secrets = NoSecrets()        # hasattr(st, 'secrets') -> True, but st.secrets[key] raises KeyError
fake_st.cache_data = lambda *a, **kw: (lambda f: f)
sys.modules['streamlit'] = fake_st

from data_sync import load_live_exchange_data

print("=== Calling load_live_exchange_data ===")
result = load_live_exchange_data()
events_df, bookings_df, artists_df, financials_df, ops_df, snapshot_dict, error_msg = result

print(f"Error: {error_msg}")
print(f"Events:     {len(events_df)} rows | {list(events_df.columns) if not events_df.empty else 'EMPTY'}")
print(f"Bookings:   {len(bookings_df)} rows | {list(bookings_df.columns) if not bookings_df.empty else 'EMPTY'}")
print(f"Artists:    {len(artists_df)} rows | {list(artists_df.columns)[:8] if not artists_df.empty else 'EMPTY'}")
print(f"Financials: {len(financials_df)} rows | {list(financials_df.columns) if not financials_df.empty else 'EMPTY'}")
print(f"Snapshot: {snapshot_dict}")

if not events_df.empty:
    print(f"\nFirst event: {events_df.iloc[0].to_dict()}")
if not artists_df.empty:
    print(f"\nFirst artist: {artists_df.iloc[0].to_dict()}")
if not financials_df.empty:
    col = 'Amount_In ' if 'Amount_In ' in financials_df.columns else 'Amount_In'
    total = pd.to_numeric(financials_df[col], errors='coerce').fillna(0).sum()
    print(f"\nTotal revenue: £{total:,.2f}")

if not error_msg and not any([len(x) if x is not None else 0 for x in [events_df, bookings_df, artists_df, financials_df]]):
    print("\nWARNING: All empty — check connection!")
elif not error_msg:
    print("\n=== LIVE DATA CONNECTED ===")
else:
    print(f"\nERROR: {error_msg}")
