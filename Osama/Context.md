# Context.md — My Complete Brain
_See also: USER.md (human facts) · SOUL.md (identity) · AGENTS.md (roles) · SKILLS.md (SOPs) · MEMORY.md (preferences) · TOOLS.md (infrastructure + keys)_

Loads at the start of every session. Claude reads this to feel "experienced" — not starting from scratch every time. Last updated: June 2026

## Who I Am
→ See USER.md — single source for personal and professional facts.

## Professional Identity — Dual Role

I operate simultaneously as Lead Auditor AND Lead Implementer. These are two distinct roles with different outputs, language, and responsibilities. The same ISO standard can appear in both tracks for different clients.

### Track A — Lead Auditor (Certification Body)

**Organization:** TÜV Austria GCC — acting as Certification Body
**Accreditation:** UKAS · CQI/IRCA · PECB

**Scheme Responsibilities (I am Scheme Head for):**

| Scheme | Standard | Scope |
|--------|----------|-------|
| ISMS | ISO/IEC 27001:2022 | Information Security Management System |
| ITSMS | ISO/IEC 20000-1:2018 | IT Service Management System |
| BCMS | ISO 22301:2019 | Business Continuity Management System |

**Audit Output Rules:**
- Identify only — never offer solutions during audit
- Output format: Clause | Compliance Status | Evidence Required | NC Severity
- Language: formal certification body English (or Arabic where required)
- NC types: Major NC · Minor NC · OFI · Observation
- CAPA required for all NCs — structure: Root Cause → Containment → Corrective → Preventive → Verification

**Full Audit Portfolio (accredited to audit all of these):**
ISO 9001 · ISO 14001 · ISO 45001 · ISO 50001 · ISO 27001 · ISO 42001
ISO 22301 · ISO 20000-1 · ISO 31000 · ISO 37301

**KSA Frameworks (active audit practice):** NCA ECC · SAMA CSF · DGA Qiyas · CITC CSF · BCM · MVC

### Track B — Lead Implementer (Consulting & Implementation)

**Role:** I design, build, and implement management systems for clients — end to end
**Output:** Policies, registers, plans, frameworks, documented information — all audit-ready

**Active Implementation Clients:**

| Client | Standards | Status |
|--------|-----------|--------|
| MSD-MOI | ISO 22301 · ISO 31000 | Active implementation |
| UACC Taif Plant | ISO 50001 | Active implementation |
| SAGCO | ISO 45001 · ISO 14001 | Active implementation |
| Al-Ahsa Municipality | ISO 27001 | Implementation |

**Implementation Output Rules:**
- Solve, build, and deliver — not just identify gaps
- Every deliverable is complete, print-ready, and audit-defensible
- Match client's document code system exactly
- Isolate each client: never mix formulas, colors, vocabulary, or styles between clients

## Active Clients — Full Detail

Each client is fully isolated. Claude loads only the relevant client context for the task at hand. Never cross-contaminate data, formulas, visual identity, or vocabulary between clients.

### Client 1 — MSD-MOI (General Directorate of Medical Services)

**Role:** Lead Implementer
**Standards:** ISO 22301 · ISO 31000
**Language:** Full Arabic MSA · ISO clause refs in English · Risk IDs in English
**Doc Code Prefix:** MSD-MOI-GRC-

**Active Deliverables:**

| Deliverable | Doc Code | Format | Status |
|-------------|----------|--------|--------|
| Corporate Risk Register (146 entries) | MSD-MOI-GRC-RR-001 | Excel .xlsx | Live — Arabic |
| Enterprise Risk & Resilience Strategy 2026–2028 | MSD-MOI-GRC-STRAT-001-v5.0 | Word .docx | Approved |
| BIA Workbook (30 processes) | MSD-MOI-GRC-BIA-001 | Excel .xlsx | Active |
| BCM Forms Workbook (21 forms) | MSD-MOI-GRC-BCM-001 | Excel .xlsx | Active |
| Business Continuity Plan | MSD-MOI-GRC-BCP-001 | Word .docx | Arabic — ISO 22301 |

**Key BIA Processes:** EMR · Pharmacy · Lab · Radiology · Network · Billing
**BCM Context:** 5 operational scenarios · phased response plans · 12-month 6-phase roadmap
**Aligned to:** DGA Qiyas + NCA ECC + NRC framework

**Risk Formulas — NEVER change:**

