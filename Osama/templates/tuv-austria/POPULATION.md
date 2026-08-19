# TÜV Austria — Template Population Reference
_How every CB form gets populated — field by field, Projects vs Audit Clients._
_Version: 1.0 · August 2026_

---

## Core Principle

**Templates are immutable.** Every population creates a NEW file. The original 10 CB forms in `templates/tuv-austria/` are never modified.

**Population mode depends on client category:**

| Mode | What It Means | Who Gets It |
|------|---------------|-------------|
| **RICH** | Most fields auto-filled from client profile + prior deliverables. Few flags for manual input. | Projects with existing deliverables (MSD-MOI → BIA, SAGCO → prior checklist) |
| **SEMI** | Some fields auto-filled from profile. Many flagged for manual input. | Projects without prior deliverables (Al-Ahsa → new implementation) |
| **SPARSE** | Structure only. Org name + standard + date pre-filled. All content fields flagged. | Audit Clients (daily by calendar) |

---

## Data Sources — Where Population Data Comes From

| Source | Available For | What It Provides |
|--------|--------------|------------------|
| `clients/<NAME>.md` | Projects only | Full profile: name, standards, scope, language, contacts, KSA regulatory, visual identity, doc code prefix |
| CONTEXT.md Projects table | Projects only | Status, formula, prefix, language, sensitivity |
| CONTEXT.md Audit Clients table | Audit Clients only | One-line: name, standard, audit type, date, auditor, sensitivity |
| BIA Workbook (prior) | MSD-MOI (BCMS) | Critical processes, MTD, RTO, RPO, dependencies, recovery strategies |
| Risk Register (prior) | All Projects | Risk scoring methodology, risk count, top risks |
| Prior Checklist (prior) | Projects with surveillance | Evidence mapping from previous audit cycle |
| Prior Audit Report (prior) | Projects with surveillance | Structure, findings format, NC history |
| `clients/KSA-REGULATORY.md` | HIGH clients + NCA/SAMA/PDPL | Regulatory control cross-maps, mandatory requirements |
| TÜV Default Lookup | All clients | Default complexity factors, standard clause lists, manday tables, accreditation bodies |
| Manual input (auditor) | All clients | Employee count, specific sites, interview schedule, findings |

---

## Population Pipeline — Step by Step

### Workflow Order (Mandatory)

```
Step 1: Manday Calculation (03)
Step 2: Questionnaire (01 or 02) — sent to client before audit
Step 3: Audit Plan (04 or 05) — auditor prepares
Step 4: Audit Checklist (08 or 09) — working document during audit
Step 5: Participation List (07) — filled at opening meeting
Step 6: Audit Report (06) — completed after audit
Step 7: Certificate (10) — issued after positive decision
```

**Never skip a step. Never reorder.** Steps 1–3 are pre-audit. Step 4 is during audit. Steps 5–7 are post-audit.

---

## Per-Template Population Details

---

### Template 01 — Questionnaire (BCM)
**File:** `01-questionnaire-bcm.docx`
**Standard:** ISO 22301 (BCMS only)
**When:** Pre-audit — sent to client organization to complete

#### Field Map

| Field | Data Source | Project (MSD-MOI) | Audit Client |
|-------|-----------|-------------------|--------------|
| Organization name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar entry |
| Organization scope | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Ask auditor |
| BCP objectives | BIA Workbook | ✅ From BIA: critical processes | ⚠️ Flag — client to complete |
| Critical processes | BIA Workbook | ✅ Auto-fill: 30 processes with MTD/RTO | ⚠️ Flag — client to complete |
| MTD / RTO / RPO | BIA Workbook | ✅ Auto-fill from BIA Table sheet | ⚠️ Flag — client to complete |
| Dependencies | BIA Workbook | ✅ From Process Detail sheet | ⚠️ Flag — client to complete |
| Key contacts | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Flag — client to complete |
| Recovery strategies | BIA Workbook | ✅ From BIA Table | ⚠️ Flag — client to complete |
| Doc code prefix | CONTEXT.md | ✅ `MSD-MOI-GRC-` | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ #004D26 / #C8A96E | ✅ TÜV default #003D7A / #C00000 |
| Language | `clients/<NAME>.md` | Arabic MSA | English (default) |

#### Population Mode
- **MSD-MOI:** RICH — BIA Workbook provides most fields. Only ~20% need client input.
- **Audit Client:** SPARSE — org name + standard only. ~80% flagged for client.

#### AutoClaw Instructions
```
1. Load clients/MSD-MOI.md → extract name, scope, contacts, language
2. Load BIA Workbook → extract critical processes, MTD, RTO, RPO, dependencies, recovery strategies
3. Copy 01-questionnaire-bcm.docx → save as MSD-MOI-GRC-Q01-BCM-YYYY-MM-DD.docx
4. Pre-fill: org name, scope, critical processes, MTD/RTO/RPO, dependencies, recovery, contacts
5. Apply visual identity: #004D26 headers, #C8A96E accents
6. Flag fields needing client input: BCP objectives, additional contacts, organizational chart
7. Queue for client completion → then auditor review
```

---

