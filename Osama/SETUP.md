# SETUP.md — OWL v4.0 Complete Platform Setup Guide
_Follow this once after the v4.0 update. Then forget it — everything just works._

---

## Step 1: Workspace Structure (Already Done)

Your files are now organized as:

```
~/.openclaw/workspace/
├── SOUL.md              ← Identity + 13 NEVER laws (always load first)
├── AGENTS.md            ← 11 agents + auto-trigger map (always load second)
├── CONTEXT.md           ← Client index + formulas (always load third)
├── MEMORY.md            ← Preferences + mistakes (always load fourth)
├── SKILLS.md            ← Trigger table + domain file index (load per task)
├── PLATFORMS.md         ← All platform configs + privacy rules + setup guides
├── TOOLS.md             ← Your specifics only (cameras, SSH, voices)
├── USER.md              ← Personal facts about Osama
├── OPENCLAW_OWL_SKILLS.md ← OpenClaw ↔ OWL integration map
├── SETUP.md             ← This file
├── skills/
│   ├── AUDIT.md         ← Skills 02,07,12,14,26,27,28
│   ├── IMPLEMENT.md     ← Skills 03,04,05,06,09,16,20,24,25
│   ├── DEV.md           ← Skills 08,11,17,38
│   ├── SYSTEM.md        ← Skills 01,01b,15,21,22,23,29,30,31,37,39
│   └── PERSONAL.md      ← Skills 10,19,32,33,34,35,36
├── clients/
│   ├── TEMPLATE.md      ← Quick-add template for new clients
│   ├── ACTIVE_CLIENTS.md ← All active clients in one file (daily use)
│   ├── MSD-MOI.md       ← Full consultation client profile
│   ├── SAGCO.md         ← Full consultation client profile
│   ├── AL-AHSA.md       ← Full consultation client profile
│   └── archive/
│       └── UACC.md      ← Finished project
├── templates/
│   └── tuv-austria/       ← 10 TÜV Austria CB audit templates (IMMUTABLE)
│       ├── README.md      ← Template inventory + audit package workflow
│       ├── 01-Audit-Questionnaire-ISO22301.docx
│       ├── 02-Audit-Questionnaire-General.docx
│       ├── 03-Manday-Calculation.docx
│       ├── 04-Audit-Plan-General.docx
│       ├── 05-Audit-Plan-ISMS.docx
│       ├── 06-Audit-Report-IMS.docx
│       ├── 07-Participation-List.docx
│       ├── 08-Audit-Checklist-ISO27001.xlsx
│       ├── 09-Audit-Checklist-Combined-QM-EM-HSE.docx
│       └── 10-Certificate-Text.docx
├── docs/
│   └── INSTALL_GUIDES.md ← Tool setup instructions
└── .learnings/
    ├── LEARNINGS.md     ← Self-improvement log
    ├── ERRORS.md        ← Error log
    └── FEATURE_REQUESTS.md
```

---

## Step 2: Qwen Studio Setup

This is your primary web workspace.

### 2.1 Load OWL Files

1. Go to **qwen.ai** → New Conversation
2. Upload these files as knowledge (or paste as system prompt):

**Minimum (every session):**
- SOUL.md
- CONTEXT.md

**Full (complex tasks):**
- AGENTS.md
- MEMORY.md
- relevant domain file from `skills/`

### 2.2 Set System Prompt

Paste this into Qwen Studio system prompt settings:

```
You are OWL — Osama's Work Layer. Work through this step by step.
- Direct output, no preamble, no filler
- Tables over bullets for structured data
- English for technical work, Arabic MSA for client documents
- ISO clause refs always in English even inside Arabic docs
- Client formulas: V=S×(1−U/4) MOI · L×S UACC/SAGCO · L×I Al-Ahsa
- Never deliver placeholders or TBD
- Skill 22 Quality Gates before every client deliverable
```

### 2.3 Task Assistant (100-doc parallel)

When batch processing multiple client documents:
1. Upload all files to Task Assistant
2. Give it the conversion task (e.g., "Convert all PDFs to markdown using markitdown format")
3. Download results → use in your main session

### 2.4 Hybrid Thinking Mode

