# ComplianceHub ↔ Template Population — Enhancement Plan
_Version: 2.0 · August 2026 · Updated with real template analysis_
_Answers: Is ComplianceHub similar to Template Population? What gaps exist? What enhancements finalize everything?_

---

## Question 1: Is ComplianceHub Similar to Template Population & Audit Package Generation?

### Short Answer: NO — They Are Complementary, Not Similar

ComplianceHub and Template Population/Audit Package Generation are **two different layers** that serve different purposes but MUST connect. Think of it as:

| Dimension | ComplianceHub (Web App) | Template Population (Knowledge System) |
|-----------|------------------------|---------------------------------------|
| **What it is** | A running software application (FastAPI + React) | A documented process + field maps in Markdown files |
| **Where it lives** | Code repo (`backend/`, `frontend/`) | Knowledge workspace (`templates/tuv-austria/POPULATION.md`) |
| **Who uses it** | Auditors via browser UI | AI agents (OWL) via knowledge file reads |
| **Output** | Interactive screens, API responses, generated files | Pre-filled .docx/.xlsx files, population confidence reports |
| **Data flow** | Database → API → UI → User | Client profiles → AI reasoning → Populated templates |
| **Current state** | Design system defined (DESIGN.md) but **no code yet** | Fully documented (POPULATION.md = 43KB) but **no automation yet** |
| **Platform** | Browser (React + Vite, port 5173) | Any AI model (model-agnostic TEXT + SCRIPT paths) |

### The Real Relationship

```
┌─────────────────────────────────────────────────────────┐
│              WHAT YOU WANT (THE GOAL)                    │
│                                                         │
│   Auditor opens ComplianceHub → Selects client +        │
│   standard → System auto-populates TÜV templates →      │
│   Auditor reviews, edits, exports audit package          │
│                                                         │
└─────────────────────────────────────────────────────────┘

                         ↓ REQUIRES BOTH ↓

┌──────────────────────┐     ┌──────────────────────────┐
│   Template Population │     │    ComplianceHub UI      │
│   (The Brain)        │────→│    (The Interface)       │
│                      │     │                          │
│ • Knows which fields │     │ • Shows populated form   │
│   go where           │     │   to auditor             │
│ • Knows RICH/SEMI/   │     │ • Lets auditor edit     │
│   SPARSE modes       │     │   flagged fields         │
│ • Knows data sources │     │ • Exports final .docx/   │
│ • Knows regulatory   │     │   .xlsx files            │
│   overlays           │     │ • Tracks confidence %    │
│ • Knows quality      │     │ • Saves to audit package │
│   pipeline           │     │                          │
└──────────────────────┘     └──────────────────────────┘
```

**ComplianceHub is the car. Template Population is the engine.** Right now you have the engine design (POPULATION.md) but no engine code, and the car exterior design (DESIGN.md) but no car built. You need BOTH connected.

---

## Question 2: What Gaps Exist? (Deep Analysis)

### Gap 1: No ComplianceHub Code Exists

**Current state:** Only `templates/DESIGN.md` defines the design system (colors, typography, components, anti-patterns). No actual React components, no FastAPI endpoints, no database schema exist.

**What's needed:**
- FastAPI backend with template population endpoints
- React frontend with audit package screens
- Database schema for client data, audit sessions, populated templates
- AI router integration (OpenRouter → Groq → HuggingFace → Local → Offline)

**Impact:** Without this, Template Population only works through AI agent conversations — no persistent UI, no database, no collaboration.

---

### Gap 2: Template Population Has No Automation Script

**Current state:** POPULATION.md (43KB) is an excellent reference — field-by-field maps, data sources, RICH/SEMI/SPARSE modes, model-agnostic prompts. But it's purely documentary. No Python script automates the actual population.

**What's needed:**
- `scripts/populate_template.py` — reads POPULATION.md logic, takes client + standard + mode, outputs populated files
- `scripts/population_engine.py` — core engine that maps fields to data sources
- `scripts/regulatory_overlay.py` — auto-detects and applies NCA ECC, SAMA CSF, PDPL, DGA Qiyas overlays
- `scripts/confidence_report.py` — generates population confidence report per template

**Impact:** Without automation, every template population is a manual AI conversation — slow, inconsistent, no confidence tracking.

---

### Gap 3: No Actual TÜV Template Files (.docx / .xlsx) — ✅ RESOLVED

**Current state:** All 14 TÜV Austria form templates have been uploaded, analyzed, and cataloged. FIELD-MAP.json v2.1 covers all 14 templates.

**Template Inventory (Real Data):**