### Template 02 — Questionnaire (General)
**File:** `02-questionnaire-general.docx`
**Standard:** All standards (universal)
**When:** Pre-audit — sent to client organization

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Organization name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Organization scope | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Ask auditor |
| Standards held/certified | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Management system scope | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Flag |
| Number of sites | `clients/<NAME>.md` | ✅ Auto-fill (if in profile) | ⚠️ Ask auditor |
| Employee count | Manual / prior questionnaire | ⚠️ From prior if available | ⚠️ Ask auditor |
| Key contacts | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Flag |
| Existing certifications | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Flag |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |
| Language | `clients/<NAME>.md` | As per profile | English (default) |

#### Population Mode
- **Projects:** SEMI — core org info from profile, but employee-specific data needs client input.
- **Audit Client:** SPARSE — org name + standard only.

---

### Template 03 — Manday Calculation
**File:** `03-manday-calc.xlsx`
**Standard:** All standards (universal)
**When:** First step — determines audit duration
**⚠️ CRITICAL:** This must be completed first. It drives the entire audit schedule.

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Standard(s) | `clients/<NAME>.md` or calendar | ✅ Auto-fill | ✅ From calendar |
| Employee count | Manual input | ⚠️ Ask (or from prior) | ⚠️ Ask auditor |
| Complexity factors | TÜV lookup + client profile | ✅ From profile + lookup | ✅ TÜV default lookup |
| Site count | `clients/<NAME>.md` | ✅ From profile (if available) | ⚠️ Ask auditor |
| Risk level | Client risk formula | ✅ Calculate using client formula | ⚠️ Use TÜV default risk table |
| Calculated mandays | Formula in Excel | ✅ Auto-calculate | ✅ Auto-calculate |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |

#### Population Mode — Formula-Driven
- **MSD-MOI:** RICH — V=S×(1−U/4) feeds complexity. Employee count from profile.
- **Al-Ahsa:** RICH — L×I formula. Employee count from profile.
- **SAGCO:** RICH — L×S / L×S×R. Employee count from profile.
- **Audit Client:** SPARSE — standard + TÜV default lookup. Must ask employee count.

#### Special Rules
- Multi-standard audits (e.g., SAGCO 45001+14001+50001): mandays are **additive** per standard, then apply reduction factor for integrated audits
- HIGH sensitivity clients: manday calc must route through Claude/Cline — never cloud platforms

---

### Template 04 — Audit Plan (General)
**File:** `04-audit-plan-ims.docx`
**Standard:** IMS (ISO 9001+14001+45001) and General
**When:** After manday calc — auditor prepares the plan

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Client name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Standards in scope | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Audit dates | Calendar / CONTEXT.md | ✅ From calendar | ✅ From calendar |
| Audit team | Manual (auditor assigns) | ⚠️ From prior plan if surveillance | ⚠️ Manual |
| Audit scope | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Ask auditor |
| Sites to visit | `clients/<NAME>.md` | ✅ From profile | ⚠️ Ask auditor |
| Interview schedule | Prior plan / manual | ⚠️ From prior if surveillance | ⚠️ Manual |
| Clause coverage | Standard clause list | ✅ Auto-generate from standard | ✅ Auto-generate |
| Manday result | Template 03 output | ✅ Carry forward | ✅ Carry forward |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |
| Language | `clients/<NAME>.md` | As per profile | English (default) |

#### Population Mode
- **SAGCO (IMS):** RICH — scope, sites, standards all from profile. Prior plan from Stage 1.
- **Audit Client:** SPARSE — name + standard + date. Plan structure is standard, but specifics are manual.

---

### Template 05 — Audit Plan (ISMS)
**File:** `05-audit-plan-isms.docx`
**Standard:** ISMS (ISO 27001)
**When:** After manday calc — ISMS-specific planning

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Client name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Scope statement | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ Ask auditor |
| SoA reference | Prior SoA / client | ✅ From prior SoA if available | ⚠️ Flag |
| Audit dates | Calendar | ✅ From calendar | ✅ From calendar |
| Audit team | Manual | ⚠️ From prior if surveillance | ⚠️ Manual |
| Annex A controls to audit | SoA / standard | ✅ From SoA — applicable controls only | ✅ Standard Annex A list |
| Interview schedule | Prior plan / manual | ⚠️ From prior if surveillance | ⚠️ Manual |
| NCA ECC overlay | `clients/KSA-REGULATORY.md` | ✅ If HIGH/gov → add 114 controls | ⚠️ Auto-detect by client type |
| SAMA CSF overlay | `clients/KSA-REGULATORY.md` | ✅ If financial sector | ⚠️ Auto-detect |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |

#### Special — Regulatory Overlay Detection

AutoClaw checks these conditions and adds control layers:

| Condition | Overlay | Added To |
|-----------|---------|----------|
| Client is KSA government entity | NCA ECC (114 controls) | Audit Plan + Checklist |
| Client is bank/insurance/finance | SAMA CSF (6 domains) | Audit Plan + Checklist |
| Client handles personal data in KSA | PDPL (12 requirements) | Audit Plan + Checklist |
| Client is government digital service | DGA Qiyas V5.0 (8 dimensions) | Audit Plan + Checklist |
| Client uses AI systems | SDAIA AI Ethics + GenAI | Audit Plan + Checklist |