| Formula | Expression |
|---------|------------|
| Latent Risk | S = O × Q |
| Residual Risk | V = S × (1 − U/4) |
| Priority Score | Cascades from _Data sheet |
| Treatment Lookup | VLOOKUP by Risk ID |

**Visual Identity — STRICT:**

| Element | Spec |
|---------|------|
| Primary Headers | #004D26 Dark Green |
| Accents | #C8A96E Gold |
| Secondary Elements | #1A3A5C Navy |
| Data Rows | Alternating light green |
| Layout | A4 · Repeating headers · RTL Arabic |

### Client 2 — UACC (Umm Alqura Cement Company — Taif Plant)

**Role:** Lead Implementer
**Standard:** ISO 50001:2018 (EnMS)
**Language:** English technical · Arabic where specified
**Doc Code Prefix:** UACC-EnMS-
**Source Documents:** UACC-EnMS-ROR-01 · UACC-L2-P-01_05

**Active Deliverables:**

| Deliverable | Doc Code | Format | Detail |
|-------------|----------|--------|--------|
| EnMS Risk & Opportunity Register | UACC-EnMS-ROR-01 | Excel .xlsx | 6 sheets · 14 risks · 19 opportunities |
| SEU Controls Documentation | UACC-EnMS-SEU-01 | Word .docx | Clause 8.1 — operational controls |
| Energy Review Report | UACC-EnMS-ERR-01 | Word .docx | Clause 6.3 — consumption analysis |

**Domain Vocabulary — preserve exactly, never translate:** SEU · EnPI · EnB · VFD · DCS · ALARP · SEEC

**Risk Formulas:**

| Formula | Expression |
|---------|------------|
| EnMS Risk Rating | L × S |
| EnMS Risk Level | Nested IF on rating score |

### Client 3 — SAGCO (Saudi Arabian Glass Company)

**Role:** Lead Implementer
**Standards:** ISO 45001 · ISO 14001 (cert scope), ISO 50001 (certified 2024), ISO 9001 (monitor), ISO 37001 (reference)
**Status:** Active implementation — Stage 2 certification pending (Q2/Q3 2026)
**Language:** English technical
**Doc Code Prefix:** SAGCO-IMS-
**Dashboard:** https://sagcodrv-ux.github.io/sagco-im/
**Site:** Jeddah Industrial City Phase 4 — ~800 direct + 100+ contractors, 24/7, 3 shifts, 5 furnaces (F1–F5)
**Certification Body:** TÜV Austria (our CB)

**Certification Status:**

| Standard | Stage 1 | Stage 2 | Status |
|----------|---------|---------|--------|
| ISO 45001:2018 | Q1 2026 ✅ | Q2 2026 ⚠️ | **3 blockers remain** |
| ISO 14001:2015 | Q1 2026 ✅ | Q2 2026 ⚠️ | Concurrent with 45001 |
| ISO 50001:2018 | 2024 ✅ | Surveillance ongoing | Cert held |
| ISO 9001:2015 | — | — | Monitoring only |
| ISO 37001:2016 | — | — | Reference framework, not cert scope |

**⚠️ 3 URGENT Actions Blocking Stage 2 Certification:**

| # | Item | Ref | Owner |
|---|------|-----|-------|
| 1 | Emergency drill 2026 OVERDUE — furnace blowback + gas leak scenarios required | MOC-07 | CEO approval required |
| 2 | Fire extinguisher 2026 inspection MISSING | HS-04 / R-S-04 | IMS Champion |
| 3 | Group A programme sign-off pending GM | I-17, RM-04 | GM |

**Dashboard Metrics (live):**

| Domain | Count | Key Detail |
|--------|-------|------------|
| Risk Register | 54 entries | 2 Critical, 27 High, 17 Medium, 4 Low |
| Compliance Register | 65 obligations | 68% compliant — 3 urgent gaps |
| Objectives & KPIs | 22 objectives | 3 on track, 2 urgent (OBJ-12 F2, OBJ-14 F4) |
| Context Register | 73 records | 29 external (PESTLE), 28 internal, 16 interested parties |
| MOC Register | ~10–15 entries | MOC-07 pending immediate |
| Energy (Q1 2026) | Ongoing | Facility SPC 562.9 kWh/t (✓ ≤565), GHG 615 kgCO₂e/t (↑ 25 above target) |
| Checklist | 61 items | 66% weighted completion |
| PESTLE/SWOT | 38 + 51 | 14 threats, 14 weaknesses (2 critical), 12 opportunities, 11 strengths |

