# MEMORY.md — Session State & Confirmed Preferences
_Version: 4.1 · August 2026 (restored from 07-08 original + enhancements)_

_See also: SOUL.md (identity) · AGENTS.md (roles) · SKILLS.md (SOPs) · PLATFORMS.md (platforms) · TOOLS.md (infrastructure)_

_Updated at session end via Skill 01b. Works on any AI model._

**Memory authority:** MEMORY.md is the **authoritative source** — overrides any conflicting auto-memory.

**Security:** ⚠️ NEVER load MEMORY.md in shared contexts — group chats, sessions with other people. Contains personal context.

---

## Confirmed Preferences

### Output & Formatting
- Direct output first — no preamble, no "Great question!", no filler
- Tables over bullet lists for structured data
- Inline code blocks for all formulas, commands, file paths
- English for technical work · Arabic MSA for client documents
- ISO clause refs always in English even inside Arabic documents
- Short sentences in client-facing documents — one idea per sentence
- Skill 22 Quality Gates before every client deliverable — no exceptions

### Code Preferences
- Python: modular scripts · `# --- CONFIG ---` at top · zero pyflakes errors
- Excel: openpyxl only · live Excel formulas · hidden `_Lists`/`_Data` sheets · A4 print · recalc.py after every build
- React/Frontend: Vite · ESLint clean · `npm run lint` + `npm run build` before delivery
- Word/Arabic: python-docx · explicit RTL bidi properties · `WD_ALIGN_PARAGRAPH.RIGHT`

### Token Pipeline (current platforms — August 2026)
- markitdown: convert ALL incoming files before reading — PDF/DOCX/PPTX/XLSX/URL
- LeanCTX: compress terminal reads in Cline (VS Code) — `lean-ctx init --agent cline`
- caveman: full at 60 turns on desktop · ultra from message 1 on phone
- Order: markitdown (inputs) → LeanCTX (terminal reads) → caveman (output)

### Working Habits (apply every session)
- Stack multiple asks into one message rather than five follow-ups
- To fix bad output: edit original prompt and regenerate — don't chase with incremental fixes
- Start fresh session when topic changes
- Default to free models for easy tasks — reserve heavy models for reasoning or client-facing
- Never combine audit findings and implementation solutions in same output
- If multiple things asked in one message, respond to each in order
- Be proactive — flag gaps without being asked
- Never assume which client — ask if ambiguous

### AI Behaviour (any model)
- Never simplify client formulas: V=S×(1−U/4) MOI · L×S SAGCO · L×I Al-Ahsa · Audit clients: no formulas (TÜV templates) · UACC (L×S) archived
- Client isolation mandatory — never cross-contaminate formulas, colours, vocabulary, doc codes
- Deliver complete files — no placeholders, no TBD, no half-finished sections
- Activate correct agent from AGENTS.md auto-trigger map without being asked

### Z.ai Mode Preferences
- **Z.ai Agent:** Use for multi-step reasoning, CAPA, stress-test, formula verification, Arabic doc drafting. Full OWL load.
- **Z.ai Chat:** Use for quick lookups, one-off analysis, brainstorming, formula spot-checks. Light load only.
- **AutoClaw:** Use for scheduled/recurring tasks. Never invoke manually — let cron trigger it.
- **Decision rule:** If it needs full OWL context + multiple steps → Agent. If it's one question → Chat. If it repeats → AutoClaw.

### Session Behaviour
- Load CONTEXT.md client data at start — identify active client before building
- Confirm client + track (A or B) before any deliverable
- Use Skill 01b at session end to log new preferences and decisions
- **Session sync:** Save state to `memory/YYYY-MM-DD.md` before leaving any platform

---

## Mistakes to Avoid

### Client & Formula Rules

| # | Mistake | Rule |
|---|---------|------|
| 1 | Mixing client formulas | Load from CONTEXT.md per client — never guess or reuse |
| 6 | Missing approval blocks | Every client doc needs filled approval block — blank = G1 gate failure |
| 9 | Mixed Arabic/English in one section | Language consistency is Quality Gate G5 |
| 10 | Wrong doc code prefix | SAGCO-IMS- · AHSA-ISMS- · MSD-MOI-GRC- · UACC-EnMS- · MOC-ABMS- |
| 14 | Producing Chinese output | OWL operates in English (technical) and Arabic MSA (client docs) only — never Chinese |
| 41 | Replacing OWL files with generic templates | OWL files contain domain-specific professional context. Never overwrite with generic/template versions. |

### Code & Build Rules

