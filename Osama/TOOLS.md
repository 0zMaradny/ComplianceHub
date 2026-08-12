# TOOLS.md — Infrastructure, API Routing & Skills Registry
_Version: 4.1 · August 2026_

_Infrastructure specifics for OWL. Skills define how tools work; this file defines what tools exist and how they route._

---

## API Routing

### OpenRouter (Primary AI Router)

| Route | Model | Use | Free? |
|-------|-------|-----|-------|
| Default | nvidia/nemotron-ultra-253b | Hermes Agent | ✅ |
| Fast | google/gemma-3-27b-it:free | Cline fallback | ✅ |
| Code | qwen/qwen3-235b-a22b:free | Cline fallback | ✅ |
| Variety | mistralai/mistral-small-3.2-24b-instruct:free | Cline fallback | ✅ |
| Speed | groq/llama-3.3-70b | Speed-critical | ✅ |

**Endpoint:** `openrouter.ai/api/v1` — never hardcode provider endpoints directly

### Direct Platform Access

| Platform | Model | Endpoint Type | Auth |
|----------|-------|---------------|------|
| Qwen Studio | Qwen 3.8 Max | Web UI (qwen.ai) | Account login |
| Z.ai Agent | GLM-5.2 | Agent mode (z.ai) | Account login |
| Z.ai Chat | GLM-5.2 | Chat mode (z.ai) | Account login |
| AutoClaw | Z.ai automation engine | AutoClaw (z.ai) | Account login |
| Gemini Pro | Pro 3.1 / Flash 3.5 / Thinking 3.6 | API (ai.google.dev) | Company API key |
| Cline | DeepSeek Flash V4 via OpenRouter | VS Code extension | OpenRouter key |
| MiniMax | MiniMax | Web UI | Account login |
| MiMo | MiMo-V2.5-Pro | Web UI | Account login |

**⚠️ Anthropic API blocked in KSA** — access Claude via OpenRouter only, or use Claude phone app

---

## Z.ai Platform Modes — When to Use Which

| Mode | What | OWL Load | Best For | Turn Limit |
|------|------|----------|----------|------------|
| **Z.ai Agent** | Full agent with knowledge files, instructions, tools | Full: SOUL + CONTEXT + AGENTS + MEMORY + skill domain file + client profile | Multi-step reasoning, CAPA, stress-test, formula verification, pre-audit analysis, Arabic doc drafting | ~60 desktop · ~40 phone |
| **Z.ai Chat** | Lightweight conversation, no agent setup | Light: SOUL summary + CONTEXT client row + 1 skill paragraph | Quick lookups, one-off analysis, brainstorming, formula spot-checks, "what clause covers X?", simple triage | ~60 desktop · ~40 phone |
| **AutoClaw** | Automated agent with scheduled triggers + OWL skill pipeline | Full: SOUL + CONTEXT + AGENTS + all skill domain files | Scheduled workflows (morning briefing, calendar sync), batch template population, quality gate automation, recurring client checks, audit package assembly | Unlimited (cron-driven) |

**Decision rule:** If it needs full OWL context and multiple steps → Z.ai Agent. If it's one question or quick check → Z.ai Chat. If it runs on a schedule or repeats → AutoClaw.

### AutoClaw — OWL Setup

**Purpose:** Automated OWL workflows that run without manual intervention.

| Automation | Schedule | OWL Skills | Description |
|------------|----------|------------|-------------|
| Morning Briefing | Daily 8 AM | 01b, 10, 28 | Load audit calendar → list today's audits → classify sensitivity → brief |
| Audit Calendar Sync | Daily 9 AM | 14, 25 | Pull new audit clients → update CONTEXT.md Audit Clients table → classify |
| Quality Gate Sweep | On deliverable save | 21, 22 | Auto-run Language Gate + Quality Gates on saved outputs |
| Template Population | On audit start | 02, 14, 25 | Identify standard → load TÜV template → pre-fill (RICH/SEMI/SPARSE) → regulatory overlays → confidence report → queue |
| Evening Digest | Daily 6 PM | 01b, 32 | Summarize day's work → update MEMORY.md → build board summary |
| Weekly Reconciliation | Friday 5 PM | 22, 34 | Reconcile skill counts, client status, platform usage → update SOUL.md Canonical Counts |
| ComplianceHub Deploy Check | On git push | 38, 17 | Run code review gate → lint check → build verification |