**Dashboard Pages:**

| Page | URL Path | Purpose |
|------|----------|---------|
| Executive Dashboard | `/sagco-im/` | Summary KPIs, risk distribution, objectives status, urgent items |
| Risk Register | `/sagco-im/risk-register.html` | 54 entries — OHS, Env, Energy, Sustainability, Social, Opportunity |
| Compliance Register | `/sagco-im/compliance.html` | 65 obligations — legal, regulatory, voluntary |
| Objectives & KPIs | `/sagco-im/objectives.html` | 22 objectives with KPI tracking |
| Context Register | `/sagco-im/context.html` | 73 records — PESTLE, internal, interested parties |
| MOC Register | `/sagco-im/moc.html` | Management of Change — 7 change types |
| Energy Planning | `/sagco-im/energy.html` | SEU register, EnPI performance, ECMs |
| Scope & Process Map | `/sagco-im/scope.html` | IMS scope, 16-process PDCA map, exclusions |
| Annual Context Review Checklist | `/sagco-im/checklist.html` | 61 items across 13 sections |
| Risk Methodology | `/sagco-im/methodology.html` | WI-RA-01 — 5×5 L×S matrix, HIRA, hierarchy of controls |
| PESTLE & SWOT | `/sagco-im/pestle-swot.html` | 38 PESTLE → 51 SWOT items |

**Domain Vocabulary — preserve exactly, never translate:**

| Term | Meaning |
|------|---------|
| SHC | Specific Heat Consumption (kcal/kg) |
| EnB | Energy Baseline |
| EnPI | Energy Performance Indicator |
| SEU | Significant Energy Use |
| SPC | Specific Power Consumption (kWh/tonne) |
| GHG | Greenhouse Gas (kgCO₂e/tonne) |
| HFO | Heavy Fuel Oil |
| LPG | Liquefied Petroleum Gas |
| HIRA | Hazard Identification and Risk Assessment |
| PTW | Permit to Work |
| MOC | Management of Change |
| ECM | Energy Conservation Measure |
| NPV / IRR / CAPEX | Net Present Value / Internal Rate of Return / Capital Expenditure |
| SEET | Significant Energy Efficiency Tactic |
| IMS Champion | System owner — primary contact for all IMS documentation |

**Document Codes Observed:**
- L4-430-RC-01 — IMS top-level
- L4-IMS-410-WI-04 — Work instruction
- SAGCO-IMS-CKL-001 — Annual context review checklist
- SAGCO-IMS-WI-RA-01 — Risk assessment methodology work instruction

**Risk Methodology (WI-RA-01):**
- 5×5 matrix — Score = L × S (confirmed)
- 5 risk types: OHS, Environmental, Energy, Sustainability, Social (plus Opportunity)
- HIRA with mandatory assessment fields + Hierarchy of Controls
- Category-specific scoring override rules
- Mandatory 30-day review on any trigger event
- Assessor competence requirements defined

**Energy Context:**
- 5 furnaces (F1–F5), primarily HFO + LPG (84.3% thermal share)
- Q1 2026: 250.09 GWh total, 17.01M SAR cost (+22.5% vs 2025)
- ECM 1 — Recuperative → Regenerative conversion (F3, F4, F5): NPV 457M SAR, IRR 17.4%, payback 7.3 yrs, CAPEX 220M SAR
- F4 SHC Deviation +119 kcal/kg above target — URGENT RCA due Jun 2026
- F2 Decision required Aug 2026 — URGENT

**IMS Process Architecture (PDCA):**
- **Plan:** Context & stakeholder analysis → Risk & aspect identification → Objective setting → Legal compliance → Energy planning (SEU)
- **Do:** Operational controls (PTW) → Emergency response drills → Training → Procurement controls → MOC implementation
- **Check:** Monitoring & measurement → Stack & EnPI monitoring → Compliance evaluation → Internal audit → KPI dashboard
- **Act:** NC & CAPA → Management Review (9.3) → Continual improvement → Annual context review → Objective revision

**Active Deliverables:** TBD — populate when next SAGCO deliverable starts.

### Client 4 — Al-Ahsa Municipality

**Role:** Lead Implementer
**Standard:** ISO 27001:2022 (ISMS)
**Language:** Arabic MSA · ISO refs and control IDs in English
**Doc Code Prefix:** AHSA-ISMS-

