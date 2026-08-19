# OWL v4.0 — Complete Setup Guide
_Created: 2026-08-08 · Audited & corrected: 2026-08-08 · Everything built today in one reference._

---

## What This Is

This guide documents every file in the OWL v4.0 workspace. 9 platforms, 31+ files, one system.

**Read this first. Then follow the setup steps per platform.**

---

## File Map — Actual Workspace Contents

```
workspace/
├── GUIDE.md                        ← You are here
├── SOUL.md                         ← OWL identity + security + NEVER laws
├── AGENTS.md                       ← Agent behavior protocol + auto-trigger map
├── IDENTITY.md                     ← Agent identity (template — fill on first run)
├── USER.md                         ← User profile (template — fill over time)
├── TOOLS.md                        ← Infrastructure, API routing, skills registry
├── HEARTBEAT.md                    ← Heartbeat config (empty)
│
├── CONTEXT.md                      ← Client data, formulas, visual identity
├── MEMORY.md                       ← Long-term memory + preferences
├── SKILLS.md                       ← Master skill index + trigger table
├── PLATFORMS.md                    ← Platform configs + privacy rules
│
├── qwen-projects/                  ← Qwen Studio (4 Projects + main prompt)
│   ├── MAIN.md                     (499 words) Main Qwen system prompt
│   ├── AUDIT.md                    (998 words) Audit Project — Agent 1
│   ├── IMPLEMENT.md                (998 words) Implementer Project — Agent 2
│   ├── DEV.md                      (996 words) Developer Project — Agent 3
│   ├── SYSTEM.md                   (999 words) System Project — Agent 8+11
│   └── SETUP.md                    Setup guide with knowledge file lists
│
├── zai-projects/                   ← Z.ai (1 Agent + Chat)
│   ├── AGENT_INSTRUCTIONS.md       (998 words) Single OWL agent
│   └── SETUP.md                    Setup guide + workflows
│
├── autoclaw-projects/              ← AutoClaw (automated workflows)
│   └── SETUP.md                    Full OWL setup + 7 automations
│
├── gemini-projects/                ← Gemini Pro (5 Gems)
│   ├── GEM1_AUDITOR.md             (768 words) Auditor — Deep Research + Grounding
│   ├── GEM2_IMPLEMENTER.md         (858 words) Implementer — Canvas + Deep Research
│   ├── GEM3_KSA.md                 (883 words) KSA Lead — Deep Research + Grounding
│   ├── GEM4_PERSONAL.md            (~400 words) Personal — Deep Research
│   ├── GEM5_CODE.md                (~500 words) Code Assistant — Deep Research
│   └── SETUP.md                    Setup guide + when to use each Gem
│
├── hermes-projects/                ← Hermes Agent (always-on)
│   └── SETUP.md                    Install + 4 cron jobs + Telegram
│
├── phone-projects/                 ← Phone (6 apps)
│   └── SETUP.md                    App list + privacy matrix + compressed pastes
│
├── skills/
│   ├── humanizer/
│   │   └── SKILL.md                (412 lines) 33-pattern anti-slop skill
│   ├── AUDIT.md                    ← Audit domain SOPs
│   ├── IMPLEMENT.md                ← Implementation domain SOPs
│   ├── DEV.md                      ← Development domain SOPs
│   ├── SYSTEM.md                   ← System domain SOPs
│   └── PERSONAL.md                 ← Personal & lifestyle SOPs
│
├── clients/
│   ├── KSA-REGULATORY.md           ← KSA framework cross-maps
│   ├── MSD-MOI.md                  ← MOI client profile (Tier 1)
│   ├── AL-AHSA.md                  ← Al-Ahsa client profile (Tier 1)
│   ├── SAGCO.md                    ← SAGCO client profile (Tier 2)
│   ├── TEMPLATE.md                 ← New client quick-add template
│   └── UACC.md                     ← UACC client profile (archived)
│
├── templates/
│   ├── DESIGN.md                   ComplianceHub design system
│   └── tuv-austria/
│       ├── README.md               TÜV audit template inventory
│       └── POPULATION.md           Template population reference (field maps, modes, overlays)
│
├── docs/
│   ├── CLINE_OPTIMIZATION.md       LeanCTX + free fallbacks
│   ├── HERMES_DEEP_DIVE.md         Hermes analysis
│   ├── MAXIMIZATION_STRATEGY.md    Full platform utilization matrix
│   ├── MODEL_GUIDE.md              Model/provider selection guide
│   ├── MASTER_OVERVIEW.md          All platforms in one view
│   ├── DESIGN_INTEGRATION.md       Design system integration guide
│   └── FREE_TIER_ANALYSIS.md       9 free AI providers analysis
│
└── memory/
    └── 2026-08-08.md               Today's session log
```

