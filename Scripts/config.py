"""
Shack Entertainment - Configuration
"""

import os
from pathlib import Path

# Base Paths
BASE_PATH = Path(r"C:\Users\Bola\Documents\Shack_Assets")
MANIFEST_PATH = BASE_PATH / "MASTER_MANIFEST.md"
PROTOCOL_PATH = BASE_PATH / "SHACK_ASSETS_PROTOCOL.md"

# Agent IDs
AGENT_IDS = {
    "CHIEF_OF_STAFF": "0fjr9eavdp2o",
    "CREATIVE_DIRECTOR": "ee30846e",
    "SHACK_NEWS_EDITOR": "16d35d97",
    "SITE_OPS": "m9cuyi4170nb",
    "SHACK_FINANCE": "e95ce80f",
    "COMMUNICATIONS_HUB": "55294ff9",
    "CONTENT_STUDIO": "vpys8rw63c09",
    "RESEARCH_ANALYST": "2b0s3pogrh1k"
}

# Brand Colors
BRAND_COLORS = {
    "PRIMARY_NAVY": "#1e1638",
    "BRIGHT_GOLD": "#f3cc13",
    "WARM_GOLD": "#cca739",
    "LINK_BLUE": "#99ccff",
    "WARM_TAN": "#d8a456",
    "DARK_NAVY": "#000030",
    "WHITE": "#ffffff"
}

# Division Paths
DIVISIONS = {
    "ARTISTS_UNLIMITED": BASE_PATH / "Artists_Unlimited",
    "LIVE_EXCHANGE": BASE_PATH / "Live_Exchange",
    "SHACK_NEWS_NETWORK": BASE_PATH / "Shack_News_Network",
    "PARTNERSHIPS": BASE_PATH / "Partnerships",
    "BRAND_CENTRAL": BASE_PATH / "Brand_Central"
}

# Access Levels
ACCESS_LEVELS = {
    "READ": "read",
    "WRITE": "write",
    "APPROVE": "approve",
    "RESTRICTED": "restricted"
}

def ensure_directories():
    """Ensure all required directories exist"""
    for division_path in DIVISIONS.values():
        division_path.mkdir(parents=True, exist_ok=True)