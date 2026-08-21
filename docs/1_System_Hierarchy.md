# SHACK ENTERTAINMENT — SYSTEM HIERARCHY
Ground truth for the human team. AI drafts; humans export, publish, sign.

## 1. THE ESTATE
- Umbrella: Shack Entertainment (shackentertainment.co.uk)
- Divisions: Artists Unlimited (roster) | The Live Exchange (live
  events) | PND FineArt (Paul Duncan hyper-realism) | Shack News
  Network (editorial; standalone estate to follow)
- Brand truth: navy #1e1638 ground, gold #f3cc13 accent, Montserrat
  titles, Inter captions. Quiet confidence, no excess.
- The Law: non-extractive — artists own their work; we amplify,
  never mine.

## 2. THE HUMAN LAYER — GROUND SKELETON TEAM
- Bola — Owner. Tier-3 approver of every external act. Final
  editorial and brand authority.
- Operator (to hire) — daily rhythm: bot health, 6 AM edition
  review, calendar, mail queue, folder hygiene.
- Editor (to hire) — reads Desktop\Shack Daily News; approves or
  returns SNN drafts before any publication.
- Production Lead (to hire) — executes shoots from Film Director
  shot lists; owns equipment inventory and the OBS broadcast rig.
- Rule: no human or AI publishes externally without Bola.

## 3. THE AI CABINET — TWELVE AGENTS
- Chief of Staff (/cos) — routing, review, chain keeper
- Artist Relations (/ar) — consent, onboarding, artist voice
- Marketing (/mk) — campaigns, metadata, distribution
- Content Studio (/cs) — motion: recaps, reels, shorts, cut plans
- Shack News Editor (/news) — editorial desk; 6 AM daily edition
- Research Analyst (/ra) — intelligence, SEO, gaps; observed vs believed
- Site Ops (/ops) — uptime, alerts, evidence-first fixes
- Design Agent (/da) — stills, posters, thumbnails; render autonomy
- Brand Vision (/bv) — constitution keeper; FIT / DRIFT / VIOLATION
- Film Director (/fd) — shot lists, clearances, production reality
- Creative Director (/cd) — treatments, taste, cut lists
- Communications (/comms) — external replies; draft flow only

## 4. THE MACHINE LAYER
- Telegram bot (shack_main_agent.py) — the switchboard; watchdog
  restarts it if it dies.
- AnythingLLM (localhost:3001) — twelve workspaces; each room has a
  soul (system prompt) and receives its brief (ground truth) with
  every request.
- Ollama — one local brain: qwen3-vl:4b-instruct. (llama3:8b
  retired 2026-08-20.)
- Mail bridge — ryan@ → drafts held PENDING → /senddraft releases
  (Tier-3).
- Newsroom — RSS-grounded articles; md + PDF to Desktop\Shack Daily
  News at 06:00 daily; nothing publishes externally.
- Render pipe — Design renders locally; evidence over promises.
- Calendar wire — /cal holds, confirms, adds; conflicts held.

## 5. CHAIN OF COMMAND
Bola -> Chief of Staff -> Lane -> Chief of Staff -> Bola
- Nothing external skips the chain.
- Tier-3: every external act needs Bola's explicit approval.
- Consent before capture: artist footage, photos, audio — per
  event, upfront, written.
- No invented facts anywhere. Ask, don't invent.

## 6. HOUSE RULES OF THE STACK
- Every workspace: Chat mode, history 4, System default model.
- One model on the machine; long jobs queue — never resend.
- A room that 500s after changes gets rebuilt clean.
- Threads remember: a fresh thread cures learned bad habits.
- The bot never publishes. Humans export and sign.