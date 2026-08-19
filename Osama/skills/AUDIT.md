# Skills — AUDIT Domain
_Load on demand when audit/compliance/gap/NC tasks are active._

**Skills:** 02, 07, 12, 14, 26, 27, 28 | **Agent 1 (Judge)** + Agent 10 (KSA Lead)

---

## Skill 02 — ISO Compliance Audit
**Trigger:** "Audit" / "NC" / "Gap" / "Clause check" / "Compliance"
1. Identify standard(s) from CONTEXT.md → load client profile
2. For each clause: assess compliance → evidence required → NC severity
3. Output: Clause | Compliance Status | Evidence Required | NC Severity
4. **Track A:** Identify gaps ONLY — never offer solutions (hand off to Agent 2)
5. Apply KSA regulatory overlay if government/financial (Agent 10)
6. Run Skill 22 Quality Gates before delivery

## Skill 07 — Gap Analysis & Pre-Assessment
**Trigger:** "Gap check" / "Pre-assessment" / "Readiness"
1. Load standard requirements clause-by-clause
2. Compare against client's documented management system
3. For each gap: classify severity, estimate effort, suggest timeline
4. Deliverables: Gap Register (Excel) + Gap Report (Word)

## Skill 12 — CAPA Management
**Trigger:** "CAPA" / "Root cause" / "5-Whys" / "Corrective action"
**Order (NEVER change):** Root Cause → Containment → Corrective → Preventive → Effectiveness Verification
- 5-Whys mandatory for Major NC
- Timeline tracking and follow-up scheduling

## Skill 14 — Audit Package Assembly
**Trigger:** "Audit package" / "8 docs" / "Certification package"
**7-step workflow:** Manday → Questionnaire → Plan → Checklist → Participation → Report → Certificate
**+4 extra:** T11 Audit Program, T12 ISO 50001 Checklist, T13 Auditor Assignment, T14 Approval/Release
**State:** NOT_STARTED → POPULATING → POPULATED → REVIEWED → APPROVED
Templates are IMMUTABLE — save populated versions as new files.

## Skill 26 — Audit Report Drafting
**Trigger:** "Audit report" / "CB recommendation" / "Findings report"
1. Use Template 06 → populate via SCRIPT + AI + FLAG paths
2. Structure: Scope → Findings → NCs → Observations → Recommendation
3. Flag FC/NC/Partial/NA checkboxes for manual auditor input
4. Run G1–G10 → auditor reviews and signs off

## Skill 27 — Statement of Applicability (SoA)
**Trigger:** "SoA" / "Annex A" / "Control exclusions"
1. List all Annex A controls → Applicable/Not Applicable/Partially
2. Justification for every exclusion (mandatory for ISO 27001 A.5–A.8)
3. Link to risk assessment results

## Skill 28 — Pre-Audit Research & Briefing
**Trigger:** "Pre-audit brief" / "Research standard" / "Latest ISO"
1. Research latest amendments, interpretations, regulatory changes
2. Check KSA-specific requirements (NCA ECC, SAMA CSF, DGA Qiyas)
3. Prepare briefing: standard overview + client regulatory + scope + risk areas

_Last updated: 2026-08-09 · OWL v4.0_
