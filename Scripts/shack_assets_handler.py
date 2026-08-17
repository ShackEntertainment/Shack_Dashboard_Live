"""
SHACK ENTERTAINMENT — shack_assets_handler.py
Local knowledge-base manager for Shack_Assets/ (Markdown) + executive_cache.db (SQLite).

Capabilities:
  * Read manifests / cards / any asset file (path-traversal guarded)
  * Create & update TALENT, PARTNER and RELEASE cards (optional category subfolder)
  * 5-minute onboarding workflow: Manifest -> Card -> DB
  * structure command: pre-create Session_Musicians + Shack_Media subfolders
  * Self-test for verification

Hard rules baked in:
  * 100% local. No network calls, no publishing, no external action of any kind.
  * Talent policy: 70/30 favoring the artist during the 1-year Shack contract;
    artist owns all rights to works, merchandise and future income after it ends.
  * Partner policy: company-level funding stream; artist arrangements separate.
  * Release policy: creator retains full ownership of the work; Shack distribution
    and promotion rights run only through the 1-year contract, then revert fully.
"""
from __future__ import annotations

import re
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ------------------------------------------------- location auto-discovery
def _discover_assets() -> Path:
    p = Path(__file__).resolve()
    for base in (p.parent, p.parent.parent, p.parent.parent.parent):
        cand = base / "Shack_Assets"
        if cand.is_dir():
            return cand
    return p.parent.parent / "Shack_Assets"

def _discover_db(assets: Path) -> Path:
    p = Path(__file__).resolve()
    for base in (p.parent, p.parent.parent, p.parent.parent.parent):
        cand = base / "executive_cache.db"
        if cand.exists():
            return cand
    return assets.parent / "Shack_Project" / "executive_cache.db"

ASSETS_ROOT = _discover_assets()
DB_PATH     = _discover_db(ASSETS_ROOT)

DIVISIONS = {
    "artists_unlimited":  "Artists_Unlimited",
    "live_exchange":      "Live_Exchange",
    "partnerships":       "Partnerships",
    "shack_media":        "Shack_Media",
    "shack_news_network": "Shack_News_Network",
    "session_musicians":  "Session_Musicians",
    "session_players":    "Session_Players",
    "talent_roster":      "Talent_Roster",
}

SESSION_SUBFOLDERS = ["Guitarists", "Bassists", "Drummers",
                      "Keyboardists", "Vocalists", "Other"]

MEDIA_SUBFOLDERS = ["Music_Releases", "Film_Video", "Audio", "Store_Pages"]

POLICY_TALENT  = ("70/30 revenue split favoring the artist during the 1-year Shack "
                  "contract. The artist owns all rights to their works, merchandise "
                  "and all future income in full after the contract ends.")
POLICY_PARTNER = ("Company-level income stream funding Shack Entertainment. "
                  "Artist arrangements are separate and always 70/30 artist-favoring.")
POLICY_RELEASE = ("The creator retains full ownership of the work. Shack Entertainment's "
                  "distribution and promotion rights run only through the 1-year contract; "
                  "all rights revert fully to the creator afterwards.")
PROTOCOL_NOTE  = "Internal record. Nothing external without Bola's explicit approval."

# ------------------------------------------------------------------ helpers
def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name.strip()).strip("_")

def _safe(rel: str) -> Path:
    p = (ASSETS_ROOT / rel).resolve()
    if not str(p).startswith(str(ASSETS_ROOT.resolve())):
        raise ValueError("Path escapes Shack_Assets — blocked.")
    return p

# ------------------------------------------------------------------ readers
def read_asset(rel: str) -> str:
    return _safe(rel).read_text(encoding="utf-8")

def read_master_manifest() -> str:
    return read_asset("MASTER_MANIFEST.md")

def read_division_manifest(key: str) -> str:
    return read_asset(f"{DIVISIONS[key]}/MANIFEST.md")

def list_tree(rel: str = "") -> list:
    root = _safe(rel)
    return [str(p.relative_to(ASSETS_ROOT))
            for p in sorted(root.rglob("*")) if p.is_file()]

# ----------------------------------------------------------------------- db
def _db_exec(sql: str, params: tuple = (), fetch: bool = False):
    con = sqlite3.connect(DB_PATH)
    try:
        con.execute("""CREATE TABLE IF NOT EXISTS shack_cards(
            name TEXT PRIMARY KEY, kind TEXT, division TEXT,
            path TEXT, status TEXT, created TEXT, updated TEXT)""")
        cur = con.execute(sql, params)
        con.commit()
        return cur.fetchone() if fetch else None
    finally:
        con.close()

def db_upsert(name, kind, division, path, status="active"):
    _db_exec("""INSERT INTO shack_cards(name,kind,division,path,status,created,updated)
                VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(name) DO UPDATE SET kind=excluded.kind,
                  division=excluded.division, path=excluded.path,
                  status=excluded.status, updated=excluded.updated""",
             (name, kind, division, path, status, _now(), _now()))

def db_get(name):
    return _db_exec("SELECT * FROM shack_cards WHERE name=?", (name,), fetch=True)

# -------------------------------------------------------------------- cards
def _card_tag(kind: str) -> str:
    return {"talent": "TALENT_CARD", "partner": "PARTNER_CARD",
            "release": "RELEASE_CARD"}.get(kind, "CARD")

def _card_policy(kind: str) -> str:
    return {"talent": POLICY_TALENT, "partner": POLICY_PARTNER,
            "release": POLICY_RELEASE}.get(kind, PROTOCOL_NOTE)

def card_relpath(kind: str, key: str, name: str, category=None) -> str:
    if category:
        return f"{DIVISIONS[key]}/{category}/{slug(name)}_{_card_tag(kind)}.md"
    return f"{DIVISIONS[key]}/{slug(name)}_{_card_tag(kind)}.md"

