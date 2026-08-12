# SKILLS.md — Master Skill Index & Trigger Table
_Last updated: 2026-08-09 · Projects vs Audit Clients model · Template population pipeline_

## Skill → Agent Mapping

| Skill # | Name | Agent | Domain File |
|---------|------|-------|-------------|
| 01b | Session-End Memory Trigger | 8+11 | SYSTEM.md |
| 02 | IMS Audit | 1 | AUDIT.md |
| 03 | Excel Risk Register | 2+4 | IMPLEMENT.md |
| 04 | BIA Workbook | 2+4 | IMPLEMENT.md |
| 05 | Arabic BCM Document | 2+5 | IMPLEMENT.md |
| 06 | ISO 42001 AIMS | 2 | IMPLEMENT.md |
| 07 | Gap Check (Pre-Assessment) | 1 | AUDIT.md |
| 08 | Python Automation | 3 | DEV.md |
| 09 | Risk Treatment Plan | 2+4 | IMPLEMENT.md |
| 10 | Travel & Bookings | 6 | PERSONAL.md |
| 11 | ComplianceHub Development | 3+7 | DEV.md |
| 12 | CAPA | 1 | AUDIT.md |
| 14 | Audit Package (TÜV Austria) | 1 | AUDIT.md |
| 15 | Universal Prompt Transform | 8 | SYSTEM.md |
| 16 | Six-Gate Certification Pipeline | 2+9 | IMPLEMENT.md |
| 17 | Debugging | 3 | DEV.md |
| 19 | Productivity | 6 | PERSONAL.md |
| 20 | Training PPTX | 2+5+7 | IMPLEMENT.md |
| 21 | Language Gate | 8+11 | SYSTEM.md |
| 22 | Quality Gates (G1–G10) | 8+11 | SYSTEM.md |
| 23 | Token Compression | 8 | SYSTEM.md |
| 24 | Document Version Control | 2 | IMPLEMENT.md |
| 25 | Client Onboarding (Projects vs Audit Clients) | 2 | IMPLEMENT.md |
| 26 | Audit Report | 1 | AUDIT.md |
| 27 | SoA (Statement of Applicability) | 1 | AUDIT.md |
| 28 | Pre-Audit Research | 1 | AUDIT.md |
| 29 | Skill Management | 8 | SYSTEM.md |
| 30 | Auto-Trigger Router | 11 | SYSTEM.md |
| 31 | Token Pipeline | 8 | SYSTEM.md |
| 32 | Board Update | 11 | PERSONAL.md |
| 33 | Adversarial Stress-Test | 11 | PERSONAL.md |
| 34 | Automation Roadmap | 6 | PERSONAL.md |
| 35 | Inbox Triage & Personal Voice | 6 | PERSONAL.md |
| 37 | Workspace Configuration | 8 | SYSTEM.md |
| 38 | Code Review Gate | 3 | DEV.md |
| 39 | PII Scrub & Route (Projects vs Audit Clients) | 11 | SYSTEM.md |

**Count: 38 active + 2 tombstoned (13, 18)**

## Domain File Map

| Domain File | Skills | Agent Focus |
|-------------|--------|-------------|
| `skills/AUDIT.md` | 02, 07, 12, 14, 26, 27, 28 | Agent 1 (Judge) |
| `skills/IMPLEMENT.md` | 01, 03, 04, 05, 06, 09, 16, 20, 24, 25 | Agent 2 (Architect) |
| `skills/DEV.md` | 08, 11, 17, 38 | Agent 3 (Developer), Agent 7 (Platform) |
| `skills/SYSTEM.md` | 01b, 15, 21, 22, 23, 29, 30, 31, 37, 39 | Agent 8 (Prompt), Agent 11 (Router) |
| `skills/PERSONAL.md` | 10, 19, 32, 33, 34, 35 | Agent 6 (Concierge), Agent 11 (Board/Stress) |
| `skills/humanizer/SKILL.md` | (pre-pipeline) | All agents · 33-pattern anti-slop |

## Auto-Trigger Table

| Signal | Agent | Skills |
|--------|-------|--------|
| Audit / NC / gap / compliance | 1 | 02, 07, 26 |
| Policy / procedure / implement | 2 | 16, 24, 25 |
| New client / onboard / client setup | 2 | 25 (Project: full profile · Audit client: quick-add row) |
| Python / script / automate | 3 | 08, 11, 17 |
| Excel / risk register / BIA | 4 | 03, 04, 09 |
| Arabic / RTL / BCM | 5 | 05, 20 |
| Travel / flight / cashback / deal | 6 | 10, 19 |
| ComplianceHub / React / frontend | 7 | 11, 14, 17 |
| Prompt / improve / skill design | 8 | 15, 21, 29 |
| Project / gate / timeline | 9 | 16 |
| KSA / NCA / SAMA / PDPL | 10 | 02, 07, 28 |
| Board update / executive summary | 11 | 32 |
| Stress-test / blind spots / should I | 11 | 33 |
| Inbox / triage / personal voice | 6 | 35 |
| Automation / roadmap / workflow audit | 6 | 34 |
| AutoClaw / scheduled / cron / automate | AutoClaw | 01b, 10, 14, 21, 22, 25, 28, 32, 34, 38 |
| populate / new audit package / manday calc / audit plan / checklist / certificate | 1 + Skill 14 | 14, 02, 25 (see templates/tuv-austria/POPULATION.md) |
| Z.ai Chat / quick question / lookup / spot-check | Any (light) | Chat mode |

## Client Routing — Projects vs Audit Clients

| Category | Who | Sensitivity | Default Route |
|----------|-----|-------------|---------------|
| **Projects** | MSD-MOI, Al-Ahsa (HIGH) | HIGH → Claude/Cline/Hermes ONLY | Full profile in `clients/<NAME>.md` |
| **Projects** | SAGCO + new (MEDIUM) | MEDIUM → all with PII scrub | Full profile in `clients/<NAME>.md` |
| **Audit Clients** | Daily by calendar | Varies → classify per client | One-line in CONTEXT.md |
| Archived | UACC, MOC | — | `clients/archive/` |

## Z.ai Mode Routing

| Signal | Z.ai Mode | Why |
|--------|-----------|-----|
| CAPA / root cause / formula verify / stress-test | Agent | Multi-step reasoning needs full OWL context |
| Arabic doc / pre-audit analysis | Agent | Needs client profile + skill domain file |
| "What clause covers X?" / quick lookup / formula spot-check | Chat | One question, no agent overhead |
| Brainstorm / triage / simple yes-no | Chat | Lightweight, fast |
| Morning briefing / calendar sync / quality gate | AutoClaw | Scheduled, recurring, never manual |
| Template population / deploy check / weekly recon | AutoClaw | Automated pipeline, cron-triggered |

## Quality Gates (Skill 22)

| Gate | Name | What It Checks |
|------|------|----------------|
| G1 | Completeness | No placeholders, no TBD, no half-finished |
| G2 | Accuracy | Formulas correct, clause refs valid |
| G3 | Consistency | Naming, terminology, doc codes match |
| G4 | Formatting | Visual identity, layout, print-ready |
| G5 | Language | Skill 21 passed, no AI filler |
| G6 | Client isolation | No cross-contamination (Projects vs Audit Clients) |
| G7 | AI patterns | Humanizer passed, no AI writing signs |
| G8 | Visual polish | Alignment, spacing (if UI) |
| G9 | Accessibility | Contrast, keyboard nav (if UI) |
| G10 | Audit-defensibility | Every claim traceable |