**AutoClaw config location:** `autoclaw-projects/SETUP.md`

---

## MCP Server Registry

| Server | Purpose | Status | Used By |
|--------|---------|--------|---------|
| Context7 | Live FastAPI/React API docs | ✅ Active | Agent 3, 7 |
| GitHub | PR/issue/code management | ✅ Active | Agent 3, 7 |
| Playwright | E2E testing | ✅ Active | Agent 7 |
| agent-browser | Web scraping (government/ISO sites) | ✅ Active | Agent 1, 10 |
| Alibaba OCR | Code review with custom rules | ✅ Active | Agent 3, 7 (Skill 38) |

**Hard limit:** Never exceed 5 active MCP servers simultaneously (SOUL.md Law #7)

---

## Installed CLI Tools

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| caveman | latest | Token compression + review | npm global |
| graphify | latest | Codebase knowledge graph (30+ file repos only) | npm global |
| markitdown | latest | Document ingestion (PDF/DOCX/PPTX/XLSX/URL → .md) | pip global |
| repomix | latest | One-shot codebase snapshots | npm global |
| LeanCTX | latest | Compress terminal reads in Cline | npm global |

### Tool-Specific Rules

| Tool | Rule |
|------|------|
| markitdown | Always run on incoming files before reading — agent reads .md, not binary. Government/ISO sites → use agent-browser first (403 otherwise) |
| caveman | Full at 60 turns (desktop) · ultra from message 1 (phone). Never modify code blocks, formulas, clause refs, or doc codes |
| graphify | Only for repos 30+ files — overhead not worth it below that |
| LeanCTX | `lean-ctx init --agent cline` — compresses terminal/file reads on Windows |
| repomix | One-shot snapshots for sharing codebase context to AI |

---

## ComplianceHub Infrastructure

| Component | Port | Stack | Notes |
|-----------|------|-------|-------|
| Backend | 8000 | FastAPI + python-docx + openpyxl | Always |
| Frontend | 5173 | React + Vite | Always |
| AI Router | — | OpenRouter → Groq → HuggingFace → Local Qwen3-4B → Offline | 8 free models |
| Design System | — | templates/DESIGN.md | red #C00000 + black — no blue, no hardcoded hex |

**Hard Constraints:**
- NEVER Firebase → `window.storage` only
- NEVER Excel as HTML blob → `window.XLSX.utils.aoa_to_sheet + writeFile`
- ALWAYS `sanitizeHtml()` before `dangerouslySetInnerHTML`
- ALWAYS `new AbortController()` per AI call
- ALWAYS `<ErrorBoundary>` wrapping `<App/>`
- NEVER `setAuditProjects` inside `.forEach` → accumulate then call once

---

## Gemini Gems Configuration

| Gem | Name | Model | Features | Knowledge Files |
|-----|------|-------|----------|-----------------|
| 1 | OWL Auditor | Pro 3.1 | Deep Research + Grounding | SOUL + CONTEXT + SKILLS + skills/AUDIT.md + clients/KSA-REGULATORY.md + templates/ |
| 2 | OWL Implementer | Pro 3.1 | Canvas + Deep Research | SOUL + CONTEXT + SKILLS + skills/IMPLEMENT.md + clients/ (MEDIUM only) |
| 3 | OWL KSA Lead | Pro 3.1 | Deep Research + Grounding | SOUL + CONTEXT + SKILLS + skills/IMPLEMENT.md + clients/KSA-REGULATORY.md |
| 4 | OWL Personal | Pro 3.1 | Deep Research | MEMORY.md only (no client data) |
| 5 | OWL Code | Pro 3.1 | Deep Research | SOUL + SKILLS + skills/DEV.md + templates/DESIGN.md |

**Gem coordination patterns:** 1→2→3 (audit→implement→KSA validate) · 3→2 (KSA requirements→implement) · 2→3 (Arabic doc→KSA validate) · 5→1 (code→compliance check) · 4 standalone (personal+board)

**Gem rules:** Never upload raw PDF/DOCX → always markitdown first. Never upload full SKILLS.md → split into domain files. Strip PUSH → "Work through this step by step".

---

## Client Routing — Projects vs Audit Clients

| Category | Clients | Formula Access | Platform Routing | Profile |
|----------|---------|----------------|------------------|---------|
| **Projects** | MSD-MOI, Al-Ahsa | Full · locked | HIGH → Claude/Cline/Hermes ONLY | Full `clients/<NAME>.md` |
| **Projects** | SAGCO + new | Full · locked | MEDIUM → all with PII scrub | `clients/<NAME>.md` from TEMPLATE |
| **Audit Clients** | Daily by calendar | No formulas | Varies → classify per client | One-line in CONTEXT.md |
| Archived | UACC, MOC | Locked · reference only | — | `clients/archive/` |

---

## Skills Registry (38 Active)

| # | Domain File | Skills |
|---|------------|--------|
| 1 | skills/AUDIT.md | 02, 07, 12, 14, 26, 27, 28 |
| 2 | skills/IMPLEMENT.md | 01, 03, 04, 05, 06, 09, 16, 20, 24, 25 |
| 3 | skills/DEV.md | 08, 11, 17, 38 |
| 4 | skills/SYSTEM.md | 01b, 15, 21, 22, 23, 29, 30, 31, 37, 39 |
| 5 | skills/PERSONAL.md | 10, 19, 32, 33, 34, 35 |
| — | Tombstoned | 13, 18 |

**Domain files split from SKILLS.md (v4.0):** 133KB → 4KB index + 5 domain files (~7KB each). 122KB saved per session.

---

## TÜV Austria Templates

14 standardized CB forms in `templates/tuv-austria/`. **NEVER modify — populate with client data only.**

| # | Form | Purpose | Code |
|---|------|---------|------|
| 1 | Audit Questionnaire (ISO 22301) | BCMS pre-audit questionnaire | Q01 |
| 2 | Audit Questionnaire (General) | General pre-audit questionnaire | Q02 |
| 3 | Manday Calculation | Audit duration determination | MD |
| 4 | Audit Plan (General) | Audit scheduling and scope | AP-IMS |
| 5 | Audit Plan (ISMS) | ISMS-specific audit plan | AP-ISMS |
| 6 | Audit Report (IMS) | Post-audit findings and recommendation | AR |
| 7 | Participation List | Audit attendee record | PL |
| 8 | Audit Checklist (ISO 27001) | Clause-by-clause evidence check | CL-ISMS |
| 9 | Audit Checklist (Combined) | QM/EMS/HSE clause evidence | CL-IMS |
| 10 | Certificate Text | Certificate wording | CERT |

**Population reference:** `templates/tuv-austria/POPULATION.md` — field maps, data sources, Projects vs Audit Clients modes, regulatory overlays, naming convention, confidence levels

---

## File Dependency Chain

**Minimum load (any platform):** SOUL.md → CONTEXT.md
**Full load (when task requires):** + AGENTS.md → SKILLS.md → MEMORY.md → TOOLS.md → PLATFORMS.md

**Client profiles loaded on demand:** Only load the relevant `clients/<NAME>.md` for the active client, never all at once.

---

_Last updated: 2026-08-09 · OWL v4.2 · Z.ai Agent/Chat/AutoClaw added_