def create_card(kind, key, name, fields: dict, force=False, category=None):
    rel = card_relpath(kind, key, name, category)
    path = _safe(rel)
    if path.exists() and not force:
        return rel, False
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {name} — {_card_tag(kind).replace('_', ' ')}", ""]
    lines += [f"**Kind:** {kind}", f"**Division:** {DIVISIONS[key]}"]
    if category:
        lines.append(f"**Category:** {category}")
    lines += ["**Status:** active", f"**Policy:** {_card_policy(kind)}",
              f"**Created:** {_now()}", "", "## Profile"]
    lines += [f"**{k.title()}:** {v}" for k, v in fields.items()]
    lines += ["", "## Notes", "- ", "", f"_{PROTOCOL_NOTE}_", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return rel, True

def append_note(kind, key, name, note: str, category=None):
    path = _safe(card_relpath(kind, key, name, category))
    if not path.exists():
        raise FileNotFoundError(path.name)
    text = path.read_text(encoding="utf-8")
    if "## Notes" in text:
        head, tail = text.split("## Notes", 1)
        text = head + "## Notes" + f"\n- {note}" + tail
    else:
        text += f"\n## Notes\n- {note}\n"
    path.write_text(text, encoding="utf-8")

def append_to_manifest(key, line: str):
    rel = f"{DIVISIONS[key]}/MANIFEST.md"
    path = _safe(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(f"# {DIVISIONS[key]} — MANIFEST\n\n", encoding="utf-8")
    path.write_text(path.read_text(encoding="utf-8") + f"- {line}\n",
                    encoding="utf-8")

# --------------------------------------------------------------- structure
def create_structure() -> list:
    """Pre-create Session_Musicians + Shack_Media subfolders."""
    made = []
    for sub in SESSION_SUBFOLDERS:
        p = _safe(f"Session_Musicians/{sub}")
        p.mkdir(parents=True, exist_ok=True)
        made.append(f"Session_Musicians/{sub}")
    for sub in MEDIA_SUBFOLDERS:
        p = _safe(f"Shack_Media/{sub}")
        p.mkdir(parents=True, exist_ok=True)
        made.append(f"Shack_Media/{sub}")
    return made

# ---------------------------------------------------------------- onboarding
def onboard(kind, key, name, fields: dict, category=None) -> dict:
    """The 5-minute workflow: Manifest -> Card -> DB."""
    if key not in DIVISIONS:
        raise KeyError(f"Unknown division '{key}'")
    category = category or fields.pop("category", None)
    rel, created = create_card(kind, key, name, fields, category=category)
    append_to_manifest(key, f"{name} — onboarded {_now()} (card: {rel})")
    db_upsert(name, kind, DIVISIONS[key], rel)
    return {"card": rel, "created": created, "category": category,
            "manifest": f"{DIVISIONS[key]}/MANIFEST.md", "db": "upserted"}

# ----------------------------------------------------------------- selftest
def selftest() -> str:
    global ASSETS_ROOT, DB_PATH
    orig = (ASSETS_ROOT, DB_PATH)
    tmp = Path(tempfile.mkdtemp(prefix="shack_selftest_"))
    try:
        ASSETS_ROOT = tmp / "Shack_Assets"
        DB_PATH = tmp / "executive_cache.db"
        ASSETS_ROOT.mkdir(parents=True)
        (ASSETS_ROOT / "MASTER_MANIFEST.md").write_text("# MASTER\n", encoding="utf-8")
        r1 = onboard("talent", "live_exchange", "Self Test", {"bio": "test act"})
        assert (ASSETS_ROOT / r1["card"]).exists()
        assert db_get("Self Test") is not None
        assert "Self Test" in read_division_manifest("live_exchange")
        r2 = onboard("partner", "partnerships", "Test Co", {"sector": "supplies"})
        assert (ASSETS_ROOT / r2["card"]).exists()
        r3 = onboard("talent", "session_musicians", "Cat Test",
                     {"bio": "g"}, category="Guitarists")
        assert "Guitarists" in r3["card"]
        assert (ASSETS_ROOT / r3["card"]).exists()
        r4 = onboard("release", "shack_media", "Dub Return",
                     {"artist": "Nick Marshall"}, category="Music_Releases")
        assert "RELEASE_CARD" in r4["card"] and "Music_Releases" in r4["card"]
        assert (ASSETS_ROOT / r4["card"]).exists()
        read_master_manifest()
        list_tree()
        return "SELFTEST PASS"
    finally:
        ASSETS_ROOT, DB_PATH = orig

# ---------------------------------------------------------------------- cli
def main(argv):
    cmd = argv[1] if len(argv) > 1 else "list"
    if cmd == "selftest":
        print(selftest()); return
    if cmd == "structure":
        print("\n".join(create_structure())); return
    if cmd == "paths":
        print(f"ASSETS_ROOT = {ASSETS_ROOT}")
        print(f"DB_PATH     = {DB_PATH}")
        return
    if cmd == "list":
        print("\n".join(list_tree())); return
    if cmd == "manifest":
        key = argv[2] if len(argv) > 2 else None
        print(read_master_manifest() if not key else read_division_manifest(key))
        return
    if cmd == "onboard":
        kind, key, name = argv[2], argv[3], argv[4]
        fields = {}
        for pair in argv[5:]:
            k, _, v = pair.partition("=")
            fields[k] = v
        print(onboard(kind, key, name, fields)); return
    print("Usage: shack_assets_handler.py [list|selftest|paths|structure|"
          "manifest [key]|onboard <talent|partner|release> <division> <Name> "
          "[category=X] [k=v ...]]")

if __name__ == "__main__":
    main(sys.argv)