| ID | Template | File Type | SDT Fields | Tagged (Auto-fill) | Checkboxes (Manual) | Auto-RICH |
|----|----------|-----------|-----------|-------------------|-------------------|-----------|
| T01 | Questionnaire BCM | .docx | 6 | 5 | 0 | 2 |
| T02 | Questionnaire General | .docx | 0* | 0 | 0 | 0 |
| T03 | Manday Calculation | .docx | 3 | 3 | 0 | 3 |
| T04 | Audit Plan (General) | .docx | 16 | 14 | 2 | 12 |
| T05 | Audit Plan (ISMS) | .docx | 16 | 14 | 2 | 12 |
| T06 | Audit Report | .docx | 162 | 23 | 139 | 17 |
| T07 | Participation List | .docx | 68 | 14 | 54 | 12 |
| T08 | Checklist ISO 27001 | .xlsx | 509 rows | N/A | N/A | N/A |
| T09 | Checklist Combined QM+EM+HSE | .docx | 298 | 14 | 284 | 12 |
| T10 | Certificate Text | .docx | 34 | 14 | 18 | 12 |
| T11 | Audit Program | .docx | 0** | 0 | 0 | 0 | 🟠 |
| T12 | Checklist ISO 50001 | .docx | 94 | 14 | 80 | 12 | 🟡 |
| T13 | Auditor Assignment | .docx | 0** | 0 | 0 | 0 | 🟠 |
| T14 | Approval/Release | .docx | 13 | 7 | 0 | 4 | 🟡 |
| | **TOTAL** | | **710** | **108** | **579** | **86** | |

*T02 uses merge fields (<<field>>) instead of SDT content controls.
**T11 and T13 are table-based templates with no SDT form controls — need upgrade.

**Extra Templates (T11-T14) — Workflow Fit:**

| Template | Step | When Used | Quality | Upgrade Needed |
|----------|:----:|-----------|---------|----------------|
| T11 Audit Program | 3.5 | After plan — detailed program with employee/risk calc | 🟠 BASIC | Add SDT form controls + dropdowns |
| T12 Checklist ISO 50001 | 4 | During ISO 50001 (EnMS) audits | 🟡 ADEQUATE | Add header/footer branding |
| T13 Auditor Assignment | 2.5 | Before audit — formal assignment notification | 🟠 BASIC | Add SDT form controls |
| T14 Approval/Release | 6.5 | After audit — CB Phase 1/2/3 evaluation & decision | 🟡 ADEQUATE | Minor — add more dropdowns |

**Key findings:**
- Fields use `tag` (not `alias`) as the identifier — aliases are all empty
- 108 tagged fields are auto-fillable structural fields (dropdowns, combos)
- 579 untagged fields are `☐` checkbox audit ratings (FC/NC/Partial/NA) — always manual
- Shared dropdown vocabularies: audit_method (6 choices), standards (23 choices), audit_type (5 choices), audit_team_role (4 choices)
- FIELD-MAP.json v2.1 built at `templates/tuv-austria/FIELD-MAP.json`
- Individual analyses at `templates/tuv-austria/analyzed/*.json`
- Templates stored at `templates/tuv-austria/files/` with SHA256 immutability hashes

**Still needed:**
- Upgrade T11 (Audit Program) and T13 (Auditor Assignment) with SDT form controls + dropdowns
- Add header/footer branding to T12 (Checklist ISO 50001)
- `markitdown` conversion of each template for AI readability

---

### Gap 4: ComplianceHub and Template Population Are Not Connected

**Current state:** These two systems exist as separate documentation:
- ComplianceHub: `templates/DESIGN.md` + `SOUL.md` rules + `TOOLS.md` infrastructure
- Template Population: `templates/tuv-austria/POPULATION.md` + `skills/AUDIT.md` Skill 14

No bridge connects them. No API endpoint says "populate template X for client Y using mode Z."

**What's needed:**
- ComplianceHub API endpoints that call the population engine
- UI screens that display populated templates with editable flagged fields
- Confidence dashboard showing RICH/SEMI/SPARSE status per template
- Export endpoints that generate final .docx/.xlsx from populated data

**Impact:** Without the bridge, ComplianceHub can't do template population, and Template Population can't reach auditors through a UI.

---

### Gap 5: No Audit Package Assembly Workflow

**Current state:** `skills/AUDIT.md` Skill 14 defines the workflow order (Manday → Questionnaire → Plan → Checklist → Participation → Report → Certificate), and AutoClaw Automation 4 defines the trigger. But there's no actual orchestration code.

