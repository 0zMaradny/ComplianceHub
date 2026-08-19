# Gemini Pro Setup Guide — OWL v4.2

## Platform Info
- **Models available (web + Android):**
  - Gemini Flash 3.5 — fast tasks, quick queries
  - Gemini Thinking 3.6 — deep reasoning, complex analysis
  - Gemini Pro 3.1 — best quality, Deep Research, Gems
- **Context:** 1M+
- **Key features:** Deep Research, Web Search, Grounding, Canvas
- **Token pipeline:** Upload markitdown-converted .md files, caveman full at 40 turns
- **Use Pro 3.1 for Gems**, Flash 3.5 for quick queries, Thinking 3.6 for complex reasoning

---

## What Changed in v2
- Full SOP detail with specific workflows per Gem (9 workflows for Auditor, 9 for Implementer, 9 for KSA Lead)
- Humanizer tone baked into every Gem — mandatory pipeline step
- Exact knowledge file lists per Gem with "always" vs "when needed" labels
- KSA control references with specific IDs (NCA ECC 1-1-1, PDPL Art.20, etc.)
- Privacy rules per Gem (HIGH clients BLOCKED, MEDIUM scrub OK)

---

## Step 1: Convert Knowledge Files with markitdown

Before uploading to Gemini, verify all files are .md:

```powershell
# Files already .md — just verify clean
# PDFs/DOCX must be converted:
markitdown client-policy.pdf -o client-policy.md
markitdown audit-report.docx -o audit-report.md
```

---

## Step 2: Create 5 Gems

Go to **gemini.google.com** → Gems (left sidebar) → New Gem

### Gem 1: OWL Auditor
- **Instructions:** Paste `GEM1_AUDITOR.md`
- **Knowledge files to upload:**
  1. SOUL.md (always)
  2. CONTEXT.md (always)
  3. skills/humanizer/SKILL.md (always — 33 pattern anti-slop pass)
  4. clients/KSA-REGULATORY.md (for KSA work)
  5. clients/MSD-MOI.md (when auditing MOI)
  6. clients/SAGCO.md (when auditing SAGCO)
  7. clients/AL-AHSA.md (when auditing Al-Ahsa)
  8. templates/tuv-austria/README.md (for audit package)
  9. skills/AUDIT.md (for detailed methodology)
- **Enable:** Deep Research ON, Web Search ON, Grounding ON
- **Use for:** Pre-audit research, gap analysis, clause mapping, audit reports, SoA, pre-audit briefs

### Gem 2: OWL Implementer
- **Instructions:** Paste `GEM2_IMPLEMENTER.md`
- **Knowledge files to upload:**
  1. SOUL.md (always)
  2. CONTEXT.md (always)
  3. skills/humanizer/SKILL.md (always)
  4. clients/KSA-REGULATORY.md (for KSA work)
  5. clients/MSD-MOI.md (when working on MOI)
  6. clients/SAGCO.md (when working on SAGCO)
  7. clients/AL-AHSA.md (when working on Al-Ahsa)
  8. clients/TEMPLATE.md (for new clients)
  9. skills/IMPLEMENT.md (for detailed methodology)
- **Enable:** Canvas ON, Deep Research ON
- **Use for:** Policy/procedure drafting, risk registers, BIA, BCM plans, Arabic docs, training, ISO 42001 AIMS, client onboarding

### Gem 3: OWL KSA Lead
- **Instructions:** Paste `GEM3_KSA.md`
- **Knowledge files to upload:**
  1. SOUL.md (always)
  2. CONTEXT.md (always)
  3. skills/humanizer/SKILL.md (always)
  4. clients/KSA-REGULATORY.md (always — primary reference)
  5. clients/MSD-MOI.md (when working on MOI)
  6. clients/AL-AHSA.md (when working on Al-Ahsa)
  7. clients/SAGCO.md (when working on SAGCO)
  8. skills/AUDIT.md (for audit workflows)
  9. skills/IMPLEMENT.md (for implementation workflows)
- **Enable:** Deep Research ON, Web Search ON, Grounding ON
- **Use for:** NCA ECC, SAMA CSF, DGA Qiyas, SDAIA, PDPL, Etimad scoring, cross-framework integration, Saudi regulatory research

### Gem 4: OWL Personal
- **Instructions:** Paste `GEM4_PERSONAL.md`
- **Knowledge files to upload:**
  1. SOUL.md (always)
  2. MEMORY.md (always — personal preferences)
  3. CONTEXT.md (reference only)
  4. skills/humanizer/SKILL.md (always)