| # | Mistake | Rule |
|---|---------|------|
| 2 | Hardcoding Python values | All calculations = live Excel formulas — Python builds structure only |
| 3 | setAuditProjects inside forEach | Accumulate results first, call setAuditProjects ONCE after loop |
| 4 | Firebase imports in React | window.storage only — no Firebase ever |
| 33 | Bash fences with Windows paths | Match fence label to actual shell |

### Process & Quality Rules

| # | Mistake | Rule |
|---|---------|------|
| 7 | Phantom agent references | Only Agents 1–11 exist — check AGENTS.md roster |
| 8 | Skipping Quality Gates | Skill 22 before every client deliverable — no exceptions |
| 29 | Treating pasted prompt as reformat-and-stop | Reformat AND execute — don't just hand back restructured version |
| 30 | Burying Skill 15 inside general routing | Skill 15 is Layer 0 — mandatory FIRST check on every message |
| 34 | Confusing Agent 9, 11, and Skill 30 | Agent 9 = project gates. Agent 11 = message routing. Skill 30 = silent mechanism |
| 35 | Accepting external numbering without checking | Always check AGENTS.md/SKILLS.md current headers before accepting numbered proposals |
| 36 | Merging Skill 32 and Skill 33 | Status report vs decision debate — different triggers, different outputs |
| 37 | Building skill without checking overlap | Check TOOLS.md/SKILLS.md/AGENTS.md first — only build what's genuinely missing |
| 38 | Routing personal-voice to client agent | Skill 35 lives under Agent 6 — non-client only |
| 40 | Writing guide without wiring into index | Every new file must update README + TOOLS.md cross-refs + MEMORY.md session log |

### Token & Platform Rules

| # | Mistake | Rule |
|---|---------|------|
| 5 | Wrong API endpoint | OpenRouter: `openrouter.ai/api/v1`. Gemini: via Google AI Studio. Never hardcode provider endpoints. |
| 11 | graphify on small repos | Only for repos 30+ files — overhead not worth it below that |
| 12 | markitdown URL scraping | Government/ISO sites 403 — use agent-browser to fetch first |
| 13 | caveman mode persistence | Stays active until "normal mode" — no need to re-trigger each message |
| 15 | PUSH on non-Claude models | Strip PUSH → "Work through this step by step" on all platforms |
| 19 | Reading raw DOCX/PDF in agent | Always run markitdown first — agent reads .md, not binary |
| 20 | caveman on code blocks | caveman must never modify code blocks, formulas, clause refs, or doc codes |
| 22 | markitdown on government sites | Returns 403 — use agent-browser to fetch first, then markitdown |
| 31 | PUSH line on non-Claude models | All platforms → "Work through this step by step". DeepSeek/GLM → native reasoning mode |

### Gemini Gems Rules

| # | Mistake | Rule |
|---|---------|------|
| 23 | PUSH in Gemini Gems | Use "Work through this step by step" instead |
| 24 | Uploading raw PDF/DOCX to Gem | Always markitdown first → upload .md |
| 25 | Uploading full SKILLS.md to Gems | Split into topic files — full file too large for RAG |

---

## Client-Specific Patterns

### How Clients Work in OWL

**Two categories — different treatment:**

| Category | Who | Duration | Profile | Update Frequency |
|----------|-----|----------|---------|------------------|
| **Projects** | MSD-MOI, Al-Ahsa, SAGCO (+ new ones) | Weeks to years | Full `clients/<NAME>.md` file | When status changes |
| **Audit Clients** | Changes daily by calendar | 1–5 days | One-line entry in CONTEXT.md Audit Clients table | Every morning from calendar |
| Archived | UACC, MOC | Closed | Move to `clients/archive/` | On project close |

**Daily workflow:**
1. Morning: Check calendar → update CONTEXT.md Audit Clients table with today's audits → classify sensitivity per client
2. During work: Load project client from `clients/<NAME>.md` OR work audit client from CONTEXT.md
3. End of day: Archive completed audit entries, sync project status if changed

### Projects (Consultation & Implementation)

#### MSD-MOI (Active)
- Full Arabic MSA · ISO refs and Risk IDs in English only
- Formula: S=O×Q (latent) · V=S×(1−U/4) (residual)
- Visual: #004D26 headers · #C8A96E accents · #1A3A5C secondary · RTL layout
- Aligned to: DGA Qiyas · NCA ECC · NRC framework
- Active: Corporate Risk Register (146 entries) · BIA Workbook (30 processes) · BCP
- Sensitivity: HIGH (government, PDPL) — see PLATFORMS.md §3