**Risk Formulas:**

| Formula | Expression |
|---------|------------|
| Risk Score | L × I |
| Risk Level | Nested IF on risk score |

**Active Deliverables:** TBD — populate when next Al-Ahsa deliverable starts.
Template: Active Deliverables · Asset Register · SoA · Risk Assessment methodology

### Client 5 — MOC (Ministry of Culture)

**Role:** Lead Implementer
**Standard:** ISO 37001:2016 (Anti-Bribery Management System)
**Status:** Pending — governance-focused engagement
**Language:** Arabic MSA · ISO clause refs in English
**Doc Code Prefix:** MOC-ABMS-
**Note:** Governance is specialized — may need extra research before starting deliverables.

Template — populate when confirmed.

## ComplianceHub Platform

**Repo:** https://github.com/0zMaradny/ComplianceHub
**Type:** Full-stack — FastAPI backend + Vite/React frontend
**Status:** Active development via opencode

### Architecture

| Layer | Technology | Port |
|-------|------------|------|
| Backend | Python · FastAPI · Uvicorn | 8000 |
| Frontend | React · Vite · Tailwind CSS | 5173 |
| AI Router | 5-tier: Claude (Anthropic) → OpenRouter frontier → OpenRouter strong → Groq → Local Qwen3-4B | — |
| Local AI | llama.cpp server — qwen3-4b.gguf (preferred) / qwen-3b.gguf / qwen-0.5b.gguf | 8080 |
| Data | clause_data.py — data-driven clause database for all 14 standards | — |
| Doc Gen | python-docx with TÜV branding (TUV_BLUE #003D7A · TUV_RED #C00000) | — |
| PDF | LibreOffice headless conversion | — |

### Supported Standards (14)

| Key | Standard | Structure |
|-----|----------|-----------|
| iso_9001 | ISO 9001:2015 — Quality | HLS Clause 1-10 |
| iso_14001 | ISO 14001:2015 — Environmental | HLS Clause 1-10 |
| iso_45001 | ISO 45001:2018 — OH&S | HLS Clause 1-10 |
| iso_50001 | ISO 50001:2018 — Energy | HLS Clause 1-10 |
| iso_13485 | ISO 13485:2016 — Medical Devices | HLS Clause 1-10 |
| iso_27001 | ISO 27001:2022 — InfoSec | HLS + Annex A (4 themes, 93 controls) |
| iso_20000 | ISO 20000-1:2018 — Service Mgmt | HLS Clause 1-10 |
| iso_22301 | ISO 22301:2019 — Business Continuity | HLS Clause 1-10 |
| iso_37301 | ISO 37301:2021 — Compliance | HLS Clause 1-10 |
| iso_42001 | ISO 42001:2023 — AI Management | HLS + Annex A (9 objectives, 40 controls) |
| iso_30401 | ISO 30401:2018 — Knowledge Mgmt | HLS Clause 1-10 |
| iso_27701 | ISO 27701:2025 — Privacy | HLS + PIMS-specific clauses |
| iso_31000 | ISO 31000:2018 — Risk (Guidelines) | Framework: Principles, Framework, Process |
| iso_10002 | ISO 10002:2018 — Complaints | Framework: 5 sections |

### Output Documents (8 types)

| Type | Label |
|------|-------|
| Audit_Plan_Stage_1 | Audit Plan Stage 1 |
| Audit_Plan_Stage_2 | Audit Plan Stage 2 |
| Participation_List | Participation List |
| Audit_Report | Audit Report |
| ISO_Checklist | ISO Checklist |
| Certificate_Text | Certificate Text |
| TNL | Test / Nonconformity Log |
| Certificate | Certificate |

### AI Task Routing (5-tier fallback chain)

All tasks route through the same 5-tier chain — no per-task provider assignment:

```
Tier 0: Claude (Anthropic) — premium, best quality (skipped if ANTHROPIC_API_KEY truncated)
Tier 1: OpenRouter frontier — nemotron_ultra, qwen3_coder, kimi_k26, owl_alpha (4 parallel, all free)
Tier 2: OpenRouter strong — nemotron_super, llama_70b, qwen3_next, hermes_405b (4 parallel, all free)
Tier 3: Groq — groq_llama (Llama 3.3 70B, ~800 t/s, free)
Tier 4: Local AI — qwen3-4b / qwen-3b / qwen-0.5b (Q4_K_M GGUF, localhost:8080)
Fallback: Offline generator — static templates, instant, no AI needed
```

### AI Content Modes

| Mode | API Key | Provider Chain | Speed | Quality |
|------|---------|----------------|-------|---------|
| Free Cloud | OPENROUTER_API_KEY + GROQ_API_KEY set | OpenRouter frontier → strong → Groq → local | Fast | Good (Nemotron 550B best) |
| Local AI | No keys (llama.cpp running) | local only | Slow | ~40s/doc qwen3-4b |
| Offline | No keys, no model | offline generator only | Instant | Professional templates |

### Key Backend Modules

| Module | Purpose |
|--------|---------|
| `app/config.py` | ISO_STANDARDS, STANDARD_FAMILIES, OUTPUT_DOCUMENTS, DOC_LABELS, paths |
| `app/main.py` | FastAPI app, upload/generate endpoints, background job processing, progress_store |
| `app/services/clause_data.py` | Data-driven clause database: HLS_CORE, CLAUSE_8 variants, ANNEX_A_27001/42001, PIMS_27701, FRAMEWORK_31000/10002, SUPPORTING_STANDARDS_EVIDENCE |
| `app/services/ai_pipeline.py` | Shared context extraction + AI doc generation with family context injection + few-shot examples |
| `app/services/ai/router.py` | 5-tier fallback chain: Claude → OpenRouter frontier → OpenRouter strong → Groq → Local. ThreadPoolExecutor + cache + rate limiter + health tracking |
| `app/services/ai/debugger.py` | Autodebugger class: input validation, output validation, placeholder detection, self-heal retries |
| `app/services/ai/anthropic_provider.py` | Claude API client (Tier 0, premium, key truncated = fast-fail skipped) |
| `app/services/ai/openrouter_provider.py` | OpenRouter client for all frontier + strong free models (Tiers 1+2) |
| `app/services/ai/groq_provider.py` | Groq client — Llama 3.3 70B (Tier 3, ~800 t/s) |
| `app/services/ai/local_provider.py` | Local llama.cpp provider — qwen3-4b/qwen-3b/qwen-0.5b (Tier 4) |
| `app/services/ai/model_registry.py` | 14 models: PREMIUM + FRONTIER_FREE + STRONG_FREE + GROQ_FREE + LOCAL_FREE |
| `app/services/ai/rate_limiter.py` | Per-provider sliding window rate limiter |
| `app/services/ai/json_utils.py` | JSON extraction utilities |
| `app/services/offline_generator.py` | Dynamic standard-specific checklists — no hardcoded ISO 9001 sections |
| `app/services/document_generator.py` | python-docx document generation with TÜV branding, RTL support, page numbers, landscape mode |
| `app/services/file_parser.py` | DOCX + TXT parsing, audit notes extraction, manday data extraction via regex |
| `app/services/pdf_converter.py` | LibreOffice headless PDF conversion |
| `app/services/template_manager.py` | Template upload and management |
| `app/services/doc_schemas.py` | Document schemas/validation |
| `app/services/manday_calculator.py` | IAF MD 5 manday reference for all 14 standards |
| `app/services/surveillance.py` | 3-year surveillance cycle management |

### Frontend Pages

| Page | Purpose |
|------|---------|
| Dashboard | Stats overview, compliance health ring, quick actions, tunnel URL |
| Audit | Upload audit notes + manday → select standards → generate 8 docs |
| AuditPlan | Stage 1/2 audit plan generation |
| Compliance | Framework viewer with pillar-based checklists |
| Projects | Project management and tracking |
| History | Past audits and document history |
| Analytics | Compliance analytics and dashboards |
| Surveillance | 3-year surveillance cycle management |
| Chat | AI chat interface |
| Templates | Document template management |
| Reporting | Reports and exports |

### TÜV Branded Templates (in repo)

17 template files in `backend/templates/04_03_26_consense_audit_documentation/`:
- BSO_Audit_Questionaire_ISO22301.docx
- AQC Form (ENG-Form FM-BA-ZET-MS-All_AQC_EN).docx
- Audit Plan forms (FM-TAGMBH-MSZ-001 through MSZ-038)
- ISO 27001 Audit Checklist (.xlsx)
- Certificate Text, Participation List, Remote Audit Risk Analysis templates

### Key Commands

```bash
# Run full stack
bash run.sh                    # offline mode
bash run.sh --local-ai        # with local AI

# Backend only
cd backend && uvicorn app.main:app --port 8000
cd backend && python -m compileall . -q       # syntax check
cd backend && python -m pyflakes app/          # zero errors mandatory

# Frontend only
cd frontend && npm run dev
cd frontend && npm run build
cd frontend && npm run lint

# Local AI (llama.cpp)
/opt/llama-server/llama-server -m /opt/llama-server/models/qwen3-4b.gguf -c 32768 -t 4 -b 2048 --mlock --port 8080
/opt/llama-server/llama-server -m /opt/llama-server/models/qwen-3b.gguf -c 8192 -t 4 -b 2048 --mlock --port 8080
/opt/llama-server/llama-server -m /opt/llama-server/models/qwen-0.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080

# API smoke test
curl http://localhost:8000/api/standards
```

### AI Keys (backend/.env)
- OPENROUTER_API_KEY (prefix: sk-or-v1) — free frontier + strong models
- GROQ_API_KEY (prefix: gsk_) — Llama 3.3 70B, free
- ANTHROPIC_API_KEY (prefix: sk-ant-api) — Claude Sonnet 4, paid (truncated key = fast-fail skip)
- HF_API_KEY (prefix: hf_) — HuggingFace free inference (optional backup)

### Git
- Auto-pushes every commit on main via .git/hooks/post-commit
- PAT token stored in ~/.git-credentials

### Python Dependencies
fastapi · uvicorn · python-docx · python-multipart · openpyxl · lxml · pydantic · aiofiles
fpdf2 · pypdf2 · requests · psycopg2-binary · pytest · httpx · pyflakes

## Legacy React Artifact (TÜV Austria Hellas)

**File:** TUV_Platform_Fixed.jsx — 1,983 lines · 157 KB
**Type:** React artifact — Claude.ai sandbox (legacy, superseded by ComplianceHub)
**Status:** Archived — replaced by full-stack ComplianceHub

### Artifact Sandbox Hard Rules (for reference)

- NO import from firebase — use window.storage only
- NO Gemini API (generativelanguage.googleapis.com)
- NO process.env · NO require() · NO useTransition (React 18 only)
- YES AI: https://api.anthropic.com/v1/messages — no key needed in artifact
- YES Model: claude-sonnet-4-6 — response: content[0].text
- YES CDN: cdnjs.cloudflare.com for mammoth + XLSX
- YES Excel: window.XLSX.utils.aoa_to_sheet + writeFile — NOT HTML blob
- YES Checklist IDs: deterministic — std-clause_with_underscores
- YES setAuditProjects called ONCE after loop — never inside forEach

## ISO 42001 — 24 Mandatory Documents Reference

Full official list. Platform checklist + templates cover all 24. Items 13, 22, 23 covered via HLS_CLAUSES (applied to all standards).

| # | Document | Clause | Platform Coverage |
|---|----------|--------|-------------------|
| 1 | AIMS Scope | 4.1 | Checklist + Template |
| 2 | Interested Parties & Requirements | 4.2 | Checklist + Template |
| 3 | AI System Inventory | A.3.2 | Checklist + Template |
| 4 | AI Context & Applicability Assessment | 4.1 & 4.3 | Checklist + Template |
| 5 | AI Policy | 5.2 & A.2 | Checklist + Template |
| 6 | Roles & Responsibilities | 5.3 & A.3.2 | Checklist + Template |
| 7 | AI Risk Assessment Methodology | 6.1.2 | Checklist + Template |
| 8 | AI Risk Register & Treatment Plan | 6.1.3 | Checklist + Template |
| 9 | AI Objectives & Plans | 6.2 | Checklist + Template |
| 10 | Statement of Applicability (SoA) | 6.1.3 | Checklist + Template |
| 11 | Competency & Awareness Records | 7.2 | Checklist + Template |
| 12 | AI Communication Process | 7.4 | Checklist + Template |
| 13 | Document Control Procedure | 7.5 | HLS + baseTemplate |
| 14 | AI Lifecycle Management Procedure | A.6 | Checklist + Template |
| 15 | Human Oversight Mechanism | A.6.2 | Checklist + Template |
| 16 | AI Incident Management Procedure | A.9 | Checklist + Template |
| 17 | AI Change Management Procedure | A.9 | Checklist + Template |
| 18 | Monitoring & Validation Records | 9.1 | Checklist + Template |
| 19 | Internal Audit Procedure & Reports | 9.2 | HLS + baseTemplate |
| 20 | Management Review Records | 9.3 | HLS + Template |
| 21 | KPI & Monitoring Metrics | 9.1 | Checklist + Template |
| 22 | Nonconformity & Corrective Action | 10.2 | HLS + Template |
| 23 | Continual Improvement Records | 10.1 | HLS + Template |
| 24 | AI Impact Assessment (AIA) — ISO/IEC 42005 (7 steps) | 6.1.4 & A.5.5 | Checklist (7 items) + 3 Templates |

**ISO/IEC 42005 Note:** The AI Impact Assessment (Doc #24) follows the ISO/IEC 42005 7-step process:
Step 1 Context → Step 2 Stakeholders → Step 3 Impact Categories (10) → Step 4 Severity×Likelihood → Step 5 Controls → Step 6 Residual Impact → Step 7 Governance Decision (Accept/Reject/Escalate).

10 mandatory impact categories: Fairness · Privacy · Safety · Security · Explainability · Accountability · Societal · Economic · Legal · Human Autonomy.

## Technical Defaults
→ See MEMORY.md — Confirmed Preferences section. Single source of truth.

## Claude Prompt Quick Reference (Merged Anatomy Framework)

12-part merged framework from Ruben Hassid + serveai.ig. Always include ROLE + TASK + OUTPUT + PUSH. Add others as needed. Full detail: Skill 15 and Agent 8.

**ROLE (🔴 always):**
Act as [expert persona with specific credentials and priority].
*Example: Act as a Senior Lead Auditor at a UKAS-accredited CB. Prioritize clause-level precision over general advice.*

**TASK (🔴 always):**
[ACTION VERB] [specific deliverable] so that [recipient does X].
Scope: [in/out]. Length: [exact]. Format: [table/Word/Excel].

**CONTEXT (🔵 situation + files):**
Here's what I know:
- Client: [name] | Standard: [ISO xxx] | Doc code: [prefix]
- Team / constraints: [relevant situation]
- Key risks: [what could go wrong with this deliverable]
Read Context.md — identity, clients, formulas, standards
Read Memory.md — confirmed preferences and corrections

**REASONING (🟡 for complex outputs):**
The goal is [crisp one-sentence description of ideal output].
By [approach / method], the output will be [quality standard].
Ask yourself: does every section serve the goal? If not, cut it.

**REFERENCE (🟢 for style matching):**
Match the rhythm of: [paste or upload reference]
Always [pattern 1 — structure]. Always [pattern 2 — tone].

**SUCCESS BRIEF (🟡 for client deliverables):**
Recipient reaction: [they approve / sign / reply / book]
Voice: [paste 2–3 sentences in target voice]
Tone: [2 words — direct, technical]
Success means: [the one action they take after reading]

**RULES (🩷 always positive):**
- Plain English — short, concrete, specific
- No leverage · no utilize · no synergies
- [Arabic MSA · ISO refs in English · doc code format]

**TOOLS (🟣 when action needed):**
Web search: [exact query + "verify with 2+ sources"]
Drive: [exact filename]. Calendar: [exact action + contact].

**CONVERSATION (🔴 if ambiguous):**
Before executing, ask about anything unclear.
Match my answers exactly. Do not fill gaps silently.

**PLAN (🔵 for multi-step work):**
List the 3 rules from my context that matter most for this task.
Then give your execution plan in 5 steps maximum.

**OUTPUT (🔴 always):**
Present as [format]. For each section:
- Content: [what goes in]
- Owner / clause: [reference]
- Quality check: [how to verify it's right]

**PUSH (🟢 always last):**
Go beyond the basics. Ship it like a real client deliverable.
Think before answering (maximum reasoning).

## Personal Finance & Lifestyle Context

| Area | Details |
|------|---------|
| Cashback Platforms | STC Pay · Urpay · Noon KSA · Amazon KSA |
| Banking | Al-Rajhi · SNB (Saudi National Bank) |
| Travel Routes | Riyadh (RUH) to Alexandria (HBE/ALY) |
| Airlines | Saudia · Flynas · EgyptAir |
| Faith Trips | Makkah & Madinah — value + quiet options preferred |
| Interests | Formula 1 · Android development · Rugby · Reading · Information Security |