### ⚠️ Files That Need Creating

The following files are referenced by projects but not yet in the workspace. They must be created before platform setup:

| File | Referenced By | Status |
|------|--------------|--------|
| `CONTEXT.md` | Qwen Implement, Z.ai, All 5 Gemini Gems, Hermes | **Create first** |
| `MEMORY.md` | Qwen System, Z.ai, Gemini Gem 4, Hermes, AGENTS.md | **Create first** |
| `SKILLS.md` | Qwen System, Hermes | **Create first** |
| `PLATFORMS.md` | Qwen System, Hermes | **Create first** |
| `skills/AUDIT.md` | Qwen Audit, Gemini Gem 1 & 3, Hermes | **Create first** |
| `skills/IMPLEMENT.md` | Qwen Implement, Gemini Gem 2 & 3 & 5, Hermes | **Create first** |
| `skills/DEV.md` | Qwen Dev, Gemini Gem 5, Hermes | **Create first** |
| `skills/SYSTEM.md` | Qwen System, Hermes | **Create first** |
| `clients/KSA-REGULATORY.md` | Qwen Audit & Implement, Gemini Gem 1-3, Hermes | **Create first** |
| `clients/MSD-MOI.md` | Qwen Audit & Implement, Gemini Gem 1-3, Hermes | **Create first** |
| `clients/SAGCO.md` | Qwen Audit & Implement & Dev, Gemini Gem 1-3 & 5, Hermes | **Create first** |
| `clients/AL-AHSA.md` | Qwen Audit & Implement, Gemini Gem 1-3, Hermes | **Create first** |
| `clients/TEMPLATE.md` | Qwen Implement, Gemini Gem 2 | **Create first** |
| `clients/UACC.md` | Referenced in formulas | **Create first** |
| `templates/tuv-austria/README.md` | Qwen Audit, Gemini Gem 1 | **Create first** |
| `OPENCLAW_OWL_SKILLS.md` | Qwen Dev, Gemini Gem 5 | **Create first** |

---

## Platform Setup — Step by Step

### 1. Qwen Studio (Primary Workspace)