- **Standard:** Quick queries, simple tasks
- **Hybrid Thinking:** Audit analysis, CAPA root cause, formula verification, Arabic drafting
- **Deep Research:** Pre-audit briefs, regulatory updates, multi-source synthesis

### 2.5 Gems (3 to Build)

Follow PLATFORMS.md §6 for setup. Quick version:

| Gem | Name | Purpose |
|---|---|---|
| Gem 1 | OWL Auditor | Pre-audit research, gap analysis, audit reports |
| Gem 2 | OWL Implementer | Client docs, risk registers, BIA, BCM |
| Gem 3 | OWL KSA Lead | NCA ECC, SAMA CSF, Etimad, Saudi regulatory |

Each Gem gets: SOUL.md + CONTEXT.md as knowledge, domain-specific instructions.

---

## Step 3: VS Code + Cline Setup

Your primary terminal coding agent.

### 3.1 OWL Files in Workspace

```powershell
# Copy OWL files to ComplianceHub workspace (so Cline can read them)
Copy-Item ~/.openclaw/workspace/SOUL.md ~/ComplianceHub/
Copy-Item ~/.openclaw/workspace/AGENTS.md ~/ComplianceHub/
Copy-Item ~/.openclaw/workspace/CONTEXT.md ~/ComplianceHub/
Copy-Item ~/.openclaw/workspace/MEMORY.md ~/ComplianceHub/
Copy-Item -Recurse ~/.openclaw/workspace/skills/ ~/ComplianceHub/skills/
```

### 3.2 LeanCTX

```powershell
# In VS Code integrated terminal (PowerShell)
npm install -g lean-ctx-bin
lean-ctx onboard
lean-ctx init --agent cline
lean-ctx init powershell | Add-Content $PROFILE

# Verify
lean-ctx doctor    # all green = good
lean-ctx gain      # see savings
```

### 3.3 Cline Project Rules

Cline reads `AGENTS.md` as project rules automatically. No extra config needed.

---

## Step 4: Z.ai Setup

Your reasoning + agent platform.

### 4.1 Load OWL Files

1. Go to **z.ai** → Agents mode
2. Create agent or paste as instructions:

```
You are OWL — Osama's Work Layer.
Use your native reasoning mode.
- Direct output, no filler
- Tables over bullets
- English for technical, Arabic MSA for client docs
- Client formulas: V=S×(1−U/4) MOI · L×S UACC/SAGCO · L×I Al-Ahsa
```

3. Upload relevant files as knowledge

### 4.2 Phone (Z.ai App)

Same agent works on Z.ai phone app. Use for:
- Quick reasoning tasks
- Vibe coding
- Agent-based workflows

---

## Step 5: Gemini Pro Setup (Paid — Maximize It)

### 5.1 Build 3 Gems

Go to gemini.google.com → Gems → New Gem

**Gem 1 — OWL Auditor:**
- Instructions: See PLATFORMS.md §6
- Knowledge: SOUL.md, CONTEXT.md
- Enable: Deep Research, Web Search, Grounding

**Gem 2 — OWL Implementer:**
- Instructions: See PLATFORMS.md §6
- Knowledge: SOUL.md, CONTEXT.md, relevant client files
- Enable: Canvas, Deep Research

**Gem 3 — OWL KSA Lead:**
- Instructions: See PLATFORMS.md §6
- Knowledge: SOUL.md, CONTEXT.md, `clients/KSA-REGULATORY.md`
- Enable: Deep Research, Grounding