**Detection method:** Check `clients/<NAME>.md` KSA Regulatory Requirements section. For Audit Clients: classify sensitivity at arrival — HIGH → assume NCA ECC + PDPL.

---

### Template 06 — Audit Report
**File:** `06-audit-report.docx`
**Standard:** All standards
**When:** After audit — the main deliverable
**⚠️ MOST IMPORTANT TEMPLATE** — goes to CB decision body

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Client name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Standard(s) | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Scope | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ From audit plan |
| Audit dates | Calendar | ✅ From calendar | ✅ From calendar |
| Audit team | Audit plan | ✅ Carry from plan | ✅ Carry from plan |
| Findings | **Manual — entered during/after audit** | ⚠️ Auditor fills | ⚠️ Auditor fills |
| Positive observations | **Manual** | ⚠️ Auditor fills | ⚠️ Auditor fills |
| NC summary | **Manual** (from checklist) | ⚠️ Auditor fills | ⚠️ Auditor fills |
| Certification recommendation | **Manual** (auditor decision) | ⚠️ Auditor fills | ⚠️ Auditor fills |
| Prior NC follow-up | Prior audit report | ✅ From surveillance report | N/A (first audit) |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |

#### Population Mode
- **Both:** STRUCTURE-ONLY for findings — these come from the audit itself.
- **Projects:** Get branded headers + prior NC history + scope from profile.
- **Audit Clients:** Get standard structure + TÜV branding.

#### Quality Gate Emphasis
Template 06 must pass ALL Quality Gates (G1–G10) with zero exceptions:
- **G1 Completeness:** No blank findings, no TBD severity
- **G2 Accuracy:** Clause refs match standard, evidence is specific
- **G6 Client Isolation:** No references to other clients' findings
- **G10 Audit-Defensibility:** Every finding traceable to clause + evidence

---

### Template 07 — Participation List
**File:** `07-participation-list.docx`
**Standard:** All audits
**When:** Day of audit — filled during opening meeting

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Client name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Audit date | Calendar | ✅ From calendar | ✅ From calendar |
| Auditor name | CONTEXT.md / calendar | ✅ From calendar | ✅ From calendar |
| Attendees — name | **Manual** (filled at meeting) | ⚠️ From prior list if repeat client | ⚠️ Blank |
| Attendees — title | **Manual** | ⚠️ From prior list | ⚠️ Blank |
| Attendees — department | **Manual** | ⚠️ From prior list | ⚠️ Blank |
| Attendees — signature | **Manual** (handwritten) | ⚠️ Blank | ⚠️ Blank |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |

#### Population Mode
- **Projects with prior audits:** SEMI — known regular attendees pre-filled.
- **Audit Clients:** SPARSE — blank attendee table.

---

### Template 08 — Audit Checklist (ISMS)
**File:** `08-checklist-isms.xlsx`
**Standard:** ISO 27001 (ISMS)
**When:** During audit — the working document

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Clause ref | ISO 27001 standard | ✅ Auto-generate | ✅ Auto-generate |
| Requirement text | ISO 27001 standard | ✅ Auto-generate | ✅ Auto-generate |
| Evidence expected | Standard guidance | ✅ Auto-generate | ✅ Auto-generate |
| Evidence found | **Manual** (auditor fills) | ⚠️ From prior if surveillance | ⚠️ Blank |
| Compliant (Y/N/Partial) | **Manual** | ⚠️ From prior if surveillance | ⚠️ Blank |
| NC severity | **Manual** | ⚠️ Blank | ⚠️ Blank |
| NCA ECC control ref | `clients/KSA-REGULATORY.md` | ✅ If gov → add column | ⚠️ Auto-detect |
| SAMA CSF control ref | `clients/KSA-REGULATORY.md` | ✅ If financial → add column | ⚠️ Auto-detect |
| PDPL mapping | `clients/KSA-REGULATORY.md` | ✅ If PDPL applicable → add column | ⚠️ Auto-detect |
| SDAIA AI mapping | `clients/KSA-REGULATORY.md` | ✅ If AI → add column | ⚠️ Auto-detect |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |

#### Special — Checklist Structure

| Sheet | Content |
|-------|---------|
| Dashboard | Compliance % by clause, NC count, progress |
| Checklist | Main working sheet — clause by clause |
| NCA ECC Overlay | (if applicable) 114 controls mapped to Annex A |
| Regulatory Summary | (if applicable) Cross-framework compliance status |
| _Lists | Dropdown data validation |

#### Population Mode
- **Al-Ahsa:** RICH — prior checklist evidence carries forward. NCA ECC overlay added.
- **Audit Client:** STANDARD — clause list auto-generated. Evidence columns blank. Regulatory overlay added if HIGH/gov.

---

### Template 09 — Audit Checklist (Combined)
**File:** `09-checklist-ims.xlsx`
**Standard:** IMS (ISO 9001+14001+45001)
**When:** During audit — the working document

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Clause ref | Combined ISO standards | ✅ Auto-generate (3 standards merged) | ✅ Auto-generate |
| Requirement text | Combined standards | ✅ Auto-generate | ✅ Auto-generate |
| Evidence expected | Standard guidance | ✅ Auto-generate | ✅ Auto-generate |
| Evidence found | **Manual** | ⚠️ From prior if surveillance | ⚠️ Blank |
| Compliant | **Manual** | ⚠️ From prior | ⚠️ Blank |
| NC severity | **Manual** | ⚠️ Blank | ⚠️ Blank |
| Standard tag (QMS/EMS/OH&SMS) | Auto | ✅ Auto-tag per clause | ✅ Auto-tag |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | CONTEXT.md Visual Identity | ✅ Client colors | ✅ TÜV default |

