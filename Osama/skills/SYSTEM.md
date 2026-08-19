# Skills — SYSTEM Domain
_Load on demand for session management, quality gates, tokens, routing._

**Skills:** 01, 01b, 15, 21, 22, 23, 29, 30, 31, 37, 39 | **Agent 8 (Prompt Architect)** + Agent 11 (Router)

---

## Skill 01 — Session Start (Auto)
Load: SOUL.md → CONTEXT.md → AGENTS.md → MEMORY.md → activate agent → load domain file

## Skill 01b — Session End
Update memory/YYYY-MM-DD.md → check .learnings/ → promote patterns → git commit

## Skill 15 — Universal Prompt Transform (Layer 0, Every Message)
Inspect → route to agent → if ambiguous: ONE question → never blend Track A + B

## Skill 21 — Language Gate (Auto, Before Every Deliverable)
- English technical / Arabic MSA client / ISO refs always English / no AI filler
- Run humanizer BEFORE this gate

## Skill 22 — Quality Gates G1–G10 (Auto, Before Every Client Deliverable)
| Gate | Name | Check |
|------|------|-------|
| G1 | Completeness | No placeholders/TBD |
| G2 | Accuracy | Clause refs valid |
| G3 | Consistency | Naming <PREFIX>-<CODE>-<DATE>.<ext> |
| G4 | Formatting | Client visual identity |
| G5 | Language | No AI filler |
| G6 | Client Isolation | No cross-client data |
| G7 | Regulatory | KSA overlays applied |
| G8 | Workflow | Correct template order |
| G9 | Confidence | Above threshold (RICH≥70%, SEMI≥40%, SPARSE≥20%) |
| G10 | Audit-Defensibility | Every field traceable |

**Pipeline:** humanizer → Skill 21 → Skill 22 → Delivery

## Skill 23 — Token Compression
**Trigger:** "Compress" / "Too long" / "Token limit"
caveman: full at 60 turns, ultra on phone. Never drop SOUL.md or CONTEXT.md.

## Skill 29 — Skill Installation & Management
**Trigger:** "Update skill" / "Install skill" / "Plugin"
Check overlap → build → update SKILLS.md + AGENTS.md

## Skill 30 — Auto-Trigger Router (Silent, Every Message)
Scan → match → activate agent. Never announce routing.

## Skill 31 — Token Pipeline Management
markitdown (inputs) → LeanCTX (terminal) → caveman (output). Caps: 60 turns / 60K chars / 5K per file.

## Skill 37 — Workspace Configuration
**Trigger:** "Configure workspace" / "MCP setup"
LeanCTX doctor → OWL files in root → MCP (max 5) → Hybrid Thinking

## Skill 39 — PII Scrub & Safe Routing
**Trigger:** "Send to non-Claude" / "Scrub PII"
Scrub: names → [EMPLOYEE-001], phones → [PHONE-REDACTED], emails → [EMAIL-REDACTED]
HIGH clients → Claude/local ONLY. Never scrub: ISO clauses, formulas, doc codes.

_Last updated: 2026-08-09 · OWL v4.0_
