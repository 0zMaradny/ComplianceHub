# Z.ai Setup Guide — OWL v4.2

## Platform Info
- **Model:** GLM-5.2 (native reasoning)
- **Use:** Reasoning, agents, chat, vibe coding, deep analysis, automated workflows
- **Context:** 128K–1M
- **Token pipeline:** Manual markitdown, caveman full at 40 turns

---

## Z.ai Has 3 Modes

| Mode | What | OWL Load | Best For |
|------|------|----------|----------|
| **Agent** | Full agent with knowledge files + instructions | Full | Multi-step reasoning, CAPA, stress-test, formula verify, Arabic docs |
| **Chat** | Lightweight conversation | Light (SOUL summary + client row) | Quick lookups, one-off analysis, brainstorming, spot-checks |
| **AutoClaw** | Automated agent with scheduled triggers | Full + all skill domains | Scheduled workflows, recurring tasks, batch processing |

---

## Step 1: Create OWL Agent

Go to **z.ai** → Agents mode → New Agent

### Instructions
Paste contents of `AGENT_INSTRUCTIONS.md` (998 words).

### Knowledge Files to Upload
1. `SOUL.md` — Identity + NEVER laws
2. `CONTEXT.md` — Client data, formulas, visual identity
3. `AGENTS.md` — Agent roster + auto-trigger map
4. `MEMORY.md` — Preferences + mistakes
5. `skills/AUDIT.md` — If using for audit work
6. `skills/IMPLEMENT.md` — If using for implementation
7. `clients/KSA-REGULATORY.md` — If doing KSA work
8. `clients/MSD-MOI.md` — If working on MOI
9. `clients/SAGCO.md` — If working on SAGCO
10. `clients/AL-AHSA.md` — If working on Al-Ahsa

**Minimum (always):** SOUL.md + CONTEXT.md
**Full (complex tasks):** Add AGENTS.md + relevant domain file + client profile

---

## Step 2: Strip Rules

Z.ai uses native reasoning mode. Do NOT paste:
- `PUSH` instruction (replace with nothing — Z.ai reasons natively)
- `Work through this step by step` (Z.ai does this automatically)

---

## Step 3: Z.ai Chat Mode

**No setup needed** — just open z.ai and start chatting.

**What to paste as context (light load):**
```
OWL — Osama's Work Layer for TÜV Austria GCC.
Dual-track: Lead Auditor (identify gaps) + Lead Implementer (build deliverables).
Formulas: MOI V=S×(1−U/4) · SAGCO L×S · Al-Ahsa L×I.
Never mix formulas. Never deliver placeholders.
Active client: [paste relevant row from CONTEXT.md]
```

**Use Z.ai Chat for:**
- Quick lookups: "What clause covers supplier risk assessment?"
- Formula spot-checks: "Verify V=S×(1−U/4) with U=2, S=4"
- Brainstorming: "Give me 5 approaches to close this NC"
- Simple triage: "Should this go to Agent 1 or Agent 2?"
- Yes-no decisions: "Does ISO 27001:2022 require a DPO?"

**When to switch to Agent:** Needs client profile data, multi-step workflow, or deliverable creation → open Agent instead.

---

## Step 4: AutoClaw Mode

**Setup:** See `autoclaw-projects/SETUP.md` for full configuration of 7 automated OWL workflows.

**Automations available:**
1. Morning Briefing (Daily 8 AM) — audit calendar + project status
2. Audit Calendar Sync (Daily 9 AM) — update CONTEXT.md
3. Quality Gate Sweep (On save) — auto Skill 21 + 22
4. Template Population (On audit start) — pre-fill TÜV templates
5. Evening Digest (Daily 6 PM) — day summary + MEMORY.md
6. Weekly Reconciliation (Friday 5 PM) — verify SOUL.md counts
7. ComplianceHub Deploy Check (On git push) — Skill 38 + lint + build

**AutoClaw is never manual** — if you need to run something now, use Agent or Chat.

---

## Step 5: When to Use Z.ai vs Other Platforms

| Use Z.ai Agent For | Use Z.ai Chat For | Use AutoClaw For | Use Qwen For | Use Cline For |
|---------------------|--------------------|-------------------|-------------|---------------|
| Deep reasoning (CAPA, root cause) | Quick lookups | Morning briefing | Long context (1M) | Terminal coding |
| Adversarial stress-test | Formula spot-check | Calendar sync | Arabic document quality | ComplianceHub dev |
| Pre-audit analysis | One-off questions | Quality gate sweep | Task Assistant (100-doc) | Git operations |
| Arabic doc drafting | Brainstorming | Template population | Desktop web workspace | Filesystem access |
| Vibe coding (phone) | Simple triage | Evening digest | Research + GRC docs | Python scripts |
| Formula verification | Yes-no decisions | Weekly reconciliation | | |

---

## Step 6: Phone (Z.ai App)

Same agent works on Z.ai phone app. Use for:
- Quick reasoning tasks on-site
- Vibe coding while mobile
- Voice-to-analysis (dictate questions)
- Agent-based workflows

**Phone token budget:** ~4K–8K. Paste compressed summary only:
- Active client entry from CONTEXT.md
- Task description
- One skill paragraph from relevant domain file

---

## Step 7: caveman for Z.ai

Full caveman at 40 turns (vs 60 on desktop). Triggers automatically or say "caveman mode."

**caveman never modifies:** code blocks, formulas, clause refs, doc codes, technical terms.

---

## Best Workflows for Z.ai

### CAPA Root Cause Analysis
```
Analyze this NC using 5-Whys methodology:
[describe the nonconformity]

Then build: Root Cause → Containment → Corrective → Preventive → Effectiveness Verification (30/60/90 day)
```

### Adversarial Stress-Test (Skill 33)
```
Stress-test this decision:
[describe the decision]

Use 3 personas:
1. GRC Skeptic — challenge compliance assumptions
2. Growth Strategist — question resource allocation
3. Governance Expert — review decision-making process
```

### Pre-Audit Deep Analysis
```
Research [standard] latest version changes.
Focus on: new requirements, published interpretations, sector-specific guidance.
Impact on client: [client context]
```

### Formula Verification
```
Verify this risk formula for [client]:
[formula]

Check: mathematical correctness, edge cases, alignment with ISO 31000 methodology.
```