**What's needed:**
- `scripts/audit_package.py` — orchestrates all 7 steps in mandatory order
- Package state tracking (which templates populated, which pending, which reviewed)
- Dependency enforcement (can't generate Report before Checklist is done)
- Final package bundling (all files + confidence report + quality gate results)

**Impact:** Without orchestration, auditors must manually track which templates are done and in what order — error-prone and slow.

---

### Gap 6: No Regulatory Overlay Engine

**Current state:** Auto-detection rules exist in POPULATION.md, AUDIT.md, and AutoClaw SETUP.md. But there's no code that actually reads `clients/KSA-REGULATORY.md` and applies overlay columns/sheets to templates.

**What's needed:**
- `scripts/regulatory_engine.py` — reads client sensitivity + sector → applies overlay
- NCA ECC: 114 controls mapped to ISO 27001 Annex A
- SAMA CSF: 6 domains mapped to ISO 27001 + 22301
- PDPL: 12 requirements mapped to ISO 27701
- DGA Qiyas V5.0: 8 dimensions mapped to ISO 27001 + 20000-1
- SDAIA AI Ethics: 7 principles mapped to ISO 42001
- Overlay columns added to Checklist templates
- Overlay rows added to Audit Plan scope section

**Impact:** Without overlay automation, KSA regulatory requirements must be manually cross-referenced every time — major time sink for HIGH government clients.

---

### Gap 7: No Database Schema for Persistent Audit Data

**Current state:** Client profiles are Markdown files. Audit sessions are ephemeral (AI conversation context). No persistent storage for:
- Populated template data (between sessions)
- Audit session state (which templates done, which pending)
- NC tracking (findings across audits)
- CAPA status (correction timeline)
- Confidence scores (per template, per session)

**What's needed:**
- SQLite schema (per SOUL.md: `DATABASE_URL=file:/home/z/my-project/db/custom.db`)
- Tables: clients, audit_sessions, populated_templates, findings, capa_actions, confidence_reports
- FastAPI CRUD endpoints for all tables
- React screens for data management

**Impact:** Without persistence, every session starts from scratch. No audit history. No trend tracking. No CAPA follow-up across sessions.

---

### Gap 8: No Quality Gate Automation in ComplianceHub

**Current state:** Skill 22 (Quality Gates G1–G10) and AutoClaw Automation 3 are documented. But there's no code that runs these gates on populated templates.

**What's needed:**
- `scripts/quality_gates.py` — programmatic G1–G10 checks on populated files
- G1: Scan for placeholders/TBD in pre-filled fields
- G2: Validate clause refs against standard
- G3: Verify naming convention matches
- G4: Check visual identity applied
- G6: Cross-client contamination detection
- G10: Traceability — every pre-filled field links to data source
- Integration with ComplianceHub: gate results shown per template, block export if FAIL

**Impact:** Without automated gates, quality is manual review only — inconsistent and easy to miss.

---

### Gap 9: No AI Router Integration for Population

**Current state:** TOOLS.md defines the AI router stack (OpenRouter → Groq → HuggingFace → Local Qwen3-4B → Offline). POPULATION.md defines model-agnostic TEXT + SCRIPT paths. But there's no code that routes AI calls through this stack.

**What's needed:**
- `scripts/ai_router.py` — implements the fallback chain
- TEXT path: AI generates pre-fill content from copy-paste prompts
- SCRIPT path: Python fills structural fields directly from client profiles
- Hybrid: SCRIPT fills structural fields (name, date, standard), AI fills narrative fields (scope description, risk summary)
- Confidence scoring: SCRIPT-filled = 100%, AI-filled = 80% (review recommended), Manual = 0%

**Impact:** Without AI routing, template population is either fully manual or requires a specific AI model — breaks the model-agnostic principle.

---

### Gap 10: No ComplianceHub Screens for Audit Workflows

**Current state:** DESIGN.md defines component patterns (Data Table, KPI Card, Risk Matrix, Audit Findings Card, CAPA Timeline). But there are no actual screens for:

| Missing Screen | Purpose |
|---------------|---------|
| Client Selector | Pick active Project or Audit Client |
| Standard Selector | Pick ISO standard(s) → auto-select templates |
| Template Dashboard | Show all 10 templates, population status, confidence % |
| Template Editor | Populated template with flagged fields highlighted |
| Audit Package View | All templates for one audit in workflow order |
| NC Tracker | Findings across audits with severity/status |
| CAPA Board | Corrective action timeline with 5-step workflow |
| Regulatory Overlay | Show which overlays applied, toggle on/off |
| Confidence Report | Per-template breakdown of pre-filled vs flagged |
| Export Manager | Generate final .docx/.xlsx, quality gate results |

**Impact:** Without screens, ComplianceHub is just a design document — unusable by auditors.

---

## Enhancement Plan: Everything We Can Build

### Phase 1: Foundation (Build the Engine First)

> **Principle:** Before building the car (ComplianceHub UI), build the engine (population automation). The engine must work standalone — testable via CLI — before wiring to the UI.

#### Enhancement 1.1 — Population Engine Core

**File:** `scripts/population_engine.py`

```python
# Purpose: Core template population engine
# Input: client_name, standard, mode (RICH/SEMI/SPARSE)
# Output: Dict of populated fields per template + confidence scores

# Logic flow:
# 1. Load client profile (clients/<NAME>.md) or audit client row (CONTEXT.md)
# 2. Determine mode (RICH if Project with prior deliverables, SEMI if Project without, SPARSE if Audit Client)
# 3. Select templates based on standard (from POPULATION.md Standard → Template Selection Matrix)
# 4. For each template in workflow order:
#    a. Load field map from POPULATION.md
#    b. SCRIPT path: Fill structural fields from client profile (name, standard, date, org, contacts, formula)
#    c. AI path: Fill narrative fields via AI router (scope descriptions, risk summaries, compliance narratives)
#    d. Apply regulatory overlays (from regulatory_engine.py)
#    e. Calculate confidence score per field
#    f. Flag fields needing manual input
# 5. Generate population confidence report
# 6. Run quality gates (G1, G2, G3, G4, G6, G10)
# 7. Return results
```

**Data sources it reads:**
- `clients/<NAME>.md` — client profile
- `CONTEXT.md` — client routing, formulas, visual identity
- `templates/tuv-austria/POPULATION.md` — field maps (parsed)
- `templates/tuv-austria/FIELD-MAP.json` — **real field inventory (603 SDT fields, 101 auto-fillable, 499 checkboxes)**
- `clients/KSA-REGULATORY.md` — regulatory overlays

**Real field population targets (from FIELD-MAP.json v2.0):**
- **82 fields auto-fillable in RICH mode** (tagged dropdowns: Audit method, Standard 1-5, Audit type, Scopes, Audit team)
- **54 fields auto-fillable in SEMI mode** (subset of RICH — Standard 3-5 drop off)
- **499 checkbox fields always manual** (☐ audit ratings — FC/NC/Partial/NA)
- **23 shared dropdown vocabularies** — standards list (23 ISO options), audit_type (5), audit_method (6), audit_team_role (4)

**Setup steps:**
1. Create `scripts/` directory + `db/` directory
2. Write `population_engine.py` with CLI interface — reads FIELD-MAP.json for actual field tags
3. Implement SCRIPT-path population for tagged dropdown fields (82 in RICH)
4. Implement checkbox field detection (499 fields → flag all as manual)
5. Test with MSD-MOI (RICH mode), Al-Ahsa (SEMI mode), and a sample audit client (SPARSE mode)
6. Verify confidence scores match expected ranges (RICH ≥70%, SEMI 40-69%, SPARSE <40%)

---

#### Enhancement 1.2 — Regulatory Overlay Engine

**File:** `scripts/regulatory_engine.py`

```python
# Purpose: Auto-detect and apply KSA regulatory overlays
# Input: client_name, standard
# Output: List of overlays + control mappings to add to templates

# Detection rules:
# - Government entity / HIGH sensitivity → NCA ECC (114 controls) + PDPL (12 requirements)
# - Financial sector → SAMA CSF (6 domains) + PDPL
# - Digital government service → DGA Qiyas V5.0 (8 dimensions)
# - AI systems → SDAIA AI Ethics (7 principles) + GenAI
# - Check clients/<NAME>.md → KSA Regulatory Requirements section
# - For Audit Clients: HIGH sensitivity → assume NCA ECC + PDPL

# Output per overlay:
# - Framework name
# - Controls/domains list
# - Mapping to ISO clauses
# - Columns/sheets to add to Checklist
# - Scope additions to Audit Plan
```

**Setup steps:**
1. Parse `clients/KSA-REGULATORY.md` for control mappings
2. Write detection logic based on client sensitivity + sector
3. Test: MSD-MOI (government → NCA ECC + PDPL), SAGCO (industrial → none), Al-Ahsa (government → NCA ECC + PDPL)
4. Verify overlay controls map correctly to ISO clauses

---

#### Enhancement 1.3 — Quality Gate Automation

**File:** `scripts/quality_gates.py`

```python
# Purpose: Run G1–G10 quality gates on populated templates
# Input: populated template data + client context
# Output: Pass/fail per gate + detailed findings

# Gates for template population:
# G1 (Completeness): No placeholders/TBD in pre-filled fields
# G2 (Accuracy): Clause refs valid for the standard
# G3 (Consistency): Naming convention <PREFIX>-<CODE>-<DATE>.<ext>
# G4 (Formatting): Visual identity applied (colors, fonts, header)
# G5 (Language): No AI filler, correct language (Arabic/English)
# G6 (Client Isolation): No cross-client data
# G10 (Audit-Defensibility): Every pre-filled field traceable to data source
```

**Setup steps:**
1. Write G1–G10 check functions
2. Test each gate independently
3. Wire into population_engine.py as post-population step
4. Block export if any gate FAIL

---

#### Enhancement 1.4 — Audit Package Orchestrator

**File:** `scripts/audit_package.py`

```python
# Purpose: Orchestrate full audit package assembly in mandatory order
# Input: client_name, standard, mode
# Output: Complete audit package (all populated templates + confidence report + gate results)

# Mandatory workflow order:
# Step 1: Manday Calculation (03) — determines audit duration
# Step 2: Questionnaire (01 or 02) — sent to client before audit
# Step 3: Audit Plan (04 or 05) — auditor prepares after manday
# Step 4: Audit Checklist (08 or 09) — working document during audit
# Step 5: Participation List (07) — filled at opening meeting
# Step 6: Audit Report (06) — completed after audit
# Step 7: Certificate (10) — issued after positive decision

# State tracking:
# - Each template: NOT_STARTED → POPULATED → REVIEWED → APPROVED
# - Dependency: Can't start Step N+1 until Step N is POPULATED
# - Exception: Questionnaire can be skipped for Audit Clients
```

**Setup steps:**
1. Define workflow state machine
2. Write orchestration logic with dependency enforcement
3. Test with full package generation for each mode
4. Generate final package bundle with all files + reports

---

#### Enhancement 1.5 — AI Router

**File:** `scripts/ai_router.py`

```python
# Purpose: Route AI calls through OpenRouter → Groq → HuggingFace → Local → Offline
# Input: prompt, model_preference, timeout
# Output: AI response + model used + confidence

# Fallback chain:
# 1. OpenRouter (8 free models) — primary
# 2. Groq — speed fallback
# 3. HuggingFace — variety fallback
# 4. Local Qwen3-4B — offline fallback
# 5. Pure SCRIPT path — no AI needed, fill from data only

# For template population:
# - SCRIPT path: Fill structural fields (name, date, standard, org) — 100% confidence
# - AI path: Fill narrative fields (descriptions, summaries) — 80% confidence
# - Flag AI-filled fields for manual review
```

**Setup steps:**
1. Write OpenRouter API client
2. Write fallback chain logic
3. Test with each provider
4. Test SCRIPT-only path (no AI needed)

---

#### Enhancement 1.6 — Confidence Report Generator

**File:** `scripts/confidence_report.py`

```python
# Purpose: Generate population confidence report per template per session
# Input: populated template data
# Output: Confidence report with per-field breakdown

# Report format:
# ┌──────────────┬───────────┬──────────┬────────────┐
# │ Template     │ Pre-filled│ Flagged  │ Confidence │
# ├──────────────┼───────────┼──────────┼────────────┤
# │ Q01 (BCM)    │ 18/22     │ 4        │ 82% (RICH) │
# │ MD (Manday)  │ 8/12      │ 4        │ 67% (SEMI) │
# │ AP-ISMS      │ 12/20     │ 8        │ 60% (SEMI) │
# │ CL-ISMS      │ 45/114    │ 69       │ 39% (SPARSE)│
# └──────────────┴───────────┴──────────┴────────────┘
# Overlays: NCA ECC (114 controls) + PDPL (12 requirements)
# Prior deliverables used: BIA Workbook, Risk Register
# Platform routing: HIGH → Claude/Cline
```

**Setup steps:**
1. Write confidence calculation logic
2. Test with RICH/SEMI/SPARSE examples
3. Format as CLI output + JSON for API consumption

---

### Phase 2: Database Schema (Persistence Layer)

#### Enhancement 2.1 — SQLite Database Schema

**File:** `db/schema.sql` + `scripts/db_init.py`

```sql
-- Core tables for ComplianceHub

-- Clients (mirrors CONTEXT.md + clients/<NAME>.md)
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL, -- 'project' or 'audit_client'
    standards TEXT, -- JSON array of standard codes
    status TEXT DEFAULT 'active',
    formula_latent TEXT,
    formula_residual TEXT,
    doc_prefix TEXT,
    language TEXT DEFAULT 'english',
    sensitivity TEXT DEFAULT 'medium', -- 'high', 'medium', 'low'
    visual_primary TEXT,
    visual_accent TEXT,
    profile_path TEXT, -- path to clients/<NAME>.md
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Sessions
CREATE TABLE audit_sessions (
    id INTEGER PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    standard TEXT NOT NULL,
    audit_type TEXT, -- 'initial', 'surveillance', 'recertification'
    session_date DATE,
    population_mode TEXT, -- 'rich', 'semi', 'sparse'
    status TEXT DEFAULT 'in_progress', -- 'in_progress', 'complete', 'archived'
    overall_confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Populated Templates
CREATE TABLE populated_templates (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id),
    template_code TEXT NOT NULL, -- Q01, Q02, MD, AP-IMS, AP-ISMS, AR, PL, CL-ISMS, CL-IMS, CERT
    template_name TEXT NOT NULL,
    workflow_step INTEGER, -- 1-7
    population_status TEXT DEFAULT 'not_started', -- 'not_started', 'populated', 'reviewed', 'approved'
    populated_data TEXT, -- JSON of field values
    flagged_fields TEXT, -- JSON array of field names needing manual input
    confidence_score REAL,
    quality_gate_results TEXT, -- JSON of G1-G10 pass/fail
    output_file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Findings (NCs)
CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id),
    template_code TEXT,
    clause_ref TEXT NOT NULL,
    finding_text TEXT NOT NULL,
    severity TEXT, -- 'major', 'minor', 'observation'
    status TEXT DEFAULT 'open', -- 'open', 'closed', 'verified'
    evidence TEXT,
    capa_id INTEGER REFERENCES capa_actions(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CAPA Actions
CREATE TABLE capa_actions (
    id INTEGER PRIMARY KEY,
    finding_id INTEGER REFERENCES findings(id),
    root_cause TEXT,
    containment TEXT,
    corrective TEXT,
    preventive TEXT,
    effectiveness_verification TEXT,
    current_step INTEGER DEFAULT 1, -- 1-5
    status TEXT DEFAULT 'root_cause', -- 'root_cause', 'containment', 'corrective', 'preventive', 'effectiveness'
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Regulatory Overlays
CREATE TABLE regulatory_overlays (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id),
    framework TEXT NOT NULL, -- 'NCA_ECC', 'SAMA_CSF', 'PDPL', 'DGA_QIYAS', 'SDAIA_AI', 'SDAIA_GENAI'
    controls_count INTEGER,
    controls_data TEXT, -- JSON of control mappings
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Confidence Reports
CREATE TABLE confidence_reports (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES audit_sessions(id),
    report_data TEXT, -- JSON of per-template confidence breakdown
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Setup steps:**
1. Create `db/` directory
2. Write `schema.sql`
3. Write `scripts/db_init.py` — creates DB, seeds from CONTEXT.md client data
4. Test: verify all tables, seed MSD-MOI, Al-Ahsa, SAGCO from their profiles

---

### Phase 3: ComplianceHub Backend (FastAPI)

#### Enhancement 3.1 — FastAPI Application Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + CORS + error handler
│   ├── config.py            # Settings (DB path, AI router config)
│   ├── database.py          # SQLite connection + session management
│   ├── models.py            # SQLAlchemy models (mirror schema.sql)
│   ├── routers/
│   │   ├── clients.py       # Client CRUD endpoints
│   │   ├── sessions.py      # Audit session management
│   │   ├── templates.py     # Template population endpoints
│   │   ├── findings.py      # NC finding CRUD
│   │   ├── capa.py          # CAPA action management
│   │   ├── regulatory.py    # Regulatory overlay endpoints
│   │   ├── quality.py       # Quality gate execution
│   │   └── export.py        # File export (.docx, .xlsx)
│   ├── services/
│   │   ├── population.py    # Population engine (calls scripts/)
│   │   ├── regulatory.py    # Regulatory overlay service
│   │   ├── quality_gates.py # Quality gate service
│   │   ├── ai_router.py     # AI router service
│   │   └── export.py        # Document export service
│   └── schemas/             # Pydantic request/response models
├── requirements.txt
└── tests/
```

**Key API endpoints:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/clients` | List all clients (Projects + Audit Clients) |
| GET | `/clients/{id}` | Get client profile |
| POST | `/sessions` | Create audit session (client + standard) |
| GET | `/sessions/{id}` | Get session status + all templates |
| POST | `/sessions/{id}/populate` | Trigger template population for session |
| GET | `/sessions/{id}/templates` | List all templates with status + confidence |
| GET | `/sessions/{id}/templates/{code}` | Get populated template data |
| PUT | `/sessions/{id}/templates/{code}` | Update populated template (manual edits) |
| POST | `/sessions/{id}/templates/{code}/approve` | Approve template |
| GET | `/sessions/{id}/confidence` | Get confidence report |
| POST | `/sessions/{id}/quality-gates` | Run quality gates |
| GET | `/sessions/{id}/overlays` | Get regulatory overlays |
| POST | `/sessions/{id}/export` | Export final audit package |
| GET | `/findings` | List findings (filterable by session, severity) |
| POST | `/findings` | Create finding |
| PUT | `/findings/{id}` | Update finding |
| GET | `/capa` | List CAPA actions |
| POST | `/capa` | Create CAPA action |
| PUT | `/capa/{id}/advance` | Advance CAPA to next step |

**Setup steps:**
1. Create backend directory structure
2. Write `main.py` with FastAPI app
3. Write database connection layer
4. Write Pydantic schemas
5. Write routers (start with clients + sessions + templates)
6. Wire population engine as service
7. Test all endpoints

---

### Phase 4: ComplianceHub Frontend (React + Vite)

#### Enhancement 4.1 — React Application Structure

```
frontend/
├── src/
│   ├── App.tsx              # Main app with ErrorBoundary
│   ├── main.tsx             # Vite entry
│   ├── api/                 # API client (fetch to FastAPI)
│   ├── components/
│   │   ├── ui/              # shadcn/ui base components
│   │   ├── DataTable.tsx    # Core data table (DESIGN.md spec)
│   │   ├── KPICard.tsx      # KPI card component
│   │   ├── RiskMatrix.tsx   # 5x5 risk matrix
│   │   ├── FindingsCard.tsx # Audit finding card
│   │   ├── CAPATimeline.tsx # CAPA 5-step timeline
│   │   ├── StatusBadge.tsx  # Compliance status badge
│   │   └── ConfidenceMeter.tsx # Confidence % indicator
│   ├── screens/
│   │   ├── Dashboard.tsx         # Main dashboard
│   │   ├── ClientSelector.tsx    # Pick client + standard
│   │   ├── TemplateDashboard.tsx # All 10 templates, status, confidence
│   │   ├── TemplateEditor.tsx    # Edit populated template
│   │   ├── AuditPackageView.tsx  # Full package in workflow order
│   │   ├── FindingsTracker.tsx   # NC findings list
│   │   ├── CAPABoard.tsx         # CAPA timeline board
│   │   ├── RegulatoryOverlay.tsx # Overlay toggle + details
│   │   ├── ConfidenceReport.tsx  # Confidence breakdown
│   │   └── ExportManager.tsx     # Export + quality gate results
│   ├── hooks/               # Custom hooks
│   └── lib/                 # Utilities (sanitizeHtml, XLSX, etc.)
├── package.json
└── vite.config.ts
```

**Design system implementation:**
- All colors from DESIGN.md (TUV Blue #003D7A, TUV Red #C00000, client accents)
- All typography (Inter font, scale from 12px to 32px)
- All spacing (4px base unit, xs through 2xl)
- All components (Data Table, KPI Card, Risk Matrix, Findings Card, CAPA Timeline, Status Badges, Risk Level Badges)
- All anti-patterns enforced (no gradients, no corners >8px, no heavy shadows, no animations on data tables)

**Setup steps:**
1. Create React + Vite project
2. Install shadcn/ui + Tailwind
3. Implement base design tokens (colors, typography, spacing)
4. Build core components from DESIGN.md specs
5. Build screens (start with Dashboard + ClientSelector + TemplateDashboard)
6. Wire API client to FastAPI backend
7. Test all screens with real data

---

### Phase 5: Integration & Automation

#### Enhancement 5.1 — AutoClaw ↔ ComplianceHub Bridge

**Purpose:** AutoClaw Automation 4 (Template Population) triggers ComplianceHub API instead of manual AI conversation.

```python
# AutoClaw trigger: On audit session start
# 1. POST /sessions (create session for client + standard)
# 2. POST /sessions/{id}/populate (trigger population)
# 3. GET /sessions/{id}/confidence (get confidence report)
# 4. Notify auditor: "X templates populated for [CLIENT] — [Y%] pre-filled"
# 5. Auditor opens ComplianceHub → reviews flagged fields → approves
```

**Setup steps:**
1. Update AutoClaw SETUP.md to call ComplianceHub API
2. Test trigger from AutoClaw
3. Verify end-to-end: AutoClaw trigger → API call → population → UI shows results

---

#### Enhancement 5.2 — Gemini Gems ↔ ComplianceHub Bridge

**Purpose:** Gem 1 (Auditor) and Gem 5 (Code) coordinate with ComplianceHub.

```
Gem 1 workflow: Research → Gap analysis → Findings → POST /findings (store in ComplianceHub)
Gem 5 workflow: Feature request → Build → Deploy check → ComplianceHub updated
```

**Setup steps:**
1. Update GEM1_AUDITOR.md with ComplianceHub API integration
2. Update GEM5_CODE.md with ComplianceHub development workflow
3. Test cross-Gem coordination

---

#### Enhancement 5.3 — POPULATION.md → API Schema Auto-Generation

**Purpose:** POPULATION.md field maps automatically generate FastAPI Pydantic schemas and React form components.

```python
# Parse POPULATION.md field maps → Generate:
# 1. Pydantic models for each template's fields
# 2. React form components with correct field types
# 3. Validation rules (required, format, range)
# 4. Flag indicators (which fields need manual input per mode)
```

**Setup steps:**
1. Write POPULATION.md parser
2. Generate Pydantic schemas
3. Generate React form field configs
4. Verify generated code matches manual definitions

---

### Phase 6: Missing ComplianceHub Features (Beyond Template Population)

These are features ComplianceHub needs that go beyond template population — the "hub" in ComplianceHub.

#### Enhancement 6.1 — Audit Dashboard

**Purpose:** Overview of all active audits across all clients.

- Active audit sessions count
- Templates populated today / this week
- Pending reviews (flagged fields awaiting auditor input)
- Quality gate pass/fail rates
- Client-specific views (Projects vs Audit Clients)

---

#### Enhancement 6.2 — NC Tracker (Finding Management)

**Purpose:** Track all non-conformities across audit sessions.

- Finding list with filters: by client, session, standard, severity, status
- Severity badges: Major (red), Minor (yellow), Observation (blue)
- Status workflow: Open → Closed → Verified
- Link findings to CAPA actions
- Clause reference validation
- Export findings report

---

#### Enhancement 6.3 — CAPA Board

**Purpose:** Manage corrective and preventive actions.

- 5-step timeline: Root Cause → Containment → Corrective → Preventive → Effectiveness
- Step status: Completed (green), In-progress (yellow), Pending (gray)
- Due date tracking (30/60/90 day effectiveness verification)
- Link to originating finding
- Progress dashboard

---

#### Enhancement 6.4 — Regulatory Overlay Manager

**Purpose:** Visual management of KSA regulatory overlays.

- Per-client overlay status: which frameworks apply
- Control mapping table: NCA ECC controls → ISO 27001 Annex A
- Toggle overlays on/off for specific audits
- Compliance gap analysis: which controls not yet addressed
- Cross-framework overlap detection (e.g., PDPL overlaps in NCA ECC and SAMA CSF)

---

#### Enhancement 6.5 — Audit Calendar Integration

**Purpose:** Visual calendar of all audits (Projects + Audit Clients).

- Daily/weekly/monthly views
- Drag-and-drop rescheduling
- Auto-classify sensitivity on calendar entry
- Morning briefing generation
- Platform routing display (HIGH → Claude/Cline, MEDIUM → all)

---

#### Enhancement 6.6 — Document Export Manager

**Purpose:** Generate final audit deliverables.

- Export individual templates as .docx/.xlsx
- Export full audit package as ZIP
- Quality gate results attached to export
- Naming convention enforced: `<PREFIX>-<CODE>-<DATE>.<ext>`
- Print-ready formatting (A4, freeze panes, repeat headers)
- Arabic RTL support for government client documents

---

#### Enhancement 6.7 — Client Profile Manager

**Purpose:** Manage client profiles in ComplianceHub (synced with Markdown files).

- View/edit client profiles
- Visual identity preview (colors, fonts)
- Formula display (locked — never editable)
- Sensitivity classification with routing display
- New client onboarding (from TEMPLATE.md)
- Archive/restore clients

---

#### Enhancement 6.8 — SoA (Statement of Applicability) Manager

**Purpose:** Manage ISO 27001 Annex A Statements of Applicability.

- Control list: Applicable / Not Applicable / Excluded (with justification)
- Implementation evidence mapping
- Gap identification: "Applicable" but no evidence
- Regulatory overlay: NCA ECC controls added to SoA
- Export as Excel

---

## Implementation Order (Setup One by One)

### Step-by-step sequence with dependencies:

```
Week 1: Foundation
├── Step 1: Create scripts/ directory + db/ directory
├── Step 2: Write population_engine.py (CLI-only, test with 3 modes)
├── Step 3: Write regulatory_engine.py (test with MSD-MOI, Al-Ahsa, SAGCO)
├── Step 4: Write quality_gates.py (test G1–G10)
├── Step 5: Write confidence_report.py
└── Step 6: Write audit_package.py (orchestrator)

Week 2: Database + Backend
├── Step 7: Create SQLite schema (db/schema.sql)
├── Step 8: Write db_init.py (seed from CONTEXT.md)
├── Step 9: Create FastAPI backend structure
├── Step 10: Write clients + sessions routers
├── Step 11: Write templates router (wire population_engine.py)
├── Step 12: Write findings + capa routers
└── Step 13: Write quality + export routers

Week 3: Frontend
├── Step 14: Create React + Vite project
├── Step 15: Implement design tokens (colors, typography, spacing)
├── Step 16: Build core components (DataTable, KPICard, StatusBadge)
├── Step 17: Build Dashboard + ClientSelector screens
├── Step 18: Build TemplateDashboard + TemplateEditor screens
├── Step 19: Build AuditPackageView screen
└── Step 20: Wire frontend to backend API

Week 4: Integration + Missing Features
├── Step 21: AutoClaw ↔ ComplianceHub bridge
├── Step 22: Gemini Gems ↔ ComplianceHub bridge
├── Step 23: NC Tracker screen
├── Step 24: CAPA Board screen
├── Step 25: Regulatory Overlay Manager screen
├── Step 26: Audit Calendar screen
├── Step 27: Export Manager screen
└── Step 28: End-to-end testing (full audit package generation)

Week 5: Polish + Documentation
├── Step 29: POPULATION.md → API schema auto-generation
├── Step 30: Client Profile Manager screen
├── Step 31: SoA Manager screen
├── Step 32: Arabic RTL testing (MSD-MOI, Al-Ahsa)
├── Step 33: Quality gate integration (block export on FAIL)
├── Step 34: Update all OWL files (SOUL.md, TOOLS.md, etc.)
└── Step 35: Final testing + deployment
```

---

## Summary: What Exists vs What's Needed

| Component | Exists? | What Exists | What's Needed |
|-----------|---------|-------------|---------------|
| **ComplianceHub Design** | ✅ | DESIGN.md (full design system) | Implement as React components |
| **Template Inventory** | ✅ | README.md (10 CB forms listed) | Actual .docx/.xlsx template files |
| **Population Reference** | ✅ | POPULATION.md (43KB, field-by-field) | Python automation scripts |
| **Population Modes** | ✅ | RICH/SEMI/SPARSE defined | Mode detection + execution logic |
| **Regulatory Overlays** | ✅ | Detection rules in AUDIT.md + POPULATION.md | Overlay engine + UI toggle |
| **Quality Gates** | ✅ | G1–G10 defined in Skill 22 | Programmatic gate checks |
| **Audit Package Workflow** | ✅ | Skill 14 + AutoClaw Automation 4 | Orchestration code |
| **AI Router** | ✅ | Stack defined in TOOLS.md | Router implementation |
| **Client Profiles** | ✅ | 4 clients + TEMPLATE.md | Database + CRUD API |
| **ComplianceHub Code** | ❌ | None | FastAPI + React full application |
| **Database** | ❌ | Only .env with DB URL | Schema + initialization |
| **Actual Templates** | ❌ | Names only, no files | 10 .docx/.xlsx template files |
| **Population Scripts** | ❌ | Documentation only | Python automation engine |
| **Audit Dashboard UI** | ❌ | Component specs in DESIGN.md | React screens |
| **NC Tracker** | ❌ | None | Full CRUD + UI |
| **CAPA Board** | ❌ | 5-step process defined | Timeline UI + state machine |
| **Export Manager** | ❌ | Naming convention defined | .docx/.xlsx export endpoints |

---

_This plan bridges ComplianceHub (the interface) with Template Population (the intelligence) into one working system. Every enhancement uses the existing OWL files as source of truth — no reinvention, only automation of what's already documented._
