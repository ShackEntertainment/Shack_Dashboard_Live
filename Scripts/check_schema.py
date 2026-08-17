import sqlite3, os
db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'executive_cache.db')
con = sqlite3.connect(db)
for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({name})")]
    print(f"{name}: {cols}")