#### SAGCO (Active — Stage 2 Pending)
- English technical
- Formula: L×S (OHS/Env) · L×S×R (Environmental Significance)
- HIRA methodology + Hierarchy of Controls + mandatory 30-day review on trigger events
- Stage 2 blockers: emergency drill · fire extinguisher inspection · Group A sign-off
- Dashboard: https://sagcodrv-ux.github.io/sagco-im/
- Prefix: SAGCO-IMS- · Visual: #1B3A4B / #E07B39
- Sensitivity: MEDIUM — PII scrub required for non-Claude platforms

#### Al-Ahsa Municipality (Active)
- Arabic MSA · ISO refs in English · NCA ECC aligned
- Formula: L×I (Risk Score) · Nested IF Risk Level
- Prefix: AHSA-ISMS- · Visual: #006400
- Sensitivity: HIGH (government, PDPL) — see PLATFORMS.md §3

### Audit Clients (Dynamic by Calendar)

Audit clients come and go based on Osama's calendar. **Do not create permanent profiles.**

**Today's audit clients** are tracked in the Audit Clients table in CONTEXT.md (updated daily from calendar).

**Quick-add format (one line per client):**
```markdown
| [Client Name] | [Standard] | [Stage 1/2/Surv] | [Date] | [Auditor] | [Notes] |
```

**For audit work, always:**
- Identify the client + standard at session start
- Apply correct doc code prefix (ask if not in CONTEXT.md)
- Use TÜV Austria CB templates from `templates/tuv-austria/`
- Follow audit package workflow: manday calc → questionnaire → plan → checklist → report → certificate
- Classify sensitivity (HIGH if government, MEDIUM if industrial) — affects platform routing

### Archived Clients

| Client | Standard | Prefix | Notes |
|--------|----------|--------|-------|
| UACC | ISO 50001 | UACC-EnMS- | Finished — English · EnMS vocabulary locked (SEU, EnPI, EnB, VFD, DCS, ALARM, SEEC) |
| MOC | ISO 37001 | MOC-ABMS- | Archived July 2026 · Arabic MSA |

---

## Active Platform Stack (August 2026)

| Platform | Role | Notes |
|---|---|---|
| VS Code + Cline | Terminal coding | Primary terminal · LeanCTX enabled |
| Qwen Studio | Web workspace | Primary web · 1M context |
| Qwen Coder | Free coding | Web + Android |
| Z.ai Agent | Agents, reasoning | GLM-5.2 · full OWL load |
| Z.ai Chat | Quick Q&A | GLM-5.2 · light load |
| AutoClaw | Automated workflows | 7 automations · cron-driven |
| Gemini Pro | Deep Research, 5 Gems | Paid · Gem 1-3 (audit/impl/KSA) · Gem 4 (personal) · Gem 5 (code) |
| Hermes Agent | Persistent agent | Windows · Telegram/WhatsApp |
| MiniMax | Free until limit | Quick queries |
| Xiaomi MiMo | OWL tasks | OpenClaw · 4hr/day free |
| Phone | Qwen, Z.ai, MiMo, DeepSeek, Claude, Gemini | Multi-app |

---

## Session Log
_Newest first._