- **Enable:** Deep Research ON, Web Search ON
- **Use for:** Travel, cashback, inbox, meeting notes, productivity, board updates, stress-testing, automation roadmap

### Gem 5: OWL Code Assistant
- **Instructions:** Paste `GEM5_CODE.md`
- **Knowledge files to upload:**
  1. SOUL.md (always)
  2. TOOLS.md (always — code standards)
  3. skills/DEV.md (always)
  4. skills/humanizer/SKILL.md (always)
  5. skills/IMPLEMENT.md (when building deliverables)
  6. clients/SAGCO.md (if SAGCO dashboard)
  7. OPENCLAW_OWL_SKILLS.md
- **Enable:** Deep Research ON
- **Use for:** Python scripts, Excel automation, code review, debugging, API research, ComplianceHub features

---

## Step 3: When to Use Each Gem

| Task | Gem | Why |
|------|-----|-----|
| Pre-audit research | Gem 1 (Auditor) | Deep Research + web grounding |
| Gap analysis | Gem 1 (Auditor) | Clause knowledge + reasoning |
| Audit report | Gem 1 (Auditor) | Formal CB language |
| SoA building | Gem 1 (Auditor) | Annex A control mapping |
| Pre-audit brief | Gem 1 (Auditor) | Web-sourced intelligence |
| Policy drafting | Gem 2 (Implementer) | Canvas + document editing |
| Procedure writing | Gem 2 (Implementer) | Structured deliverables |
| Risk register design | Gem 2 (Implementer) | Excel formula logic |
| BIA / BCM plans | Gem 2 (Implementer) | Process mapping |
| Arabic documents | Gem 2 (Implementer) | RTL + practitioner voice |
| ISO 42001 AIMS | Gem 2 (Implementer) | 24 mandatory docs |
| Training courses | Gem 2 (Implementer) | Content structure |
| Client onboarding | Gem 2 (Implementer) | Profile creation |
| NCA ECC compliance | Gem 3 (KSA Lead) | 114 controls, 5 domains |
| SAMA CSF assessment | Gem 3 (KSA Lead) | 6 domains, financial |
| PDPL implementation | Gem 3 (KSA Lead) | Art.5→A.5.34 cross-maps |
| DGA Qiyas maturity | Gem 3 (KSA Lead) | 8 dimensions, 5 levels |
| SDAIA AI ethics | Gem 3 (KSA Lead) | 7 principles, ISO 42001 |
| Etimad scoring | Gem 3 (KSA Lead) | Certification strategy |
| Vision 2030 alignment | Gem 3 (KSA Lead) | Saudization, PIF, NEOM |
| Flight/hotel research | Gem 4 (Personal) | Deep Research + deals |
| Cashback optimization | Gem 4 (Personal) | STC Pay, Urpay, Al-Rajhi, SNB |
| Inbox triage | Gem 4 (Personal) | Summarize, draft, triage |
| Board updates | Gem 4 (Personal) | Executive summary |
| Stress-test decisions | Gem 4 (Personal) | 3-persona challenge |
| Python scripts | Gem 5 (Code) | Modular, clean code |
| Excel automation | Gem 5 (Code) | openpyxl, live formulas |
| Code review | Gem 5 (Code) | NEVER laws check |
| Debugging | Gem 5 (Code) | Systematic fix |
| API/library research | Gem 5 (Code) | Deep Research |

---

## Step 4: Gemini on Android

Same 5 Gems work on Gemini Android app. Use for:
- On-site audit questions (voice-to-research)
- Mobile document review
- Deep Research while mobile

---

## Step 5: Gemini vs Qwen vs Z.ai — When to Use

| Use Gemini For | Use Qwen For | Use Z.ai Agent For | Use Z.ai Chat For | Use AutoClaw For |
|----------------|-------------|--------------------|--------------------|-------------------|
| Deep Research (multi-source synthesis) | Long context work (1M) | Multi-step reasoning | Quick lookups | Scheduled workflows |
| Web grounding (real-time data) | Arabic document quality | CAPA root cause | Formula spot-checks | Morning/evening briefings |
| Canvas (document editing) | Task Assistant (100-doc) | Stress-test | One-off questions | Quality gate sweeps |
| Drive-synced knowledge base | Daily client deliverables | Pre-audit analysis | Brainstorming | Template population |
| Regulatory research with web search | Desktop web workspace | Arabic doc drafting | Triage | Calendar sync |