**Gem 3 Detailed Instructions (paste into Gemini):**
```
You are OWL — Osama's Work Layer. KSA ISO & Compliance Lead.
Work through this step by step.

Cover ALL KSA regulatory frameworks:
- NCA ECC (114 controls, 5 domains: Governance, Defense, Resilience, Third-Party, ICS)
- SAMA CSF (6 domains: Governance, Risk, Operations, Resilience, Third-Party, M&A)
- PDPL (PIA mandatory, DPO mandatory, 72hr breach notify, cross-border restrictions, consent management, data subject rights)
- DGA Qiyas V5.0 (8 dimensions: Strategy, Infrastructure, Services, Data, Cyber, AI, Talent, Innovation — 5 maturity levels)
- SDAIA AI Ethics (7 principles: Fairness, Accountability, Transparency, Safety, Sustainability, Privacy, Human Oversight)
- SDAIA GenAI Guidelines (government entity use of generative AI)
- Vision 2030 (sustainability, energy targets, Saudization, PIF portfolio)
- Etimad scoring (ISO weight: 9001/45001/27001 ⭐⭐⭐⭐⭐, 14001/50001 ⭐⭐⭐⭐, 22301/42001 ⭐⭐⭐)

Cross-framework integration:
- PDPL × ISO 27701: Art.5→A.5.34, Art.12→§7.3, Art.20→A.5.24
- DGA × ISO 27001: Strategy→§5.1, Cyber→A.5–A.8, Data→A.5.12
- SDAIA × ISO 42001: Ethics→§5.2, Risk→§6.1.2, Inventory→A.3.2, Oversight→A.6.2
- NCA ECC × ISO 27001: 114 controls map to Annex A + §5–§7

Always reference specific controls (e.g., NCA ECC 1-1-1, PDPL Art.20, ISO 27001 A.5.24).
Include version numbers and effective dates when citing regulations.
Align all recommendations to Saudi Vision 2030 where applicable.

For AI systems: assess against SDAIA AI Ethics Principles + ISO 42001 + PDPL Art.11 (automated decisions).
For government clients: mandatory NCA ECC + DGA Qiyas + PDPL compliance.
For financial clients: mandatory SAMA CSF + PDPL compliance.
For industrial clients: mandatory Vision 2030 + MOL requirements.
```

### 5.2 Gemini on Android

Same 3 Gems work on Gemini Android app. Use for:
- On-site audit questions (voice-to-research)
- Mobile document review
- Deep Research while mobile

### 5.3 When to Use Gemini vs Qwen

| Use Gemini For | Use Qwen For |
|---|---|
| Deep Research (multi-source synthesis) | Long context work (1M) |
| Google Workspace integration | Arabic document quality |
| Drive-synced knowledge base | Task Assistant (100-doc parallel) |
| Android quick queries | Desktop web workspace |

---

## Step 6: Hermes Agent Setup (Desktop App)

### 6.1 Install

1. Download from **hermes-agent.org** → Windows installer
2. Run installer → follow wizard
3. Launch Hermes Agent from Start Menu

### 6.2 Configure LLM

In Hermes Agent settings:
- Provider: **OpenRouter**
- API Key: Your `OPENROUTER_API_KEY` (from ComplianceHub `.env`)
- Model: `nvidia/nemotron-ultra-253b` (free) or any OpenRouter model

### 6.3 Load OWL Context

In Hermes Agent, import your OWL files:
1. Settings → Memory → Import
2. Select: SOUL.md, CONTEXT.md, AGENTS.md
3. Hermes remembers these across all sessions

### 6.4 Connect Telegram

1. Message @BotFather on Telegram → `/newbot` → get token
2. In Hermes: Settings → Channels → Telegram → paste token
3. Enable Telegram channel
4. Test: send "What's the SAGCO risk formula?" to your bot

### 6.5 Connect WhatsApp (Optional)

1. In Hermes: Settings → Channels → WhatsApp
2. Scan QR code with your WhatsApp
3. Test: send a message to the connected number

### 6.6 Set Up Daily Automation

In Hermes Agent → Automations → New:

**Daily Digest (6 PM):**
```
Check today's git log. Summarize what was committed.
If nothing was committed, remind me to save my work.
```

**Sync Reminder (8 PM):**
```
Did you sync today's work to the repo?
Check memory/YYYY-MM-DD.md for what happened today.
```

**Morning Briefing (8 AM):**
```
What's on my calendar today?
Any pending client deliverables?
Any overdue CAPA items?
```

---

## Step 7: MiniMax / Xiaomi MiMo Setup

### 7.1 MiniMax

- Web: minimax.chat → free until daily limit
- Use for: quick queries, drafts, non-client work
- No OWL file loading needed — use for speed, not depth

### 7.2 Xiaomi MiMo (OpenClaw)

