# CONTEXT.md — Active Clients & Platform
_Version: 4.2 · August 2026_

_Single source of truth for client data, formulas, and visual identity._
_See also: SOUL.md (identity) · PLATFORMS.md (platforms) · TOOLS.md (infrastructure)_

---

## Professional Identity

**Organization:** TÜV Austria GCC — Certification Body
**Accreditation:** SAAC (Saudi Accreditation) · Austrian Accreditation · Hellas Accrediting
**Scheme Head:** ISMS (ISO 27001) · ITSMS (ISO 20000-1) · BCMS (ISO 22301)
**Full Audit Portfolio:** ISO 9001 · 14001 · 45001 · 50001 · 27001 · 42001 · 22301 · 20000-1 · 31000 · 37301
**KSA Frameworks:** NCA ECC · SAMA CSF · DGA Qiyas · CITC CSF

---

## Client Routing — Projects vs Audit Clients

**The two categories that matter in daily work:**

| Category | What | Profile | Duration | Routing |
|----------|------|---------|----------|---------|
| **Projects** | Consultation & implementation engagements | Full `clients/<NAME>.md` | Weeks to months to years | Sensitivity-based (HIGH/MEDIUM) |
| **Audit Clients** | CB certification audits from calendar | One-line entry below | 1–5 days | Classify per client on arrival |

**How to decide:** If you're building deliverables (policies, risk registers, BIA, procedures, CAPA) → it's a Project. If you're auditing (plan → checklist → report → certificate) → it's an Audit Client. Some Projects also need audits — they appear in both tables when relevant.

---

## Projects (Consultation & Implementation)

_Each project has a full profile in `clients/<NAME>.md`. Formulas locked. Visual identity locked. Doc codes locked._

| Client | Standards | Status | Formula | Prefix | Language | Sensitivity |
|--------|-----------|--------|---------|--------|----------|-------------|
| **MSD-MOI** | ISO 22301 · 31000 | Active | S=O×Q · V=S×(1−U/4) | `MSD-MOI-GRC-` | Arabic MSA | HIGH |
| **Al-Ahsa** | ISO 27001 | Active | L×I | `AHSA-ISMS-` | Arabic MSA | HIGH |
| **SAGCO** | ISO 45001 · 14001 · 50001 | Stage 2 pending | L×S · L×S×R | `SAGCO-IMS-` | English | MEDIUM |
| _Add new projects here_ | | | | | | |

**Project lifecycle:**
1. **New project** → Create `clients/<NAME>.md` from TEMPLATE.md → add row above → define formula + prefix + visual identity + sensitivity
2. **Active project** → Build deliverables. Formula never changes. Visual identity never changes.
3. **Project closes** → Move row to Archived table → move profile to `clients/archive/`

**Sensitivity routing for ALL project work:**
- **HIGH (MSD-MOI, Al-Ahsa, any government/PDPL):** Claude phone or Cline local ONLY — never through cloud providers
- **MEDIUM (SAGCO, industrial clients):** All platforms with PII scrub (Skill 39)
- **LOW:** All platforms freely

---

## Audit Clients (Daily by Calendar)

_Changes every day based on Osama's audit calendar. No permanent profiles. No formulas. Uses TÜV templates._

| Client | Standard | Audit Type | Date | Auditor | Sensitivity | Notes |
|--------|----------|------------|------|---------|-------------|-------|
| _Updated daily from calendar_ | | | | | _Classify on arrival_ | Quick-add: `clients/TEMPLATE.md` |

**Daily workflow:**
1. **Morning:** Check calendar → add today's audits to table above → classify sensitivity per client
2. **During audit:** Identify client + standard → apply TÜV templates → classify sensitivity → choose platform
3. **End of day:** Archive completed audit entries → remove from table

**Sensitivity classification for audit clients:**
- Government entity / PDPL-regulated → HIGH → same routing as HIGH projects (Claude/Cline/Hermes ONLY)
- Corporate / industrial → MEDIUM → all platforms with PII scrub
- Unknown → default MEDIUM with full scrub

**Quick-add format:**
```markdown
| [Client Name] | [Standard] | [Stage 1/2/Surv] | [Date] | [Auditor] | [HIGH/MEDIUM/LOW] | [Notes] |
```

