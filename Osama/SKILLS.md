# Skills.md — Master Playbook (SOPs)

Standardized processes. Claude runs these without re-explanation. Trigger a skill by name or by describing the task. Any agent can run any skill.

**Platform:** ComplianceHub — full-stack FastAPI + Vite/React (https://github.com/0zMaradny/ComplianceHub)
**Legacy:** React artifact (TUV_Platform_Fixed.jsx) — archived, superseded by ComplianceHub

---

## Skill 01 — New Session Startup

**Trigger:** Start of any new Claude session

**Steps:**
1. Load Context.md — read the full dual role structure:
   - Track A (Auditor): Am I here to audit a client seeking certification? → Agent 1 (Judge)
   - Track B (Implementer): Am I here to build/deliver for a client? → Agent 2 (Architect)
   - Both tracks can be active in the same session (e.g. reviewing an audit gap, then building the fix)
2. Load Agents.md — identify which agent(s) are needed
3. Review Memory.md — apply all confirmed preferences, avoid all logged mistakes
4. Client isolation check: Which client is active?
   - MSD-MOI → Arabic MSA · GRC formulas · MOI visual identity
   - UACC → English technical · EnMS vocabulary · ISO 50001 formulas
   - SAGCO → TBD per deliverable
   - Al-Ahsa Municipality → Arabic · ISMS/27001 framework
   - New client → establish doc code, formulas, language, visual identity in Context.md first
5. Ask: "What are we delivering today — and in which role?"
6. Begin — never re-explain standards, client context, or formulas already in Context.md

---

## Skill 02 — IMS Audit (Multi-Standard)

**Trigger:** "Audit this document" / "Check against [ISO standards]" / "Surveillance audit prep"
**Agent:** Agent 1 (The Judge) — Track A: Lead Auditor role

**Scheme Responsibility Context:** Osama is Scheme Head at TÜV Austria GCC for:
- ISMS (ISO 27001) · ITSMS (ISO 20000-1) · BCMS (ISO 22301)
- Accredited to audit: ISO 9001 · 14001 · 45001 · 50001 · 42001 · 31000 · 37301

**Steps:**
1. Confirm: which standard(s), which audit type (Initial / Surveillance / Recertification)
2. Confirm: which client — check if this is one of the active implementation clients (MOI, UACC, SAGCO, Al-Ahsa) or a new CB client
3. Map each element to relevant clauses across all applicable standards
4. For each clause: Compliance Status · Evidence Required · NC Severity
5. Output table format:

| Clause | Standard | Compliance Status | Evidence Required | NC Severity |
|--------|----------|-------------------|-------------------|-------------|
| 6.1 | ISO 9001 | Partially Met | Risk register with documented methodology | Minor NC |

6. Summarize: total NCs by standard, top 3 priority gaps
7. Hand off to Agent 2 if this is also an implementation engagement (dual role scenario)

---

## Skill 03 — Build Excel Risk Register

**Trigger:** "Build a risk register" / "Create [X] risk register workbook"
**Agent:** Agent 4 (Excel Engineer) + Agent 2 (Implementer) for content

**Steps:**
1. Confirm: number of risks, standard (ISO 31000 / ISO 50001), organization (MOI or UACC)
2. Load visual identity from Context.md
3. Create sheets: Dashboard · Risk Register · Opportunities (if EnMS) · Scoring Matrix · Reference · _Lists
4. Build _Lists sheet: all dropdowns (likelihood, severity, level, owners, status)
5. Apply data validation on all dropdown columns linked to _Lists
6. Formula columns: L×S = Rating → nested IF → Risk Level
7. Conditional formatting: Red (Critical) / Orange (High) / Yellow (Medium) / Green (Low)
8. Dashboard: KPI cards (Total · Critical · High · Medium · Low) + summary chart
9. A4 print layout, freeze panes, repeat header row 1
10. Run scripts/recalc.py · verify zero formula errors
11. Output: complete .xlsx

---

## Skill 04 — Build BIA Workbook

**Trigger:** "Build BIA" / "Business Impact Analysis workbook"
**Agent:** Agent 4 (Excel Engineer)

**Steps:**
1. Confirm: process list, MTD/RTO/RPO values if known, organization context
2. Sheets: Dashboard · BIA Table · Process Detail · _Data
3. Columns: Process ID · Name · Department · Criticality · MTD · RTO · RPO · Dependencies · Recovery Strategy
4. Auto-calculate Criticality Score · conditional format by tier
5. Dashboard: criticality distribution, top 5 critical processes, RTO compliance status
6. Apply MOI visual identity
7. Run scripts/recalc.py · verify zero errors · Output: .xlsx

---

## Skill 05 — Write Arabic BCM Document

**Trigger:** "Write BCM document" / "Arabic business continuity plan"
**Agent:** Agent 5 (Arabic Writer) + Agent 2 (Implementer) for structure

**Steps:**
1. Confirm: scope (directorates/services), scenarios needed, compliance frameworks
2. Document structure:
   - ﺍﻟﻤﻘﺪﻣﺔ | Introduction
   - ﻧﻄﺎﻕ ﺍﻟﺘﻄﺒﻴﻖ | Scope
   - ﺗﺤﻠﻴﻞ ﺗﺄﺛﻴﺮ ﺍﻷﻋﻤﺎﻝ | BIA Tables
   - ﺳﻴﻨﺎﺭﻳﻮﻫﺎﺕ ﺍﻟﺘﺸﻐﻴﻞ | Operational Scenarios (5 minimum)
   - ﺧﻄﻂ ﺍﻻﺳﺘﺠﺎﺑﺔ ﺍﻟﻤﺮﺣﻠﻴﺔ | Phased Response Plans
   - ﺧﺎﺭﻃﺔ ﻃﺮﻳﻖ ﺍﻟﺘﻨﻔﻴﺬ | 12-Month Implementation Roadmap
   - ﺧﺮﻳﻄﺔ ﺍﻻﻣﺘﺜﺎﻝ | Compliance Mapping (ISO 22301 / DGA / NRC)
   - ﺇﻃﺎﺭ ﻗﻴﺎﺱ ﺍﻷﺩﺍء | KPI Measurement Framework
3. Voice: ﻗﻤﻨﺎ ﺑـ... / ﺗﻢ ﺗﻄﺒﻴﻖ... / first-person practitioner
4. ISO clause references stay in English · Risk IDs stay in English
5. Output: .docx via python-docx · full RTL formatting

---

## Skill 06 — ISO 42001 AI Management Implementation

**Trigger:** "ISO 42001" / "AI management system" / "AI policy" / "AIMS"
**Agent:** Agent 2 (Implementer) + Agent 3 (Developer) for automation layer

### 24 Mandatory Documents — ISO/IEC 42001:2023 (complete list):

| # | Document | Clause | Type |
|---|----------|--------|------|
| 1 | AIMS Scope | 4.1 | Word |
| 2 | Interested Parties & Requirements | 4.2 | Excel |
| 3 | AI System Inventory | A.3.2 | Excel |
| 4 | AI Context & Applicability Assessment | 4.1 & 4.3 | Word |
| 5 | AI Policy | 5.2 & A.2 | Word |
| 6 | Roles & Responsibilities Matrix | 5.3 & A.3.2 | Excel |
| 7 | AI Risk Assessment Methodology | 6.1.2 | Word |
| 8 | AI Risk Register & Treatment Plan | 6.1.3 | Excel |
| 9 | AI Objectives & Plans | 6.2 | Excel |
| 10 | Statement of Applicability (SoA) | 6.1.3 | Excel |
| 11 | Competency & Awareness Records | 7.2 & 7.3 | Excel |
| 12 | AI Communication Process | 7.4 | Word |
| 13 | Document Control Procedure | 7.5 | Word |
| 14 | AI Lifecycle Management Procedure | A.6 | Word |
| 15 | Human Oversight Mechanism | A.6.2 | Word |
| 16 | AI Incident Management Procedure | A.9 | Word |
| 17 | AI Change Management Procedure | A.9 | Word |
| 18 | AI Monitoring & Validation Records | 9.1 | Excel |
| 19 | Internal Audit Procedure & Reports | 9.2 | Word |
| 20 | Management Review Records | 9.3 | Word |
| 21 | KPI & Monitoring Metrics | 9.1 | Excel |
| 22 | Nonconformity & Corrective Action Procedure | 10.2 | Word |
| 23 | Continual Improvement Records | 10.1 | Excel |
| 24 | AI Impact Assessment (AIA) — ISO 42005 | 6.1.4 & A.5.5 | Word + Excel |

**Implementation Steps:**
1. Define AIMS scope (Clause 4.3) and organizational AI context
2. Build AI System Inventory (A.3.2) — all models, tools, services in scope
3. Conduct AI Risk Assessment using documented methodology (6.1.2)
4. Complete SoA (6.1.3) — justify all Annex A control inclusions/exclusions
5. Develop AI Policy + Roles & Responsibilities (5.2 + 5.3)
6. Run AI Impact Assessment per system (6.1.4)
7. Establish lifecycle, oversight, incident, and change procedures (A.6, A.9)
8. Set KPIs and monitoring plan (9.1)
9. Map overlaps to ISO 27001 (security controls A.5–A.8 align with ISMS)
10. Agent 3 adds: Python monitoring scripts for automated AI governance compliance tracking
11. Output: all 24 mandatory documents — Word + Excel, audit-ready

### ISO/IEC 42005 — AI System Impact Assessment (AIIA) — 7-Step Process:

| Step | Name | Key Output |
|------|------|------------|
| 1 | Define AI System Context | System description: purpose, intended use, life cycle stage, key components |
| 2 | Identify Stakeholders | Register of direct/indirect users, affected parties, vulnerable groups |
| 3 | Identify Impact Categories | Assessment across 10 categories (see below) |
| 4 | Assess Severity & Likelihood | Inherent Risk = Severity (1–5) × Likelihood (1–5). Consider scale, duration, reversibility |
| 5 | Review Controls & Mitigations | Existing controls adequacy + additional mitigations with owners and timelines |
| 6 | Determine Residual Impact | Residual Severity × Residual Likelihood = Overall Residual Impact Level |
| 7 | Governance Decision & Review | Accept / Conditionally Accept / Escalate / Reject + documented rationale + action plan |

### 10 ISO 42005 Impact Categories (Step 3 — must assess ALL):

| # | Category | What to Check |
|---|----------|---------------|
| 1 | Fairness | Bias in data, model, or outcomes — protected characteristics |
| 2 | Privacy | Personal data processing, consent, data minimisation |
| 3 | Safety | Physical or psychological harm to users or third parties |
| 4 | Security | Adversarial attacks, data poisoning, model manipulation |
| 5 | Explainability | Ability to explain AI decisions to affected stakeholders |
| 6 | Accountability | Clear ownership of AI decisions and outcomes |
| 7 | Societal | Broad societal effects: employment, democracy, social cohesion |
| 8 | Economic | Financial harm, market distortion, access inequity |
| 9 | Legal | Compliance with applicable laws: GDPR, labour law, liability |
| 10 | Human Autonomy | Degree to which AI overrides or undermines human decision-making |

### AIIA Audit Key Points (checklist for auditors):
- AI system purpose and intended use documented
- All stakeholder groups identified including vulnerable groups
- All 10 impact categories assessed (N/A requires justification)
- Each impact scored: Severity (1–5) × Likelihood (1–5)
- Controls identified and evaluated for adequacy
- Additional mitigations planned with responsible owners and target dates
- Residual impact determined after controls applied
- Governance body has reviewed and recorded decision (Accept/Escalate/Reject)
- Action plan exists for all conditional acceptances
- Monitoring and periodic review schedule defined
- Communication to affected stakeholders documented

---

## Skill 07 — ISO Compliance Gap Check

**Trigger:** "Gap analysis" / "Check compliance against [standard]"
**Agent:** Agent 1 (Judge) for gaps · Agent 2 (Implementer) for remediation

**Steps:**
1. Confirm standard: ISO 31000 / 22301 / 50001 / 9001 / 27001 / 42001 (or multi-standard IMS)
2. List all mandatory clauses for that standard
3. Per clause: Status (Fully Met / Partially Met / Not Met / N/A) · Evidence · Gap · Recommended Action
4. Calculate: compliance % by clause group
5. Output: structured Excel table or Word report depending on request
6. Priority matrix: Critical gaps (immediate) vs Medium gaps (90 days) vs Low gaps (6 months)

---

## Skill 08 — Build Python Automation Tool

**Trigger:** "Automate [task]" / "Build a script for [workflow]"
**Agent:** Agent 3 (Automator) + Agent 2 (Implementer) for ISO control layer

**Steps:**
1. Clarify: what is being automated, what inputs/outputs are needed
2. Agent 3 drafts modular Python script with # --- CONFIG --- block
3. Agent 2 reviews: identifies which ISO controls apply (e.g., ISO 27001 for data handling)
4. Add ISO control comments inline in the code
5. Provide: script + usage instructions + any ISO documentation requirements triggered by the tool
6. Output: .py file, locally deployable, no cloud dependency assumed

---

## Skill 09 — Add Treatment Plan Sheet

**Trigger:** "Add treatment plan" / "Link treatments to risk register"
**Agent:** Agent 4 (Excel Engineer)

**Steps:**
1. Load existing risk register · confirm Risk ID column reference
2. Create Treatment Plan sheet
3. Columns: Risk ID · Risk Description (VLOOKUP) · Treatment Type · Action · Owner · Due Date · Status · Post-Treatment Residual Risk
4. VLOOKUP formula: =VLOOKUP(A2,'Risk Register'!$A:$C,2,0) for description
5. Status dropdown: Not Started / In Progress / Completed / Deferred
6. Conditional format Status column · link completion % back to Dashboard KPI

---

## Skill 10 — Travel & Savings Optimizer

**Trigger:** "Plan trip" / "Find deal for [destination/purchase]"
**Agent:** Agent 6 (Personal Concierge)

**Steps:**
1. Identify: destination (Alexandria / Makkah / Madinah / other), dates, budget
2. Search: current Saudia / Flynas / EgyptAir offers for Riyadh ↔ target route
3. Layer: applicable cashback via STC Pay, Urpay, or bank offers (Al-Rajhi / SNB)
4. For Umrah trips: check quiet periods, proximity to Haram, transport options
5. Output: "Savings Strategy" — total trip cost with and without optimizations

---

## Skill 11 — ComplianceHub Full-Stack Development

**Trigger:** "Fix the platform" / "Add feature to ComplianceHub" / "Debug backend/frontend"
**Agent:**  Agent 3 (Developer) + Agent 7 (Platform Engineer)

### Tech Stack
- **Backend:** FastAPI + Uvicorn (port 8000) — `backend/app/`
- **Frontend:** React + Vite (port 5173) — `frontend/src/`
- **AI:** Multi-provider router — `backend/app/services/ai/router.py`
- **Docs:** python-docx document generation — `backend/app/services/document_generator.py`
- **Data:** clause_data.py — data-driven clause database for 13 standards
- **PDF:** LibreOffice headless conversion — `backend/app/services/pdf_converter.py`

### Key Constraints
- Backend: `python -m compileall . -q` + `python -m pyflakes app/` — zero errors mandatory
- Frontend: `npm run lint` + `npm run build` — zero errors mandatory
- AI keys in `backend/.env` — never hardcode
- All 8 document types generated via `OUTPUT_DOCUMENTS` list in config
- 13 standards in `ISO_STANDARDS` — never hardcode ISO 9001 sections
- TÜV branding: TUV_BLUE #003D7A, TUV_RED #C00000

### Development Steps
1. Identify: backend (Python/FastAPI) or frontend (React/Vite) or both
2. Backend changes: edit → `compileall` → `pyflakes` → test endpoint
3. Frontend changes: edit → `lint` → `build` → verify in browser
4. AI changes: check router chain, provider fallback, Autodebugger integration
5. Run full stack: `bash run.sh` (offline) or `bash run.sh --local-ai`
6. Smoke test: `curl http://localhost:8000/api/standards`

---

## Skill 12 — CAPA Plan Generation (Corrective & Preventive Action)

**Trigger:** "Generate CAPA" / "Minor NC / Major NC found" / "Corrective action needed"
**Agent:** Agent 1 (Judge) to confirm finding · Agent 2 (Implementer) to write CAPA

**Steps:**
1. Confirm: clause reference · NC severity (Minor / Major) · objective evidence of the finding
2. CAPA structure (mandatory, in this order):
   - Root Cause Analysis — 5-Whys methodology, documented per clause
   - Immediate Containment Action — within 24–48 hours
   - Corrective Action — eliminate root cause · assign responsible owner · set target date
   - Preventive Action — systemic change to prevent recurrence across the system
   - Effectiveness Verification — define measurable success criteria and review date
3. Language: ISO audit formal English (or Arabic MSA if client is Arabic)
4. Reference: ISO 9001 Clause 10.2 · ISO 27001 Clause 10.1 as applicable
5. Output: CAPA table in Word or inline in platform UI (amber panel under NC clause)

---

## Skill 13 — GitHub vs Platform Delta Comparison

**Trigger:** "Compare GitHub version" / "What's new in this code" / "Merge improvements"
**Agent:** Agent 3 (Developer)

**Steps:**
1. Fetch latest from GitHub: `gh api repos/0zMaradny/ComplianceHub/contents/<path>`
2. Compare against local `~/ComplianceHub/` working copy
3. For each changed file: classify as Critical / High / Medium
4. Apply changes — backend: `compileall` + `pyflakes`; frontend: `lint` + `build`
5. Update Memory.md session log with delta count and summary

---

## Skill 14 — ComplianceHub: Audit Document Package Generation

**Trigger:** "Generate audit package" / "Create all documents for [client]" / "Generate 8 docs"
**Agent:** Agent 7 (Platform Engineer) + Agent 2 (Implementer) for content

### 8 Document Types (OUTPUT_DOCUMENTS)

| # | Type | Label |
|---|------|-------|
| 1 | Audit_Plan_Stage_1 | Audit Plan Stage 1 |
| 2 | Audit_Plan_Stage_2 | Audit Plan Stage 2 |
| 3 | Participation_List | Participation List |
| 4 | Audit_Report | Audit Report |
| 5 | ISO_Checklist | ISO Checklist |
| 6 | Certificate_Text | Certificate Text |
| 7 | TNL | Test / Nonconformity Log |
| 8 | Certificate | Certificate |

### Generation Steps
1. Upload audit notes (.docx/.txt) + manday data via `/api/upload`
2. Select standard(s) from 13 available
3. Provide API key (or use offline/local mode)
4. System extracts shared context (client, date, team, scope) via AI
5. Generates all 8 documents with per-task AI routing:
   - Audit_Report → claude primary; Certificate → claude primary
   - Audit_Plan_Stage_1/2 → openai primary; TNL → openai primary
   - ISO_Checklist → gemini primary; Participation_List → openai primary
6. Each document validated by Autodebugger (placeholder check, required fields, self-heal retry)
7. Output: download package (DOCX + optional PDF via LibreOffice)
8. TÜV-branded templates applied from `backend/templates/`

### AI Modes
- **Cloud AI:** Best quality — uses Gemini/OpenAI/Claude per task routing
- **HF Free:** 7/8 docs via Llama-3-8B (HuggingFace Inference)
- **Local AI:** llama.cpp qwen-1.5b — ~6-7/8 docs
- **Offline:** Professional templates — instant, no AI needed

---

## Skill 15 — AI Prompt Engineering (Merged 12-part Anatomy Framework)

**Trigger:** "Write a prompt" / "Improve this prompt" / "Build me a prompt for [task]"
**Agent:** Agent 8 (Prompt Architect)

**Framework:** Merged from Ruben Hassid (9-part) + serveai.ig → 12-part master framework
**Always include:** ROLE + TASK + OUTPUT + PUSH. Add others as needed.

### The 12 Parts

| # | Part | Color | When to Use |
|---|------|-------|-------------|
| 1 | ROLE | 🔴 | Always — define the expert persona and its priority |
| 2 | TASK | 🔴 | Always — action verb + deliverable + scope + format |
| 3 | CONTEXT | 🔵 | Always for client work — situation, files, risks |
| 4 | REASONING | 🟡 | Complex outputs — state the goal and why the structure serves it |
| 5 | REFERENCE | 🟢 | Matching existing document style or voice |
| 6 | SUCCESS BRIEF | 🟡 | Client deliverables — define recipient behavior as success |
| 7 | RULES | 🩷 | Any output needing guardrails — positive instructions only |
| 8 | TOOLS | 🟣 | Web search / Drive / Calendar actions needed |
| 9 | CONVERSATION | 🔴 | Task has more than 2 unstated assumptions |
| 10 | PLAN | 🔵 | Multi-step deliverable over 500 words |
| 11 | OUTPUT | 🔴 | Always — define format, sections, quality check per section |
| 12 | PUSH | 🟢 | Always last — activates maximum reasoning |

### Quick Selection Guide

| Task Type | Parts to Include |
|-----------|-----------------|
| Quick answer | ROLE + TASK + OUTPUT + PUSH |
| ISO clause check | ROLE + TASK + CONTEXT + RULES + OUTPUT + PUSH |
| Client document | ROLE + TASK + CONTEXT + REASONING + SUCCESS BRIEF + RULES + OUTPUT + PUSH |
| Arabic document | ROLE + TASK + CONTEXT + REFERENCE + SUCCESS BRIEF + RULES + OUTPUT + PUSH |
| Complex audit | All 12 parts |

### ISO/GRC ROLE Defaults
- **Audit:** "Act as Senior Lead Auditor at UKAS-accredited CB. Prioritize NC precision over general advice."
- **Implement:** "Act as Senior Lead Implementer for [standard]. Prioritize complete audit-defensible docs."
- **Arabic:** "Act as Senior ISO Implementer and Arabic technical writer. MSA first-person practitioner voice."
- **AI/42001:** "Act as ISO 42001 Lead Implementer. Prioritize ethical AI docs and Annex A control coverage."

---

## Skill 16 — Six-Gate Delivery Pipeline (ISO Project)

**Trigger:** "Plan the project" / "What's the delivery sequence?"
**Agent:** Agent 9 (Delivery Manager) coordinating Agents 1–6

| Gate | Name | Agent | Output |
|------|------|-------|--------|
| G1 | Scope & Context | Agent 2 | Context doc, stakeholder map, scope statement |
| G2 | Gap Analysis | Agent 1 | Full clause-by-clause gap report |
| G3 | Risk Register | Agent 4 | Complete Excel risk register |
| G4 | Implementation Docs | Agent 2 + 5 | Policies, procedures, CAPA log |
| G5 | Internal Audit | Agent 1 | Pre-certification audit report |
| G6 | Certification Package | Agent 7 | Full 8-document audit package via ComplianceHub |

**Hard Rule:** No gate skips. Agent 1 gap analysis must precede Agent 2 implementation.

---

## Skill 17 — ComplianceHub Debugging Checklist

**Trigger:** "Something's broken" / "Error in platform" / "Build fails"
**Agent:** Agent 3 (Developer)

### Backend Triage
1. `cd backend && python -m compileall . -q` — syntax errors?
2. `cd backend && python -m pyflakes app/` — unused imports, undefined vars?
3. `curl http://localhost:8000/api/standards` — API responding?
4. Check `backend/.env` — AI keys present and valid?
5. Check `backend/app/config.py` — paths correct?

### Frontend Triage
1. `cd frontend && npm run lint` — ESLint errors?
2. `cd frontend && npm run build` — build succeeds?
3. Check browser console for React errors
4. Verify `API = '/api'` proxy in vite.config.js

### AI Pipeline Triage
1. Check provider chain in `ai/router.py` — correct order for task type?
2. Autodebugger: `debugger.py` — placeholder patterns, required fields?
3. AI keys: env vars set? Key prefix matches provider?
4. Fallback: does offline mode work when AI fails?

### Full Stack
1. `bash run.sh` — both servers start?
2. Backend port 8000 + frontend port 5173 both accessible?
3. Upload → generate → download flow works end-to-end?

---

## Skill 18 — Legacy React Artifact (Reference Only)

**Trigger:** Questions about the old TUV_Platform_Fixed.jsx artifact
**Agent:** Agent 7 (Platform Engineer)

**Status:** Archived — superseded by ComplianceHub full-stack. Kept for reference only.

**Hard Rules (never violate if maintaining legacy):**
- ❌ NO import from "firebase/..." — use window.storage only
- ❌ NO process.env · NO require() · NO Gemini API
- ✅ AI: https://api.anthropic.com/v1/messages — claude-sonnet-4-20250514
- ✅ CDN: cdnjs.cloudflare.com (mammoth, XLSX)
- ✅ Excel: window.XLSX.utils.aoa_to_sheet + writeFile — NOT HTML blob
- ✅ Checklist IDs: deterministic — `${std}-${clause.replace(/\./g,'_')}`
- ✅ setAuditProjects called ONCE after loop — never inside forEach
- ✅ sanitizeHtml() before any dangerouslySetInnerHTML
- ✅ aiCallLimiter.canProceed() before every AI call
- ✅ AbortController per AI call, cleanup in unmount
- ✅ <ErrorBoundary> wrapping <App/>