- Already running on this server
- 4 hours/day free
- Use for: OWL-related tasks, general queries
- OWL files already in workspace — auto-loaded

---

## Step 8: Phone Setup

### 8.1 Install These Apps

| App | Use Case |
|---|---|
| **Qwen** | Primary — general, documents, vibe coding |
| **Z.ai** | Agents, coding, reasoning |
| **Xiaomi MiMo** | General, OWL tasks |
| **DeepSeek** | Confirmation of outputs |
| **Claude** | Client-sensitive data only |
| **Gemini** | Deep Research, Gems, general |

### 8.2 Phone Workflow

1. Open relevant app
2. Paste compressed summary (not full OWL files)
3. caveman ultra from message 1
4. For client-sensitive work: Claude phone only

### 8.3 Phone Context Budget

~4K–8K tokens. Paste only:
- Active client entry from CONTEXT.md
- Task description
- One skill paragraph from relevant domain file

---

## Step 9: Client Data Entry (Daily Workflow)

### 9.1 New Audit Client (Most Common)

For short-term audit engagements — one line, no separate file:

1. Open `clients/ACTIVE_CLIENTS.md`
2. Add a row to the Audit Clients table:

```
| [Client Name] | [ISO Standard] | [Stage 1/2/Surv] | [Date] | [Notes] |
```

Done. Takes 10 seconds.

### 9.2 New Consultation Client (Rare)

For long-term implementation engagements:

1. Copy `clients/TEMPLATE.md` → `clients/<CLIENT-NAME>.md`
2. Fill in: formula, doc code prefix, visual identity, language
3. Add entry to `clients/ACTIVE_CLIENTS.md` Consultation table
4. Add entry to `CONTEXT.md` Active Clients table

### 9.3 End-of-Day Update

At end of each workday:
1. Update `clients/ACTIVE_CLIENTS.md` if any client status changed
2. Write `memory/YYYY-MM-DD.md` with what you did
3. Hermes Agent sends reminder at 8 PM if you forgot

---

## Step 10: Session Sync Protocol

### 10.1 Before Leaving Any Platform

```
Write to memory/YYYY-MM-DD.md:
- Platform: [where you worked]
- Client: [which client]
- Tasks: [what you did]
- Deliverables: [files produced]
- Decisions: [anything decided]
- Next: [what's pending]
```

### 10.2 Git Commit

```powershell
git add -A
git commit -m "session: YYYY-MM-DD <summary>"
```

### 10.3 Hermes Automation

Hermes Agent handles reminders automatically:
- 6 PM: daily digest
- 8 PM: sync reminder

### 10.4 Weekly Reconciliation (Friday)

Compare repo state vs actual deliverables:
```powershell
git log --oneline --since="1 week ago"
```
Flag anything missing.

---

## Quick Reference: What to Load Where

| Platform | Load These | Skip These |
|---|---|---|
| **Qwen Studio** | SOUL + CONTEXT + relevant domain file | Full AGENTS.md, full MEMORY.md |
| **Cline (VS Code)** | AGENTS.md (auto) + relevant domain file | PLATFORMS.md, docs/ |
| **Z.ai** | SOUL + CONTEXT | Full SKILLS.md |
| **Gemini Gems** | SOUL + CONTEXT (as knowledge) | Everything else (Gems have own instructions) |
| **Hermes Agent** | SOUL + CONTEXT + AGENTS (import once) | Domain files (Hermes has own skills) |
| **Phone** | Compressed summary only | All full files |

---

## Token Budget Per Platform

| Platform | Context Window | OWL Baseline | Free for Work |
|---|---|---|---|
| Qwen Studio (3.7-Max) | 1M | ~15K | **985K (98.5%)** |
| Gemini Pro | 1M+ | ~15K | **985K+** |
| Z.ai | 128K–1M | ~15K | **113K–985K** |
| Cline + LeanCTX | ~600K–2M | ~15K | **585K–1.985M** |
| MiniMax | Varies | ~15K | Varies |
| Phone | ~4K–8K | ~2K (compressed) | **2K–6K** |

---

_Last updated: 2026-08-07 · OWL v4.0_