---

## Archived Clients

| Client | Category | Standard | Prefix | Formula | Notes |
|--------|----------|----------|--------|---------|-------|
| UACC | Project (closed) | ISO 50001 | `UACC-EnMS-` | L×S | Finished · English · EnMS vocabulary locked (SEU, EnPI, EnB, VFD, DCS, ALARM, SEEC) |
| MOC | Project (closed) | ISO 37001 | `MOC-ABMS-` | — | Archived July 2026 · Arabic MSA |

---

## Audit Calendar (Projects + Audit Clients)

| Client | Category | Next Audit | Type | Status |
|--------|----------|-----------|------|--------|
| MSD-MOI | Project | [TBD] | Surveillance | In progress |
| SAGCO | Project | [TBD] | Stage 2 | Prep phase |
| Al-Ahsa | Project | [TBD] | Initial | Implementation |

---

## Client Formulas — NEVER Change

| Client | Category | Latent Risk | Residual Risk | Notes |
|--------|----------|-------------|---------------|-------|
| MSD-MOI | Project | S = O × Q | V = S × (1 − U/4) | Arabic MSA, DGA/NCA aligned |
| Al-Ahsa | Project | L × I | Nested IF | NCA ECC aligned |
| SAGCO | Project | L × S | L × S × R (env) | HIRA methodology |
| UACC | Archived | L × S | Nested IF | EnMS vocabulary locked |

---

## Supported Standards

| Standard | Scheme | Status |
|----------|--------|--------|
| ISO 9001:2015 | QMS | Accredited |
| ISO 14001:2015 | EMS | Accredited |
| ISO 45001:2018 | OH&SMS | Accredited |
| ISO 50001:2018 | EnMS | Accredited |
| ISO 27001:2022 | ISMS | Scheme Head |
| ISO 42001:2023 | AIMS | Accredited |
| ISO 22301:2019 | BCMS | Scheme Head |
| ISO 20000-1:2018 | ITSMS | Scheme Head |
| ISO 31000:2018 | Risk | Accredited |
| ISO 37301:2021 | CMS | Accredited |
| NCA ECC | KSA Cyber | Active |
| SAMA CSF | KSA Financial | Active |
| DGA Qiyas | KSA Gov | Active |
| CITC CSF | KSA Telecom | Active |
| PDPL | Personal Data Protection | Active (enforced Sep 2024) |
| DGA Qiyas V5.0 | Government Digital Maturity | Active |
| SDAIA AI Ethics | AI Governance | Active |
| SDAIA GenAI | Government GenAI Use | Active |

---

## TÜV Austria Audit Templates

14 standardized CB forms in `templates/tuv-austria/`. NEVER modify — populate with client data only.

| # | Form | Purpose | Code |
|---|------|---------|------|
| 1 | Audit Questionnaire (ISO 22301) | BCMS pre-audit questionnaire | Q01 |
| 2 | Audit Questionnaire (General) | General pre-audit questionnaire | Q02 |
| 3 | Manday Calculation | Audit duration determination | MD |
| 4 | Audit Plan (General) | Audit scheduling and scope | AP-IMS |
| 5 | Audit Plan (ISMS) | ISMS-specific audit plan | AP-ISMS |
| 6 | Audit Report (IMS) | Post-audit findings and recommendation | AR |
| 7 | Participation List | Audit attendee record | PL |
| 8 | Audit Checklist (ISO 27001) | Clause-by-clause evidence check | CL-ISMS |
| 9 | Audit Checklist (Combined) | QM/EMS/HSE clause evidence | CL-IMS |
| 10 | Certificate Text | Certificate wording |
| 11 | Audit Program | Audit program planning |
| 12 | Checklist (ISO 50001) | EnMS clause evidence |
| 13 | Auditor Assignment | Auditor designation |
| 14 | Approval & Release | Documentation release approval | CERT |

**Full details:** `templates/tuv-austria/README.md`
**Population reference:** `templates/tuv-austria/POPULATION.md` — field maps, data sources, Projects vs Audit Clients population modes, regulatory overlays, naming convention

