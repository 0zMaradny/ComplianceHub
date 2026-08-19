# AutoClaw Setup — OWL v4.2

_AutoClaw is Z.ai's automation engine for scheduled OWL workflows. Full automation map and skills wiring: `../OPENCLAW_OWL_SKILLS.md` — this file is the pointer the OWL files reference as `autoclaw-projects/SETUP.md`._

## What's here

| Automation | Schedule | OWL Skills | Trigger |
|------------|----------|------------|---------|
| Morning Briefing | Daily 8 AM | 01b, 10, 28 | cron `0 8 * * *` |
| Audit Calendar Sync | Daily 9 AM | 14, 25 | cron `0 9 * * *` |
| Quality Gate Sweep | On save | 21, 22 | file `on_deliverable_save` |
| Template Population | On audit start | 02, 14, 25 | event `audit_session_start` |
| Evening Digest | Daily 6 PM | 01b, 32 | cron `0 18 * * *` |
| Weekly Reconciliation | Friday 5 PM | 22, 34 | cron `0 17 * * 5` |
| ComplianceHub Deploy Check | On git push | 38, 17 | event `git_push` |

## Setup steps

1. Read `../OPENCLAW_OWL_SKILLS.md` — the OpenClaw ↔ OWL integration map (skills wiring + workspace layout).
2. Configure AutoClaw natively in Z.ai Agent — paste the OWL system files as agent instructions (`../SOUL.md` + `../CONTEXT.md` minimum; add `../AGENTS.md` for full roster).
3. Create each automation with its cron trigger from the table above, referencing the OWL skills named.
4. Never manual — AutoClaw owns the scheduled layer (per OWL AGENTS.md rules).

## Related

- Z.ai Agent instructions: `../zai-projects/AGENT_INSTRUCTIONS.md`
- Z.ai quick setup: `../zai-projects/SETUP.md`
- Platform guides index: `../docs/INSTALL_GUIDES.md`

_Last updated: 2026-08-20_