### August 2026 — AI Provider Refresh + Agent Harness (08-16)
- Registry rewritten to 21 models: PREMIUM (premium_claude/claude-sonnet-5) + 7 FRONTIER + 8 STRONG + 2 GROQ + 3 LOCAL; Gemini dropped from doc-gen chain (chat-only) per Mistake #5
- Antigravity provider: key renamed antigravity_claude_sonnet_46 → premium_claude, model claude-sonnet-5 (retired -4-6)
- Fixed Groq tier dead: router._provider_has_key only recognized legacy 'groq' key, not groq_llama/groq_scout
- Added registry-driven /v1/models endpoint + MODELS_LIST to chat.py
- Full AI test suite green: 84 passed (router 46 + providers + chat)
- model_bench.py fixed (was broken: only benched openrouter, malformed dict) + verify_groq.py added
- Branding scrub: Osama/*.md red #C00000 + black only (no blue hexes) — synced from G: OWL-Complete workspace
- HARNESS.md created: portable agent bootstrap with 33 Cherny rules + memory table + model strip
- tasks/ second brain created: todo.md + lessons.md correction log
- Commits: 6671cc4 (provider refresh), e832672 (Groq fix + /v1/models, 84/84 green) — both pushed

### August 2026 — File Restoration (08-08)
- SOUL.md restored from 07-08 original: replaced Chinese security template with English domain-specific content
- SOUL.md enhanced: v3.1→v4.0 · added Quality Pipeline section · Law #14 (never Chinese) · skills 35→38 · Gemini 3→5 Gems · phone workflow
- AGENTS.md restored from 07-08 original: replaced generic OpenClaw template with 11-agent roster
- AGENTS.md enhanced: v4.0→v4.1 · MEMORY.md security note · Gemini 5 Gems in strip rules · Gem 4+5 trigger signals · Phone 6 apps
- CONTEXT.md restored from 07-08 original: added Platform routing, Audit Calendar, Visual Identity Summary, Gem→Client mapping
- CONTEXT.md fix: Accreditation changed from UKAS to SAAC (Saudi Accreditation) + Austrian Accreditation + Hellas Accrediting
- MEMORY.md restored from 07-08 original: 34→206+ lines · all preferences, mistakes, client patterns, session log recovered
- MEMORY.md enhanced: Client-Specific Patterns restructured → Consultation (stable) + Audit (dynamic, daily by calendar) + Archived
- MEMORY.md added mistakes #14 (no Chinese) and #41 (never replace OWL files with generic templates)
- Key lesson: 08-08 session incorrectly replaced domain-specific OWL files with generic templates — must not happen again

### August 2026 — OWL v4.0 Consolidation (07-08)
- Major platform consolidation: killed opencode, Cherry Studio, claude.ai configs
- Actual stack: Cline (VS Code), Qwen Studio, Z.ai, MiniMax, MiMo, Hermes Agent, Gemini Pro, Qwen Coder
- SOUL.md updated to v3.1: agent count fixed (9→11), platform stack updated, Law #4 reworded
- PLATFORMS.md rewritten: 46KB → 14KB. Merged PLATFORMS_RULES.md. Added Gemini activation plan (3 Gems), Hermes Agent setup, Qwen Coder guide, session sync protocol
- MEMORY.md pruned: 29KB → 10KB. Removed 12 dead mistakes, grouped remaining by category
- SKILLS.md split: 133KB → 4KB index + 5 domain files (~7KB each). 122KB saved per session
- TOOLS.md split: 61KB → 3KB. Install guides to docs/INSTALL_GUIDES.md
- CONTEXT.md simplified: 33KB → 3KB. Client profiles to clients/ folder. Quick-add template created
- Skills 37/38/39 integrated: Qwen Workspace, Code Review Gate (Alibaba OCR), PII Scrub & Route
- 8 OpenClaw skills mapped to OWL agents
- LeanCTX confirmed compatible with Cline: `lean-ctx init --agent cline`
- Session sync protocol: Hermes Agent cron jobs for daily digest + sync reminder
- Client model simplified: Audit clients (quick-add) + Consultation (full profile) + Finished (archived)
- Gemini Pro activation plan: 3 Gems (Auditor, Implementer, KSA Lead) with setup instructions
- AGENTS.md updated: 29KB → 12KB. Removed dead platform refs, updated Agent 3/7 tools, added Skills 37/38/39 to trigger map
- Dead platform guide files deleted (CHERRY_STUDIO, OPENCODE, GEMINI_GEMS, DEEPSEEK, QWEN_STUDIO, ZAI_ARENA, CLAUDE.md, GEMINI.md)
- Total token savings: ~78K tokens per session (90K → 12K baseline)
- Client data: all 4 clients have profiles (MSD-MOI, SAGCO, AL-AHSA active; UACC archived)
- ACTIVE_CLIENTS.md created for daily audit client tracking (one-line entries)
- SETUP.md created: complete platform setup guide for v4.0
- Hermes Agent: desktop application (not CLI) — setup guide in SETUP.md §6
- KSA regulatory layer expanded: PDPL (12 requirements, ISO 27701 mapping), DGA Qiyas V5.0 (8 dimensions, 5 maturity levels), SDAIA AI Ethics (7 principles), SDAIA GenAI Guidelines, NCA ECC (114 controls), SAMA CSF (6 domains), Etimad scoring
- clients/KSA-REGULATORY.md created: 15KB comprehensive reference with cross-framework integration maps
- Agent 10 updated: expanded auto-trigger, cross-framework integration table, reference to KSA-REGULATORY.md
- Gem 3 (KSA Lead) instructions updated: full PDPL/DGA/SDAIA coverage with specific control references
- docs/QWEN_PROJECTS.md created: 4 Projects with task rules, Hybrid Thinking triggers, Deep Research triggers
- TÜV Austria audit templates installed: 10 standardized CB forms in templates/tuv-austria/
- Audit package workflow defined: manday calculation → questionnaire → plan → checklist → report → certificate
- Templates are IMMUTABLE — never modify, always save as new file with client data
- PLATFORM_RULES.md v1.0 content integrated into PLATFORMS.md: prompt injection defense, hard token caps (60 turns/60K chars/5K per file), token pressure drop order, cross-client denial rule, API key echo protection

---