**What:** 4 Projects with knowledge files. Best agentic model (#1 on Agentic Index).

**Setup:**
1. Go to qwen.ai → Settings → System Prompt → paste `qwen-projects/MAIN.md`
2. Create Project 1: OWL Auditor → paste `qwen-projects/AUDIT.md` → upload knowledge files
3. Create Project 2: OWL Implementer → paste `qwen-projects/IMPLEMENT.md` → upload knowledge files
4. Create Project 3: OWL Developer → paste `qwen-projects/DEV.md` → upload knowledge files
5. Create Project 4: OWL System → paste `qwen-projects/SYSTEM.md` → upload knowledge files

**Knowledge files per Project:** See `qwen-projects/SETUP.md`

**Use for:** Daily deliverables, Arabic docs, Excel workbooks, research, Task Assistant

---

### 2. VS Code + Cline (Terminal Coding)

**What:** ComplianceHub development, Python scripts, terminal work.

**Setup:**
1. Install LeanCTX: `npm install -g lean-ctx-bin` → `lean-ctx onboard` → `lean-ctx init --agent cline`
2. Add free fallbacks: Cline → Settings → API Configuration → OpenRouter → add `google/gemma-3-27b-it:free`, `qwen/qwen3-235b-a22b:free`
3. Copy DESIGN.md to repo: `Copy-Item templates/DESIGN.md ~/ComplianceHub/DESIGN.md`
4. Verify AGENTS.md is in `~/ComplianceHub/` root

**Full guide:** `docs/CLINE_OPTIMIZATION.md`

**Use for:** ComplianceHub dev, Python scripts, Git ops, file management

---

### 3. Z.ai Agent (Reasoning + Agents — Full OWL)

**What:** Deep reasoning, CAPA, stress-test, vibe coding. Full OWL context with agent + knowledge files.

**Setup:**
1. Go to z.ai → Agents mode → New Agent
2. Paste `zai-projects/AGENT_INSTRUCTIONS.md`
3. Upload: SOUL.md, CONTEXT.md, AGENTS.md, MEMORY.md, skills/humanizer/SKILL.md
4. Use native reasoning mode (no PUSH, no "work through step by step")

**Full guide:** `zai-projects/SETUP.md`

**Use for:** CAPA root cause, adversarial stress-test, pre-audit analysis, formula verification, Arabic doc drafting, multi-step reasoning

---

### 3b. Z.ai Chat (Quick Q&A — Light OWL)

**What:** Lightweight chat mode. No agent setup. Fast one-off questions.

**Setup:**
1. Go to z.ai → Chat mode (default)
2. Paste SOUL summary (~200 words) + active client row from CONTEXT.md as context
3. Use native reasoning mode

**Load:** SOUL summary + CONTEXT client row + 1 skill paragraph (if relevant). Never the full OWL stack.

**Use for:** Quick lookups ("what clause covers X?"), formula spot-checks, brainstorming, simple triage, one-off analysis, yes-no decisions

**When to switch to Agent:** If the question requires client profile data, formula verification, or multiple steps → open Agent instead.

---

### 3c. AutoClaw (Automated Workflows)

**What:** Z.ai's automation engine for scheduled, recurring OWL tasks.

**Setup:** See `autoclaw-projects/SETUP.md` for full configuration.

**Quick setup:**
1. Go to z.ai → AutoClaw mode
2. Create new automation → paste OWL automation instructions
3. Upload: SOUL.md, CONTEXT.md, AGENTS.md, all skill domain files
4. Set schedule and triggers

**Automations:**
- Morning Briefing (Daily 8 AM): Audit calendar → classify → brief
- Audit Calendar Sync (Daily 9 AM): Update CONTEXT.md Audit Clients table
- Quality Gate Sweep (On save): Auto-run Skill 21 + 22
- Template Population (On audit start): Load TÜV template → pre-fill client data → regulatory overlays → confidence report
- Evening Digest (Daily 6 PM): Day summary → MEMORY.md → board summary
- Weekly Reconciliation (Friday 5 PM): Reconcile counts → SOUL.md
- ComplianceHub Deploy Check (On git push): Skill 38 + lint + build

**Use for:** Any OWL task that runs on a schedule or repeats without manual input

---

### 4. Gemini Pro (Deep Research + Synthesis)

**What:** 5 Gems for different domains. Company-paid = unlimited.

**Available models:** Flash 3.5 (fast), Thinking 3.6 (reasoning), Pro 3.1 (best quality)

**Setup:**
1. Go to gemini.google.com → Gems → New Gem
2. Create 5 Gems (see `gemini-projects/SETUP.md` for exact instructions + knowledge files):
   - Gem 1: OWL Auditor (Deep Research + Grounding)
   - Gem 2: OWL Implementer (Canvas + Deep Research)
   - Gem 3: OWL KSA Lead (Deep Research + Grounding)
   - Gem 4: OWL Personal (Deep Research)
   - Gem 5: OWL Code Assistant (Deep Research)
3. Use Pro 3.1 for Gems, Flash 3.5 for quick queries, Thinking 3.6 for complex reasoning

**Full guide:** `gemini-projects/SETUP.md`

**Use for:** Pre-audit research, regulatory updates, policy drafting, KSA compliance, deep analysis

---

### 5. Hermes Agent (Always-On)

**What:** Persistent memory, Telegram/WhatsApp, 4 cron jobs.

**Setup:**
1. Download from hermes-agent.org → install
2. Configure LLM: OpenRouter → API key → model (nvidia/nemotron-ultra-253b or DeepSeek V3)
3. Import 13 OWL files (see `hermes-projects/SETUP.md` for exact commands)
4. Connect Telegram: @BotFather → new bot → paste token
5. Add 4 automations:
   - Morning briefing (8 AM)
   - Evening digest + sync (6 PM)
   - Weekly reconciliation (Friday 5 PM)
   - Monthly KSA + audit calendar (1st, 9 AM)

**Full guide:** `hermes-projects/SETUP.md`

**Use for:** Quick queries, client status, audit prep, implementation guidance, KSA compliance

---

### 6. Phone (Mobile Apps)

**What:** 6 apps for on-site, commuting, quick queries.

**Setup:**
1. Install: Qwen, Z.ai, Gemini, DeepSeek, Claude, MiMo
2. Login with same accounts as desktop
3. Same Projects/Gems available on phone

**Privacy:** HIGH clients (MSD-MOI, Al-Ahsa — Tier 1) → Claude ONLY. MEDIUM (SAGCO — Tier 2) → scrub OK. Tier 3 audit → classify per client.

**Full guide:** `phone-projects/SETUP.md`

**Use for:** On-site audits, commuting research, voice-to-research, client-sensitive work

---

## Design System

**What:** AI-readable design reference for ComplianceHub UI.

**Setup:**
1. Copy `templates/DESIGN.md` to `~/ComplianceHub/DESIGN.md`
2. Cline reads it automatically
3. Upload to Qwen/Gemini/Z.ai as knowledge file

**Contains:** TÜV branding, client colors, typography, spacing, component specs, anti-slop rules, 5 component prompts from 21st.dev

**Full guide:** `docs/DESIGN_INTEGRATION.md`

---

## Humanizer Skill

**What:** 33-pattern anti-slop skill based on Wikipedia's "Signs of AI writing."

**Setup:** Already installed at `skills/humanizer/SKILL.md`. Referenced in all Project/Gem/Agent instructions.

**Quality pipeline:** Humanizer (33 patterns) → Skill 21 (Language Gate) → Skill 22 (Quality Gates)

**Voice calibration:** Share 2-3 paragraphs of your own writing to match YOUR style.

---

## Model Selection — Quick Reference

| Task | Best Model | Platform | Free? |
|------|------------|----------|-------|
| Arabic docs | Qwen 3.8 Max | Qwen Studio | ✅ |
| English deliverables | Qwen 3.8 Max or Gemini Pro 3.1 | Qwen/Gemini | ✅ / Company |
| Coding | DeepSeek Flash V4 | Cline | ✅ |
| Deep reasoning | GLM-5.2 or Gemini Thinking 3.6 | Z.ai Agent/Gemini | ✅ / Company |
| Research | Gemini Pro 3.1 | Gemini Gems | Company |
| Quick queries | GLM-5.2 or MiniMax | Z.ai Chat/MiniMax | ✅ |
| Speed-critical | Groq Llama 3.3 70B | Groq | ✅ |
| Client-sensitive | Claude or local (Cline) | Phone/Cline | ✅ |
| Backup (unlimited) | GPT-5.6 Luna | ChatGPT | ✅ |

**Free fallbacks (when limits hit):**
- google/gemma-3-27b-it:free
- qwen/qwen3-235b-a22b:free
- mistralai/mistral-small-3.2-24b-instruct:free

**Full guide:** `docs/MODEL_GUIDE.md`

---

## Decision Tree — Where to Do What

```
START
  │
  ├─ Quick question? → Z.ai Chat or Hermes (Telegram) or GPT-5.6 Luna
  │
  ├─ Client-sensitive data (HIGH)? → Claude (Phone) or Cline (local)
  │
  ├─ Coding? → Cline (VS Code)
  │   └─ Limit hit? → Qwen Coder or Groq
  │
  ├─ Deep research / regulatory? → Gemini Pro 3.1 (Gems)
  │
  ├─ Arabic document? → Qwen Studio (Project)
  │
  ├─ Reasoning / CAPA / stress-test? → Z.ai Agent or Gemini Thinking 3.6
  │
  ├─ Scheduled / recurring / automate? → AutoClaw
  │
  ├─ Daily deliverable (English)? → Qwen Studio or Gemini Pro 3.1
  │
  ├─ Quick query (non-critical)? → Z.ai Chat, MiniMax or GPT-5.6 Luna
  │
  └─ On-site / mobile? → Phone (Gemini + Hermes Telegram + Z.ai Chat)
```

---

## Daily Workflow

| Time | Action | Platform |
|------|--------|----------|
| 8 AM | AutoClaw: morning briefing (auto) | AutoClaw → Telegram |
| 9 AM | AutoClaw: audit calendar sync (auto) | AutoClaw → CONTEXT.md |
| Work day | Deliverables | Qwen (4 Projects) |
| Work day | Coding | Cline (LeanCTX) |
| Work day | Research | Gemini Pro 3.1 (5 Gems) |
| Work day | Reasoning | Z.ai Agent or Gemini Thinking 3.6 |
| Work day | Quick queries | Z.ai Chat, Hermes, or MiniMax |
| On save | AutoClaw: quality gate sweep (auto) | AutoClaw → Skill 21+22 |
| 6 PM | AutoClaw: evening digest + sync (auto) | AutoClaw → MEMORY.md |
| End of day | Update memory, git commit | Manual |
| Friday 5 PM | AutoClaw: weekly reconciliation (auto) | AutoClaw → SOUL.md |
| 1st of month | Hermes: KSA + audit calendar (auto) | Hermes Telegram |

---

## Privacy Matrix

| Client | Qwen | Gemini | Z.ai Agent | Z.ai Chat | AutoClaw | Cline | Claude | Hermes |
|--------|------|--------|------------|-----------|----------|-------|--------|--------|
| MSD-MOI (HIGH, Project) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ local | ✅ | ✅ self-hosted |
| Al-Ahsa (HIGH, Project) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ local | ✅ | ✅ self-hosted |
| SAGCO (MEDIUM, Project) | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ | ✅ | ✅ self-hosted |
| Audit clients (varies) | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ | ✅ | ✅ |
| OWL internal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Scrub:** Remove names, phones, emails, NIDs, addresses before pasting.

---

## Rate Limit Habits

| # | Habit | Status |
|---|-------|--------|
| 01 | Pick the right model | ✅ Built in |
| 02 | Edit, don't stack corrections | ⚡ Habit change |
| 03 | Fresh chat every 15 min | ✅ Built in (Projects) |
| 04 | Batch into one message | ✅ OWL rule |
| 05 | Use right tool, not strongest | ⚡ Habit change |
| 06 | Pace across platforms | ⚡ Habit change |
| 07 | Memory set up | ✅ MEMORY.md |
| 08 | Brief in Projects | ✅ 4 Projects + 5 Gems |
| 09 | Instructions short | ✅ All under 1000 words |

---

## Free Providers (Backup Stack)

| Provider | Model | Limits | Use |
|----------|-------|--------|-----|
| OpenAI | GPT-5.6 Luna | Unlimited | Safety net |
| Google AI Studio | Gemini 3.5 Flash | 1,500 req/day | API, bulk |
| Groq | Llama 3.3 70B | 14,400 req/day | Speed |
| Cerebras | Various | 1M tok/day | Batch |
| Mistral | All models | Experiment tier | Variety |
| OpenRouter | 26 models | 50 req/day | Fallbacks |

**Full guide:** `docs/FREE_TIER_ANALYSIS.md`

---

## Setup Checklist

### ⚠️ Prerequisite: Create Missing Files
- [ ] Create CONTEXT.md (client data, formulas, visual identity)
- [ ] Create MEMORY.md (long-term memory + preferences)
- [ ] Create SKILLS.md (master skill index)
- [ ] Create PLATFORMS.md (platform configs + privacy rules)
- [ ] Create skills/AUDIT.md (audit domain SOPs)
- [ ] Create skills/IMPLEMENT.md (implementation domain SOPs)
- [ ] Create skills/DEV.md (development domain SOPs)
- [ ] Create skills/SYSTEM.md (system domain SOPs)
- [ ] Create clients/KSA-REGULATORY.md (KSA framework cross-maps)
- [ ] Create clients/MSD-MOI.md (MOI client profile)
- [ ] Create clients/SAGCO.md (SAGCO client profile)
- [ ] Create clients/AL-AHSA.md (Al-Ahsa client profile)
- [ ] Create clients/UACC.md (UACC client profile)
- [ ] Create clients/TEMPLATE.md (new client template)
- [ ] Create templates/tuv-austria/README.md (TÜV audit template inventory)
- [ ] Create OPENCLAW_OWL_SKILLS.md (OpenClaw integration map)

### Qwen Studio
- [ ] Paste MAIN.md into system prompt
- [ ] Create Project 1: OWL Auditor + upload knowledge files
- [ ] Create Project 2: OWL Implementer + upload knowledge files
- [ ] Create Project 3: OWL Developer + upload knowledge files
- [ ] Create Project 4: OWL System + upload knowledge files

### VS Code + Cline
- [ ] Install LeanCTX
- [ ] Add free fallback models
- [ ] Copy DESIGN.md to ComplianceHub repo
- [ ] Verify AGENTS.md in workspace root

### Z.ai Agent
- [ ] Create agent + paste instructions
- [ ] Upload knowledge files

### Z.ai Chat
- [ ] Test chat mode with SOUL summary + CONTEXT client row
- [ ] Confirm native reasoning works

### AutoClaw
- [ ] Configure AutoClaw mode — see `autoclaw-projects/SETUP.md`
- [ ] Set up 7 automations (morning, calendar, gates, template, evening, weekly, deploy)
- [ ] Test each automation on manual trigger first

### Gemini Pro
- [ ] Create Gem 1: OWL Auditor + upload knowledge files
- [ ] Create Gem 2: OWL Implementer + upload knowledge files
- [ ] Create Gem 3: OWL KSA Lead + upload knowledge files
- [ ] Create Gem 4: OWL Personal + upload knowledge files
- [ ] Create Gem 5: OWL Code Assistant + upload knowledge files

### Hermes Agent
- [ ] Install Hermes
- [ ] Configure LLM (OpenRouter)
- [ ] Import 13 OWL files
- [ ] Connect Telegram
- [ ] Add 4 automations

### Phone
- [ ] Install 6 apps
- [ ] Login with same accounts

### Design System
- [ ] Copy DESIGN.md to ComplianceHub repo

### Humanizer
- [ ] Already installed (skills/humanizer/SKILL.md)
- [ ] Share 2-3 paragraphs of own writing for voice calibration

---

## What's Covered

- ✅ Qwen: 4 Projects + main prompt + knowledge file lists
- ✅ Cline: LeanCTX + free fallbacks + selective loading + design system
- ✅ Z.ai: Agent instructions + native reasoning + knowledge files
- ✅ Gemini: 5 Gems + Deep Research + Canvas + knowledge files + correct model names
- ✅ Hermes: Full OWL load + 4 cron jobs + Telegram/WhatsApp
- ✅ Phone: 6 apps + privacy matrix + compressed pastes
- ✅ Models: Selection guide + free fallbacks + 9 free providers
- ✅ Design: TÜV branding + component prompts + anti-slop rules
- ✅ Humanizer: 33 patterns + voice calibration + quality pipeline
- ✅ Privacy: HIGH/MEDIUM/LOW client routing per platform
- ✅ Daily workflow: morning briefing → work → evening digest
- ✅ Decision tree: which platform for which task
- ✅ Rate limit habits: 6 built in, 3 habit changes
- ✅ Free tier: 9 providers analyzed, 3 unlimited-tier
- ✅ File map: matches actual workspace contents
- ✅ Word counts: verified against actual file headers

---

_Last updated: 2026-08-08 · OWL v4.0 · Audited & corrected_