#### Population Mode
- **SAGCO:** RICH — prior checklist carries forward. 3-standard merged view.
- **Audit Client:** STANDARD — merged clause list. Evidence blank.

---

### Template 10 — Certificate Text
**File:** `10-certificate.docx`
**Standard:** All standards
**When:** After positive certification decision — last step

#### Field Map

| Field | Data Source | Project | Audit Client |
|-------|-----------|---------|--------------|
| Client name | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Standard(s) | `clients/<NAME>.md` | ✅ Auto-fill | ✅ From calendar |
| Scope statement | `clients/<NAME>.md` | ✅ Auto-fill | ⚠️ From audit report |
| Issue date | **Manual** (cert decision date) | ⚠️ Manual | ⚠️ Manual |
| Expiry date | Calculated (issue + 3 years) | ✅ Auto-calculate | ✅ Auto-calculate |
| Certificate number | **Manual** (CB assigns) | ⚠️ Manual | ⚠️ Manual |
| Accreditation bodies | Fixed: SAAC + Austrian + Hellas | ✅ Always these 3 | ✅ Always these 3 |
| Doc code prefix | CONTEXT.md | ✅ Auto-fill | ⚠️ Ask auditor |
| Header branding | TÜV Austria branding | ✅ TÜV branding | ✅ TÜV branding |

#### ⚠️ Critical Rule
**Accreditation is ALWAYS:** SAAC (Saudi Accreditation) + Austrian Accreditation + Hellas Accrediting.
**Never UKAS.** (Previous mistake — corrected in August 2026.)

---

## Standard → Template Selection Matrix

| Standard | Questionnaire | Plan | Checklist | Special |
|----------|--------------|------|-----------|---------|
| ISO 27001 (ISMS) | 02 (General) | 05 (ISMS) | 08 (ISMS) | NCA ECC overlay if gov |
| ISO 22301 (BCMS) | 01 (BCM) | 04 (General) | 08 (ISMS) adapted | BIA pre-fill if available |
| IMS (9001+14001+45001) | 02 (General) | 04 (IMS) | 09 (Combined) | Multi-standard merge |
| ISO 50001 (EnMS) | 02 (General) | 04 (General) | 09 (Combined) adapted | EnMS vocabulary |
| ISO 42001 (AIMS) | 02 (General) | 05 (ISMS) adapted | 08 (ISMS) adapted | SDAIA overlay |
| ISO 20000-1 (ITSMS) | 02 (General) | 05 (ISMS) adapted | 08 (ISMS) adapted | — |
| ISO 31000 (Risk) | 02 (General) | 04 (General) | — | Advisory only |
| ISO 37301 (CMS) | 02 (General) | 04 (General) | 09 (Combined) adapted | — |

**Always for all standards:** 03 (Manday) · 06 (Report) · 07 (Participation) · 10 (Certificate)

---

## AutoClaw Template Population — Full Automation Script

### Trigger
- **Primary:** On audit session start (manual trigger or calendar event)
- **Secondary:** On "populate template" command

### Decision Flow

```
TRIGGER: Audit session starting
  │
  ├─ 1. Read CONTEXT.md → identify client
  │   ├─ Client in Projects table? → PROJECT MODE
  │   └─ Client in Audit Clients table? → AUDIT CLIENT MODE
  │
  ├─ 2. Identify standard(s) → select templates from matrix above
  │
  ├─ 3. PROJECT MODE:
  │   ├─ Load clients/<NAME>.md → extract profile data
  │   ├─ Load visual identity from CONTEXT.md
  │   ├─ Check for prior deliverables (BIA, risk register, SoA, prior checklist)
  │   ├─ Check KSA-REGULATORY.md for applicable regulatory overlays
  │   └─ Pre-fill all RICH/SEMI fields → flag SPARSE fields
  │
  ├─ 4. AUDIT CLIENT MODE:
  │   ├─ Read one-line entry from CONTEXT.md Audit Clients table
  │   ├─ Classify sensitivity (HIGH if gov/PDPL → assume NCA ECC)
  │   ├─ Apply TÜV default lookup tables
  │   └─ Pre-fill SPARSE fields (name, standard, date) → flag all content fields
  │
  ├─ 5. For each template in workflow order:
  │   ├─ Copy template → save as new file with doc code prefix
  │   ├─ Apply visual identity (headers, accents, fonts)
  │   ├─ Pre-fill available fields
  │   ├─ Add regulatory overlays if applicable
  │   ├─ Flag fields needing manual input
  │   └─ Run Skill 21 (Language Gate) on pre-filled text
  │
  ├─ 6. Generate population report:
  │   ├─ Per template: fields pre-filled / fields flagged / confidence level
  │   ├─ Regulatory overlays applied (if any)
  │   └─ Platform routing for review (HIGH → Claude/Cline, MEDIUM → all)
  │
  └─ 7. Queue populated files for auditor review
```

