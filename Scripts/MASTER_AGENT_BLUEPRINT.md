# 🏰 SHACK ENTERTAINMENT: MASTER AGENT BLUEPRINT

## 📐 DELEGATION & REPORTING HIERARCHY
**Rule:** No agent communicates directly with the user. All outputs are filtered, verified, and packaged by the Chief of Staff (MD) before presentation. All inputs from the user are routed through the MD for task parsing and agent assignment.

## 📊 FULL AGENT ROSTER (COLUMNIZED SUMMARY)

| Agent | Core Role | Tools/Stack | Input Source | Output Deliverable | Human Review | Reports To |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Chief of Staff (MD)** | Central command, task parsing, verification, final reporting. | AnythingLLM, State Ledger | User commands | Verified, packaged deliverables | ✅ User | User |
| **📊 Data Sync** | Bridges Sheets ↔ Streamlit, queues offline changes, handles exports. | gspread, SQLite, APScheduler | Google Sheets, CSV uploads | Live data feeds, backup CSVs, sync logs | ✅ Optional | MD |
| **💰 Commission** | Auto-calculates 70/30 splits, tracks payouts, flags discrepancies. | Pandas, SQLite, Jinja2 | Sales data, partner contracts | Payout reports, commission ledger, dispute flags | ✅ Mandatory | MD |
| **🚨 Alert Dispatcher** | Monitors thresholds, routes notifications, manages escalation. | python-telegram-bot, smtplib, SQLite | System metrics, agent heartbeats | Telegram/Email alerts, resolution logs | ✅ Toggle | MD |
| **📅 Content/Event Scheduler** | Manages editorial queue, syncs calendars, auto-publishes drafts. | APScheduler, google-calendar-api | Draft articles, event briefs | Published posts, calendar entries, schedule reports | ✅ Mandatory | MD |
| **🎨 Design Agent** | Generates brand-consistent graphics, templates, social assets. | Pillow, Google Drive API, Canva (manual) | Design briefs, brand guidelines | PNG/PDF exports, versioned drafts, spec compliance logs | ✅ Mandatory | MD |
| **📰 News Gathering** | Curates industry trends, drafts articles, extracts citations. | feedparser, newspaper3k, BeautifulSoup | Topic keywords, source URLs | Curated drafts, source links, SEO metadata, trend reports | ✅ Mandatory | MD |
| **🎬 Video Editing Director** | Assembles clips, auto-captions, formats for social/events. | MoviePy, FFmpeg, Whisper, Python | Raw footage, scripts, brand templates | Edited clips, subtitled versions, optimized exports, preview links | ✅ Mandatory | MD |
| **🤝 Artist Onboarding** | Sends welcome packs, collects contracts, populates profiles. | Jinja2, Gmail API, SQLite, Telegram Bot | Artist sign-up forms, contract templates | Onboarding checklists, contract status, profile drafts | ✅ Toggle | MD |
| **📈 Financial Reconciler** | Cross-checks revenue, commissions, expenses, generates summaries. | Pandas, ReportLab, SQLite | Transaction logs, payout records | Weekly reconciliation PDFs, variance reports, audit trails | ✅ Mandatory | MD |
| **🛡️ Self-Healing Sentinel** | Monitors agent health, auto-restarts, enforces security, logs errors. | psutil, SQLite, pre-commit hooks | Agent logs, system metrics | Heartbeat reports, auto-recovery actions, security audit logs | ❌ Autonomous | MD |

## 📐 EXPANDED DATA ARCHITECTURE (3-SHEET ECOSYSTEM)
- **🎨 Artists Unlimited (AU_DB):** Sales, inventory, artist profiles, contracts. Syncs every 5 mins.
- **🎭 Live Exchange (LE_DB):** Events, tickets, venues, capacity, attendance, refunds. Syncs every 5 mins.
- **📰 Shack News (SN_DB):** Articles, drafts, published status, views, shares, categories. Syncs every 10 mins.
- **🏰 Executive Cache (SQLite):** Aggregated KPIs, commission ledger, alert thresholds, daily rollups. Streamlit reads from this cache, NOT directly from Google Sheets, to prevent lag and API limits.

## 🔑 KEY OPERATIONAL RULES
1. **Single Point of Command:** User delegates to MD. MD parses, assigns, verifies, and returns.
2. **Verification Gate:** Every output passes through MD's documentation-check and QA filter.
3. **Human-in-the-Loop Default:** All creative, financial, and publishing actions require explicit approval. Automation handles drafting, routing, and logging only.
4. **Cost Control:** All tools are open-source or free-tier. No subscriptions.

## 🛡️ SECURITY PROTOCOL
- **Credentials:** Stored ONLY in `.streamlit/secrets.toml` or local `.env` (gitignored).
- **Access:** Single Google Service Account with folder-level isolation.
- **Canva:** Human-in-the-loop workflow. Agents write briefs to `01_Briefs/`, human executes in Canva, exports to `03_Drafts/`, agent verifies.