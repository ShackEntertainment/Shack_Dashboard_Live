# SHACK OPS REGISTRY — updated 01/09/2026

## Scheduled jobs
| Job | Time | Runs | State |
| ShackMorningBrief | 08:00 | Scripts\shack_brief.py | HEALTHY |
| ShackOpsSweep | 07:00 | Scripts\shack_ops_sweep.py | CANARY — new |
| ShackBackup | 21:00 | Scripts\shack_backup.bat | CHECK (last 128) |
| Shack Daily Report | 08:00 | daily_report.py | RELIC — disabled 01/09 |

## Bot-internal loops
| mail_loop | 5-min poll | drafts to MD only | LIVE |
| news loop | 06:00 desk | LIVE — keep 05:30–08:30 free of LLM grinds |

## External surfaces
| X ×4 | password+2FA, all apps revoked | DARK till relaunch |
| Buffer | channels disconnected, key starred | DORMANT |
| Mailchimp | signup paused | PAUSED |
| shackentertainment.co.uk | HTTP 403 | DARK (as ordered) |
| theliveexchange.com | DNS FAILED | CHECK renewal/DNS in Hostinger |
| Twilio | trial suspended | DEAD — heartbeat build later |

## AnythingLLM skills (estate-wide)
ON (read/draft): RAG, summarize, scrape, web search, doc creation, charts.
OFF (write/reach): File System, SQL, GMail, GCal, Outlook. No MCP, no flows.

## Approval gates
| /senddraft | Tier-3, MD-only |
| owner gate | every bot command MD-only |
| Comms agent | drafts only, [AWAITING BOLA APPROVAL] |
| Design agent | brand card + authority rule, no connector |