### Population Confidence Report (example output)

```
Template Population Report — MSD-MOI · ISO 22301 · 2026-08-10
═══════════════════════════════════════════════════════════════

Template 01 (BCM Questionnaire):  RICH — 12/15 fields pre-filled (80%)
  ✅ Auto-filled: org name, scope, critical processes (30), MTD/RTO/RPO, dependencies, contacts
  ⚠️ Flagged: BCP objectives (client input), additional contacts, organizational chart

Template 03 (Manday Calc):        RICH — 5/7 fields pre-filled (71%)
  ✅ Auto-filled: standard, complexity, risk level (V=S×(1−U/4)), manday result
  ⚠️ Flagged: employee count (verify with client), site count

Template 04 (Audit Plan):         SEMI — 6/10 fields pre-filled (60%)
  ✅ Auto-filled: client, standards, scope, sites, clause coverage, manday
  ⚠️ Flagged: audit team, interview schedule, opening/closing meeting times

Template 08 (ISMS Checklist):     RICH — clause list generated, 8 prior evidence items carried forward
  ✅ Auto-generated: 114 clauses + NCA ECC overlay (114 controls)
  ⚠️ Evidence fields: blank for auditor to fill

Regulatory overlays: NCA ECC ✅ · PDPL ✅ · DGA Qiyas ✅
Platform routing: HIGH → Claude/Cline/Hermes ONLY
Visual identity: #004D26 / #C8A96E (MSD-MOI)
Language: Arabic MSA (ISO refs in English)
```

---

## Naming Convention for Populated Files

**Pattern:** `<PREFIX>-<TEMPLATE-CODE>-<DATE>.<ext>`

| Template | Code | Example (MSD-MOI) | Example (Audit Client) |
|----------|------|--------------------|------------------------|
| 01 Questionnaire BCM | Q01 | `MSD-MOI-GRC-Q01-2026-08-10.docx` | `CLIENT-GRC-Q01-2026-08-10.docx` |
| 02 Questionnaire Gen | Q02 | `MSD-MOI-GRC-Q02-2026-08-10.docx` | `CLIENT-GRC-Q02-2026-08-10.docx` |
| 03 Manday Calc | MD | `MSD-MOI-GRC-MD-2026-08-10.xlsx` | `CLIENT-GRC-MD-2026-08-10.xlsx` |
| 04 Audit Plan IMS | AP-IMS | `SAGCO-IMS-AP-IMS-2026-08-10.docx` | `CLIENT-IMS-AP-IMS-2026-08-10.docx` |
| 05 Audit Plan ISMS | AP-ISMS | `AHSA-ISMS-AP-ISMS-2026-08-10.docx` | `CLIENT-ISMS-AP-ISMS-2026-08-10.docx` |
| 06 Audit Report | AR | `MSD-MOI-GRC-AR-2026-08-10.docx` | `CLIENT-GRC-AR-2026-08-10.docx` |
| 07 Participation List | PL | `MSD-MOI-GRC-PL-2026-08-10.docx` | `CLIENT-GRC-PL-2026-08-10.docx` |
| 08 Checklist ISMS | CL-ISMS | `AHSA-ISMS-CL-ISMS-2026-08-10.xlsx` | `CLIENT-ISMS-CL-ISMS-2026-08-10.xlsx` |
| 09 Checklist Combined | CL-IMS | `SAGCO-IMS-CL-IMS-2026-08-10.xlsx` | `CLIENT-IMS-CL-IMS-2026-08-10.xlsx` |
| 10 Certificate | CERT | `MSD-MOI-GRC-CERT-2026-08-10.docx` | `CLIENT-GRC-CERT-2026-08-10.docx` |