### Model Selection Within Gemini

| Task | Model | Why |
|------|-------|-----|
| Gem operations (5 Gems) | Pro 3.1 | Best quality, supports Deep Research + Canvas + Grounding |
| Quick question (no Gem) | Flash 3.5 | Fast, 1,500 req/day free tier |
| Complex reasoning without Gem | Thinking 3.6 | Chain-of-thought, multi-step |
| Daily deliverable in Gem | Pro 3.1 | Consistent quality, Deep Research available |
| Mobile quick query | Flash 3.5 | Fastest response |
| Research-heavy task | Pro 3.1 + Deep Research | Multi-source synthesis with citations |

### Cross-Gem Coordination Patterns

| Pattern | Gems | How |
|---------|------|-----|
| Full audit package | 1 → 2 → 3 | Gem 1 identifies findings → Gem 2 builds fixes → Gem 3 validates KSA alignment |
| KSA + implement | 3 → 2 | Gem 3 defines regulatory requirements → Gem 2 builds implementation |
| Arabic doc with KSA overlay | 2 → 3 | Gem 2 drafts Arabic doc → Gem 3 validates NCA/PDPL references |
| Code + audit check | 5 → 1 | Gem 5 builds feature → Gem 1 checks compliance |
| Personal + board update | 4 | Gem 4 handles both (personal + board) |
| Audit + research | 1 → Deep Research | Gem 1 uses Deep Research for pre-audit intelligence |

---

## Step 6: Z.ai and AutoClaw Coordination

### When Gemini Hands Off to Z.ai

| Gemini Gem | Hand Off Trigger | Z.ai Mode | Why |
|------------|-----------------|-----------|-----|
| Gem 1 (Auditor) | CAPA root cause needed | Z.ai Agent | 5-Whys multi-step reasoning |
| Gem 2 (Implementer) | Stress-test implementation plan | Z.ai Agent | Adversarial 3-persona |
| Gem 3 (KSA Lead) | Deep CAPA for KSA NC | Z.ai Agent | Multi-step regulatory reasoning |
| Any Gem | Quick one-off question | Z.ai Chat | Fast, lightweight |
| Any Gem | Recurring/scheduled task | AutoClaw | Automated pipeline |

### When AutoClaw Triggers Gemini

| AutoClaw Automation | Gemini Role | How |
|---------------------|-------------|-----|
| Morning Briefing | Gem 1 + Gem 3 | Audit calendar + KSA updates |
| Quality Gate Sweep | Gem 2 | Language Gate + Quality Gates on deliverables |
| Evening Digest | Gem 4 | Board summary + personal digest |
| Weekly Reconciliation | None | Pure count verification (no Gemini needed) |

---

## Step 7: Token Pipeline

- **markitdown:** Convert all files before uploading to Gems
- **caveman:** Full at 40 turns — say "caveman mode" to activate
- **Never modify:** code blocks, formulas, clause refs, doc codes, technical terms

---

## Privacy Rules (All Gems) — Projects vs Audit Clients
- **MSD-MOI / Al-Ahsa (HIGH, Project):** BLOCKED on Gemini — use Cline (local) or Claude phone only
- **SAGCO (MEDIUM, Project):** PII scrub required — remove names, phones, emails, NIDs, addresses
- **Audit clients (varies):** Classify at session start: gov → HIGH → BLOCKED, industrial → MEDIUM → scrub OK, unknown → default MEDIUM
- **UACC (Archived):** Reference only, MEDIUM sensitivity
- **OWL internal:** Full Gemini access

## Cross-Platform Privacy Routing

| Client | Gemini | Z.ai Agent | Z.ai Chat | AutoClaw | Cline | Claude |
|--------|--------|------------|-----------|----------|-------|--------|
| MSD-MOI (HIGH) | ❌ | ❌ | ❌ | ❌ | ✅ local | ✅ |
| Al-Ahsa (HIGH) | ❌ | ❌ | ❌ | ❌ | ✅ local | ✅ |
| SAGCO (MEDIUM) | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ | ✅ |
| Audit (varies) | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ | ✅ |

---

## Word Count Summary

| File | Words |
|------|-------|
| GEM1_AUDITOR.md | 768 |
| GEM2_IMPLEMENTER.md | 858 |
| GEM3_KSA.md | 883 |
| GEM4_PERSONAL.md | ~400 |
| GEM5_CODE.md | ~500 |