### Population Workflow Order
```
Manday (03) → Questionnaire (01/02) → Plan (04/05) → Checklist (08/09) → Participation (07) → Report (06) → Certificate (10)
```

### Population Mode Summary
| Mode | Who | Pre-fill % | Example |
|------|-----|------------|---------|
| **RICH** | Projects with prior deliverables | ≥70% | MSD-MOI (BIA exists) → BCM questionnaire 80% pre-filled |
| **SEMI** | Projects without prior deliverables | 40–69% | Al-Ahsa (new impl) → ISMS plan 60% pre-filled |
| **SPARSE** | Audit Clients (daily) | <40% | New audit client → name + standard only, rest flagged |

### Regulatory Overlay Auto-Detection
| Condition | Overlay Added |
|-----------|-------------|
| KSA government entity | NCA ECC (114 controls) + PDPL (12 requirements) |
| Financial sector | SAMA CSF (6 domains) + PDPL |
| Digital government | DGA Qiyas V5.0 (8 dimensions) |
| AI systems | SDAIA AI Ethics (7 principles) + GenAI |

## Document Types

| # | Type | Format |
|---|------|--------|
| 1 | Policy | Word |
| 2 | Procedure | Word |
| 3 | Risk Register | Excel |
| 4 | BIA Workbook | Excel |
| 5 | SoA | Excel |
| 6 | Audit Report | Word |
| 7 | CAPA Form | Word/Excel |
| 8 | Training Deck | PPTX |

---

## Visual Identity Summary

| Client | Primary | Accent | Font | Category |
|--------|---------|--------|------|----------|
| TÜV Default | #C00000 (red) | black | Inter | Default |
| MSD-MOI | #004D26 | #C8A96E | Inter | Project (HIGH) |
| Al-Ahsa | #006400 | — | Inter | Project (HIGH) |
| SAGCO | #1B3A4B | #E07B39 | Inter | Project (MEDIUM) |

---

## Gemini Gem → Client Mapping

| Gem | Primary Use | Clients |
|-----|------------|---------|
| Gem 1 (Auditor) | Pre-audit research, gap analysis, audit reports | All (anonymized for HIGH) · Audit clients for daily work |
| Gem 2 (Implementer) | Policy/procedure drafting, risk registers, BIA | MEDIUM projects on Gemini; HIGH projects via Claude only |
| Gem 3 (KSA Lead) | NCA ECC, SAMA CSF, DGA Qiyas, Etimad | HIGH projects (KSA mandatory) |
| Gem 4 (Personal) | Personal tasks, lifestyle, budget | Non-client only |
| Gem 5 (Code) | Quick code help, snippets, refactoring | ComplianceHub dev |

---

## New Client Onboarding

**New Project:**
1. Create `clients/<NAME>.md` from TEMPLATE.md
2. Add row to Projects table above
3. Define: formula, doc code prefix, visual identity, language, vocabulary, sensitivity
4. Classify sensitivity → HIGH (gov/PDPL) / MEDIUM (industrial) / LOW → affects platform routing
5. Wire into Audit Calendar if audit is expected

**New Audit Client:**
1. One-line entry in Audit Clients table (from calendar each morning)
2. Classify sensitivity on arrival
3. No permanent profile — archive after audit closes

---

## Z.ai Mode Routing by Client Work

| Client Work | Z.ai Mode | Reason |
|-------------|-----------|--------|
| Project deliverable (policy, risk register, BIA) | Agent | Needs full client profile + skill domain file |
| Audit package (plan, checklist, report) | Agent | Multi-step TÜV template pipeline |
| Quick client question ("what's MOI's formula?") | Chat | One lookup, light load |
| Formula spot-check ("verify V=S×(1−U/4)") | Chat | Quick math, no context needed |
| Arabic doc review | Agent | Needs client vocabulary + RTL rules |
| Morning audit list | AutoClaw | Scheduled, recurring |
| Quality gate check on saved file | AutoClaw | Automated pipeline |
| Evening summary | AutoClaw | Scheduled digest |

---

_Last updated: 2026-08-09 · OWL v4.2 · Z.ai Agent/Chat/AutoClaw + Projects vs Audit Clients model_