**Audit Client prefix:** Ask auditor for doc code prefix. If not provided, use `<CLIENT-NAME>-<STD>-`.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Client profile not found | AUDIT CLIENT MODE — proceed with SPARSE population |
| BIA Workbook not found | Flag questionnaire fields — client must complete manually |
| Prior checklist not found | Generate standard clause list — no evidence carry-forward |
| KSA-REGULATORY.md missing | Skip regulatory overlays — log warning |
| Visual identity not in CONTEXT.md | Use TÜV default (#003D7A / #C00000) |
| Employee count unknown for manday | Flag as CRITICAL — manday calc cannot complete without it |
| Standard not in selection matrix | Use General templates (02, 04, 09) — log warning |
| HIGH client on cloud platform | BLOCK population — route to Claude/Cline/Hermes ONLY |

---

## Model-Agnostic Population — Works on Any Platform

**Problem:** The AutoClaw instructions above assume script execution. But on Qwen, Gemini, Z.ai Chat, or Hermes, you can't run python-docx/openpyxl directly. You need a **text-first approach** that works everywhere.

**Solution:** Two population paths — pick based on your platform:

| Path | Platform | How It Works | Output |
|------|----------|-------------|--------|
| **SCRIPT** | Cline, AutoClaw, Z.ai Agent (with tools) | Python script reads template file, populates, saves as .docx/.xlsx | Ready-to-use file |
| **TEXT** | Qwen, Gemini, Z.ai Chat, Hermes, MiMo, Phone | Generate structured Markdown matching template structure → paste into template manually | Structured text to paste |

### How to Choose Your Path

```
Can you run Python scripts?
  ├─ YES (Cline terminal / AutoClaw / Z.ai Agent with tools) → SCRIPT PATH
  └─ NO (Qwen web / Gemini / Z.ai Chat / Hermes / Phone) → TEXT PATH
```

---

### TEXT PATH — Per-Template Population Prompts

Copy the prompt for the template you need. Paste it into any model. Fill in [BRACKETS] with your client data.

#### Prompt for Template 01 — BCM Questionnaire

```
I need to populate the TÜV Austria BCM Questionnaire (ISO 22301) for this client:

Client: [CLIENT NAME]
Standard: ISO 22301
Doc Code: [PREFIX]-GRC-Q01-[DATE]
Language: [Arabic MSA / English]

Pre-fill data I have:
- Organization scope: [SCOPE]
- Critical processes: [LIST FROM BIA, or "need from client"]
- MTD/RTO/RPO: [FROM BIA, or "need from client"]
- Key dependencies: [FROM BIA, or "need from client"]
- Recovery strategies: [FROM BIA, or "need from client"]
- Key contacts: [FROM CLIENT PROFILE, or "need from client"]

For each field I marked "need from client", leave it as [TO BE COMPLETED BY CLIENT] with a note explaining what information is needed.

Output the populated questionnaire as structured text matching the TÜV Austria BCM Questionnaire format. Use formal CB language. ISO clause references in English. Apply client visual identity: [PRIMARY COLOR] headers, [ACCENT COLOR] accents.
```

#### Prompt for Template 02 — General Questionnaire

```
I need to populate the TÜV Austria General Questionnaire for this client:

Client: [CLIENT NAME]
Standard(s): [LIST STANDARDS]
Doc Code: [PREFIX]-GRC-Q02-[DATE]
Audit Type: [Initial / Surveillance / Recertification]
Language: [Arabic MSA / English]

Pre-fill data:
- Organization scope: [SCOPE or "need from client"]
- Number of sites: [COUNT or "need from client"]
- Employee count: [COUNT or "need from client"]
- Key contacts: [LIST or "need from client"]
- Existing certifications: [LIST or "need from client"]

For fields I don't have data for, mark [TO BE COMPLETED BY CLIENT].

Output as structured text matching TÜV Austria General Questionnaire format. Formal CB language.
```

#### Prompt for Template 03 — Manday Calculation

```
Calculate audit mandays for this client:

Client: [CLIENT NAME]
Standard(s): [LIST — e.g., ISO 27001, or ISO 9001+14001+45001 as IMS]
Employee count: [NUMBER — ASK IF UNKNOWN]
Number of sites: [NUMBER]
Risk level: [USE CLIENT FORMULA RESULT, or "TÜV default"]
Complexity: [FROM PROFILE, or "standard"]

Rules:
- Multi-standard: add mandays per standard, then apply integrated audit reduction factor
- HIGH sensitivity: this calculation must NOT be shared on cloud platforms

Output a manday calculation table with: Standard | Base Mandays | Complexity Factor | Adjusted Mandays | Total. Include the TÜV Austria reduction factor for integrated audits if multiple standards.
```

#### Prompt for Template 04 — Audit Plan (General/IMS)

```
Create an audit plan for this IMS/General audit:

Client: [CLIENT NAME]
Standard(s): [e.g., ISO 9001+14001+45001]
Doc Code: [PREFIX]-AP-IMS-[DATE]
Audit dates: [DATES]
Audit team: [NAMES or "to be assigned"]
Scope: [FROM CLIENT PROFILE or "to be defined"]
Sites: [LIST or "to be confirmed"]
Manday result: [FROM TEMPLATE 03]

Generate the audit plan structure:
1. Opening meeting (date, time, attendees)
2. Document review (which clauses, which documents)
3. On-site audit (interviews, observations, evidence collection)
4. Closing meeting (date, time, findings summary)

Include clause coverage table: Standard | Clauses | Audit Focus
Formal CB language. Apply client visual identity: [PRIMARY COLOR] / [ACCENT COLOR].
```

#### Prompt for Template 05 — Audit Plan (ISMS)

```
Create an ISMS audit plan for this client:

Client: [CLIENT NAME]
Standard: ISO 27001:2022
Doc Code: [PREFIX]-AP-ISMS-[DATE]
Audit dates: [DATES]
Scope: [FROM CLIENT PROFILE or "to be defined"]
SoA reference: [FROM PRIOR SoA, or "to be reviewed"]
Annex A controls: [FROM SoA — list applicable, or "all 93 controls"]
Manday result: [FROM TEMPLATE 03]

KSA Regulatory check:
- Is this a government entity? → Add NCA ECC overlay (114 controls)
- Is this financial sector? → Add SAMA CSF overlay (6 domains)
- Does it handle personal data? → Add PDPL overlay (12 requirements)
- Is it a digital government service? → Add DGA Qiyas overlay
- Does it use AI? → Add SDAIA overlay

Generate audit plan with regulatory overlay section if applicable.
Formal CB language.
```

#### Prompt for Template 06 — Audit Report

```
Create the audit report structure for this client:

Client: [CLIENT NAME]
Standard(s): [LIST]
Doc Code: [PREFIX]-AR-[DATE]
Audit dates: [DATES]
Audit team: [FROM PLAN]

Generate the report structure (I will fill in findings during/after audit):
1. Executive Summary
2. Scope & Objectives
3. Standards Referenced
4. Findings Table: Clause | Finding | Evidence | Severity | Requirement
5. Positive Observations
6. NC Summary (by severity)
7. Recommendations
8. Certification Recommendation

Prior NC follow-up: [FROM SURVEILLANCE REPORT, or "N/A — initial audit"]

CRITICAL: This template goes to the CB decision body. Every finding must be traceable to a clause + evidence. No TBD severity. No cross-client references.
```

#### Prompt for Template 07 — Participation List

```
Create a participation list for this audit:

Client: [CLIENT NAME]
Doc Code: [PREFIX]-PL-[DATE]
Audit date: [DATE]
Lead auditor: [NAME]

Generate the structure:
- Opening meeting: date, time, location
- Attendee table: Name | Title | Department | Signature
- Closing meeting: date, time, location
- Attendee table: Name | Title | Department | Signature

Prior known attendees (if repeat client): [LIST FROM PRIOR, or "blank — fill at meeting"]
```

#### Prompt for Template 08 — ISMS Checklist

```
Generate the ISO 27001:2022 audit checklist for this client:

Client: [CLIENT NAME]
Doc Code: [PREFIX]-CL-ISMS-[DATE]
Standard: ISO 27001:2022

Generate a clause-by-clause checklist with these columns:
Clause | Requirement | Evidence Expected | Evidence Found | Compliant (Y/N/Partial) | NC Severity | Notes

Cover all clauses: 4 (Context), 5 (Leadership), 6 (Planning), 7 (Support), 8 (Operation), 9 (Performance), 10 (Improvement), plus Annex A controls.

KSA Regulatory overlays (add columns if applicable):
- NCA ECC: Add "NCA ECC Control Ref" column mapping 114 controls to Annex A
- SAMA CSF: Add "SAMA CSF Domain" column if financial sector
- PDPL: Add "PDPL Article" column if personal data handler
- SDAIA: Add "SDAIA Principle" column if AI systems

Prior evidence (if surveillance): [FROM PRIOR CHECKLIST, or "blank — fill during audit"]

Also generate: Dashboard sheet with Compliance % by clause, NC count, Progress tracker.
```

#### Prompt for Template 09 — Combined IMS Checklist

```
Generate the combined IMS audit checklist (ISO 9001+14001+45001) for this client:

Client: [CLIENT NAME]
Doc Code: [PREFIX]-CL-IMS-[DATE]
Standards: ISO 9001:2015 + ISO 14001:2015 + ISO 45001:2018

Generate a merged clause-by-clause checklist with these columns:
Clause | Standard (QMS/EMS/OH&SMS) | Requirement | Evidence Expected | Evidence Found | Compliant | NC Severity | Notes

Merge the three standards' clause structures. Tag each clause with its standard.
Common clauses (e.g., 4 Context, 5 Leadership, 6 Planning, 7 Support) show once with all three standards tagged.
Standard-specific clauses show separately.

Prior evidence (if surveillance): [FROM PRIOR CHECKLIST, or "blank — fill during audit"]

Also generate: Dashboard sheet with Compliance % by standard, NC count, Progress tracker.
```

#### Prompt for Template 10 — Certificate Text

```
Generate the certificate text for this client:

Client: [CLIENT NAME]
Standard(s): [LIST]
Doc Code: [PREFIX]-CERT-[DATE]
Scope: [FROM CLIENT PROFILE or "from audit report"]
Issue date: [CERT DECISION DATE]
Expiry date: [ISSUE DATE + 3 YEARS]
Certificate number: [CB ASSIGNS — leave as [TO BE ASSIGNED BY CB]]

Accreditation bodies (ALWAYS these three, never UKAS):
1. SAAC — Saudi Accreditation
2. Austrian Accreditation
3. Hellas Accrediting

Generate formal certificate text. TÜV Austria branding.
```

---

### SCRIPT PATH — For Cline / AutoClaw / Z.ai Agent

**When you can execute Python**, use this approach:

```
1. Read the template file from templates/tuv-austria/
2. Run python-docx (for .docx) or openpyxl (for .xlsx) to populate
3. Save as new file with doc code prefix
4. Run Skill 21 + Skill 22 quality gates
5. Save to workspace
```

**Python script template** (adapt for each template):

```python
# --- CONFIG ---
CLIENT_NAME = "[CLIENT NAME]"
DOC_PREFIX = "[PREFIX]-[CODE]-"
DATE = "2026-08-10"
TEMPLATE_PATH = "templates/tuv-aussia/[template-file]"
OUTPUT_PATH = f"output/{DOC_PREFIX}{DATE}.docx"  # or .xlsx

# --- LOGIC ---
# 1. Load template (python-docx or openpyxl)
# 2. Read client data from CONTEXT.md / clients/<NAME>.md
# 3. Find and replace placeholder fields
# 4. Apply visual identity (header colors, fonts)
# 5. Apply regulatory overlays if applicable
# 6. Save as new file — NEVER modify template
# 7. Run quality gates
```

**Available on:** Cline (terminal), AutoClaw (automated), Z.ai Agent (with tool access)
**NOT available on:** Qwen Studio, Gemini, Z.ai Chat, Hermes, MiMo, Phone

---

### Quick-Start Population Commands (Any Model)

Type these natural-language commands on any platform. The auto-trigger map routes them correctly.

| Command | What It Triggers | Templates Populated |
|---------|-----------------|-------------------|
| `populate MOI BCM` | Template 01 for MSD-MOI | Q01 (BCM Questionnaire) |
| `populate [client] questionnaire` | Template 01 or 02 based on standard | Q01 or Q02 |
| `new audit package for [client]` | Full audit package (all 7 steps) | 03→01/02→04/05→08/09→07→06→10 |
| `manday calc for [client]` | Template 03 only | MD |
| `audit plan for [client]` | Template 04 or 05 based on standard | AP-IMS or AP-ISMS |
| `checklist for [client] [standard]` | Template 08 or 09 based on standard | CL-ISMS or CL-IMS |
| `audit report for [client]` | Template 06 structure | AR |
| `certificate for [client]` | Template 10 | CERT |

**On Qwen/Gemini/Z.ai Chat:** Use the TEXT PATH prompts above.
**On Cline/AutoClaw:** Use the SCRIPT PATH — the command triggers Skill 14 automatically.

---

### Model Compatibility Matrix — Per Template

| Template | .docx/.xlsx | Cline (script) | Qwen/Gemini (text) | Z.ai Agent | Z.ai Chat | Phone |
|----------|------------|----------------|-------------------|------------|-----------|-------|
| 01 BCM Q | .docx | ✅ python-docx + RTL | ✅ TEXT prompt | ✅ Either | ✅ TEXT | ⚠️ Compressed |
| 02 Gen Q | .docx | ✅ python-docx | ✅ TEXT prompt | ✅ Either | ✅ TEXT | ✅ TEXT |
| 03 Manday | .xlsx | ✅ openpyxl + formulas | ✅ TEXT (calculate manually) | ✅ Either | ✅ TEXT | ⚠️ Simple only |
| 04 Plan IMS | .docx | ✅ python-docx | ✅ TEXT prompt | ✅ Either | ✅ TEXT | ✅ TEXT |
| 05 Plan ISMS | .docx | ✅ python-docx + RTL | ✅ TEXT prompt | ✅ Either | ✅ TEXT | ✅ TEXT |
| 06 Report | .docx | ✅ python-docx | ✅ TEXT prompt | ✅ Either | ⚠️ Too long | ❌ Too long |
| 07 Participation | .docx | ✅ python-docx | ✅ TEXT prompt | ✅ Either | ✅ TEXT | ✅ TEXT |
| 08 CL ISMS | .xlsx | ✅ openpyxl + formulas | ✅ TEXT (clause list) | ✅ Either | ⚠️ Too long | ❌ Too long |
| 09 CL IMS | .xlsx | ✅ openpyxl + formulas | ✅ TEXT (clause list) | ✅ Either | ⚠️ Too long | ❌ Too long |
| 10 Certificate | .docx | ✅ python-docx | ✅ TEXT prompt | ✅ Either | ✅ TEXT | ✅ TEXT |

**Key constraints:**
- **Templates 06, 08, 09 are too long for Phone and Z.ai Chat** — they need full clause lists or complete findings. Use Z.ai Agent or Cline instead.
- **Template 01 (BCM) needs RTL support** for Arabic — all models handle Arabic text, but python-docx needs explicit bidi settings (only Cline can set these programmatically).
- **Templates 03, 08, 09 (.xlsx) need openpyxl** for live formulas — on non-Cline platforms, generate the structure as text and build manually, or have Cline create the file.

---

### Prior Deliverable File Paths

When POPULATION.md says "load BIA Workbook" or "load prior checklist", here's where to find them:

| Deliverable | Client | Expected Path | Notes |
|------------|--------|--------------|-------|
| BIA Workbook | MSD-MOI | `output/MSD-MOI-GRC-BIA-*.xlsx` | 30 processes, feeds Template 01 |
| Risk Register | MSD-MOI | `output/MSD-MOI-GRC-RR-*.xlsx` | 146 entries, V=S×(1−U/4) |
| Risk Register | Al-Ahsa | `output/AHSA-ISMS-RR-*.xlsx` | L×I formula |
| Risk Register | SAGCO | `output/SAGCO-IMS-RR-*.xlsx` | L×S / L×S×R formula |
| SoA | Al-Ahsa | `output/AHSA-ISMS-SoA-*.xlsx` | Feeds Template 05 controls |
| Prior Checklist | Any Project | `output/<PREFIX>-CL-*-<PRIOR-DATE>.xlsx` | Surveillance carry-forward |
| Prior Audit Report | Any Project | `output/<PREFIX>-AR-<PRIOR-DATE>.docx` | NC follow-up for Template 06 |
| KSA Regulatory | All | `clients/KSA-REGULATORY.md` | Regulatory overlay source |

**For Audit Clients:** No prior deliverables exist. All content generated fresh from TÜV defaults.

---

_Last updated: 2026-08-09 · POPULATION v1.1 · Model-agnostic population + TEXT/SCRIPT paths + quick-start commands + prior deliverable paths_
