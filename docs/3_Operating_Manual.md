# SHACK ENTERTAINMENT — FULL OPERATING MANUAL
How the estate runs day to day. For the ground skeleton team.

## 1. DAILY RHYTHM
06:00 — Newsroom auto-writes six articles; md + PDF land in
Desktop\Shack Daily News; summary hits Telegram.
07:00 — Operator: check bot alive (/status), read the news folder,
flag returns to Editor; clear mail queue (PENDING drafts to Bola).
09:00 — Calendar review: holds expire unless confirmed; conflicts
escalate to Bola.
Evening — Operator: glance watchdog SMS log; no action unless paged.

## 2. COMMAND REFERENCE (Telegram)
/status — bot heartbeat.
/dailynews [topic] — newsroom on demand (six, or one by keyword).
/cos /ar /mk /cs /news /ra /ops /da /bv /fd /cd /comms <request> —
the twelve lanes; each injects its brief automatically.
/cal hold|confirm|add ... — calendar wire; holds auto-expire.
/senddraft — releases a PENDING mail draft (Tier-3 in motion).
Rule: one request at a time per lane; long jobs queue — never
resend; a resend joins the queue behind your own answer.

## 3. APPROVAL FLOWS (TIER-3)
- Mail: draft arrives PENDING -> Bola reads -> /senddraft or drop.
- News: folder read -> approve or return; nothing publishes yet.
- Design: PNG attached as evidence; approve before external use.
- Everything else: CoS ruling -> Bola sign-off -> human exports.

## 4. WORKSPACE HYGIENE (AnythingLLM)
- Every room: Chat mode, history 4, System default model.
- Soul = system prompt (who the agent is); Brief = ground truth
  injected per request (configs\*.txt). Change briefs in Notepad;
  souls in the UI; always click Update Workspace.
- Threads remember: bad habits cured by New Thread, not louder rules.
- A room that 500s after changes: delete and recreate with the same
  name; paste the soul; re-apply settings; Update.

## 5. TROUBLESHOOTING LADDER
1. Stall / "thinking" long: WAIT. CPU brain; queue physics.
2. 500 error: settings saved? model pinned to a deleted model?
   then rebuild the room (section 4).
3. Glossy / off-voice output: New Thread; check model is the 4B.
4. Bot silent: watchdog pages SMS; shortcut restart; py_compile
   before every restart.
5. Never debug by resending requests.

## 6. GROUND TEAM CADENCE
Operator (daily): rhythm in section 1 + folder hygiene + backups.
Editor (daily): read the six; approve/return; keep the evidence
note discipline.
Production Lead (per shoot): FD shot list + clearance list signed
by Bola before cameras; inventory updated after every job.
Bola (always): the only signature on external acts.

## 7. GROWTH ROADMAP (QUEUED)
1. Roster & outlet data population (artists, bands, soloists,
   partners, backend staff; artist stock; outlets).
2. Equipment inventory + small-business video revenue line
   (leverage existing OBS rig and past work).
3. Animated Shack Origin Story (Happy Horse) to the Film Director:
   finishing, edit, sound plan.
4. Standalone sites: Shack News Network + Artists Unlimited.

## 8. THE LAW, RESTATED
Non-extractive: artists own their work; we amplify, never mine.
Consent before capture. No invented facts. No external act without
Bola. AI drafts; humans export, publish, sign.