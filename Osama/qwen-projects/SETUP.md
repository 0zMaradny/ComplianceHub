# Qwen Studio Setup Guide — OWL v4.0 (v2)

## Constraints
- **Main Qwen (system prompt):** 500 words max, no knowledge files
- **Projects:** 1000 words max instructions, knowledge files allowed

---

## What Changed in v2
- Full SOP detail from domain files (AUDIT.md, IMPLEMENT.md, DEV.md, SYSTEM.md, PERSONAL.md)
- Humanizer tone baked into every Project — mandatory pipeline step before delivery
- Specific methodologies, checklists, quality gates (not just skill numbers)
- KSA regulatory cross-maps with specific control references
- Quality pipeline explicit in each Project

---

## Step 1: Main Qwen System Prompt

Go to **qwen.ai** → Settings → System Prompt → Paste contents of `MAIN.md` (431 words)

---

## Step 2: Create 4 Projects

Go to **qwen.ai** → Projects → New Project

### Project 1: OWL Auditor
- **Instructions:** Paste `AUDIT.md` (710 words)
- **Knowledge files:**
  1. `skills/AUDIT.md`
  2. `clients/KSA-REGULATORY.md`
  3. `clients/MSD-MOI.md`
  4. `clients/SAGCO.md`
  5. `clients/AL-AHSA.md`
  6. `templates/tuv-austria/README.md`
- **Use for:** Audit, NC findings, gap analysis, compliance checks, audit reports, SoA, CAPA, pre-audit research

### Project 2: OWL Implementer
- **Instructions:** Paste `IMPLEMENT.md` (832 words)
- **Knowledge files:**
  1. `skills/IMPLEMENT.md`
  2. `CONTEXT.md`
  3. `clients/KSA-REGULATORY.md`
  4. `clients/MSD-MOI.md`
  5. `clients/SAGCO.md`
  6. `clients/AL-AHSA.md`
  7. `clients/TEMPLATE.md`
- **Use for:** Policies, procedures, risk registers, BIA, Arabic docs, training, CAPA, client onboarding, version control

### Project 3: OWL Developer
- **Instructions:** Paste `DEV.md` (566 words)
- **Knowledge files:**
  1. `skills/DEV.md`
  2. `TOOLS.md`
  3. `clients/SAGCO.md`
  4. `OPENCLAW_OWL_SKILLS.md`
- **Use for:** Python scripts, ComplianceHub features, Excel/Word automation, debugging, code review

### Project 4: OWL System
- **Instructions:** Paste `SYSTEM.md` (791 words)
- **Knowledge files:**
  1. `skills/SYSTEM.md`
  2. `AGENTS.md`
  3. `MEMORY.md`
  4. `SKILLS.md`
  5. `PLATFORMS.md`
- **Use for:** Prompt engineering, skill management, routing, quality gates, token optimization, session management

---

## Step 3: Workflow

| Task | Where |
|------|-------|
| Quick question / brainstorming | Main Qwen chat |
| Audit / compliance / gap analysis | Audit Project |
| Policy / procedure / risk / Arabic docs | Implement Project |
| Python / ComplianceHub / code | Dev Project |
| OWL system / prompts / routing | System Project |

---

## Step 4: Knowledge File Maintenance

When OWL files change, re-upload to the relevant Project. Update frequency:
- `CONTEXT.md` — client status changes
- `MEMORY.md` — after each session
- `SKILLS.md` — skills added/modified
- `clients/*.md` — client data changes

---

## Humanizer Pipeline (All Projects)

Every output goes through:
```
1. Task execution (agent builds deliverable)
2. Humanizer pass (strip AI patterns from narrative text)
3. Skill 21 (language gate — client-specific rules)
4. Skill 22 (quality gates G1–G10)
5. Delivery
```

Humanizer never touches: code blocks, formulas, clause refs, doc codes, technical terms.

---

## Word Count Summary

| File | Words | Limit |
|------|-------|-------|
| MAIN.md | 499 | 500 |
| AUDIT.md | 998 | 1000 |
| IMPLEMENT.md | 998 | 1000 |
| DEV.md | 996 | 1000 |
| SYSTEM.md | 999 | 1000 |

> ⚠️ AUDIT, IMPLEMENT, DEV, and SYSTEM are at or near the 1000-word limit. Any additions require trimming elsewhere.
