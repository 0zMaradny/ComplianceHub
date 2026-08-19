# TÜV Austria — Audit Template Inventory
_Last updated: 2026-08-09_

## Template List (14 CB Forms)

| # | Form Name | File | Used For |
|---|-----------|------|----------|
| 01 | Questionnaire (BCM) | `T01_Questionnaire_BCM.docx` | BCMS (ISO 22301) |
| 02 | Questionnaire (General) | `T02_Questionnaire_General.docx` | All standards |
| 03 | Manday Calculation | `T03_Manday_Calc.docx` | Audit planning |
| 04 | Audit Plan (General/IMS) | `T04_Audit_Plan_General.docx` | IMS (9001+14001+45001) |
| 05 | Audit Plan (ISMS) | `T05_Audit_Plan_ISMS.docx` | ISMS (ISO 27001) |
| 06 | Audit Report | `T06_Audit_Report.docx` | All standards |
| 07 | Participation List | `T07_Participation_List.docx` | All audits |
| 08 | Audit Checklist (ISMS) | `T08_Checklist_ISMS.xlsx` | ISMS (ISO 27001) |
| 09 | Audit Checklist (Combined) | `T09_Checklist_Combined.docx` | QM+EM+HSE |
| 10 | Certificate | `T10_Certificate.docx` | All certifications |
| 11 | Audit Program | `T11_Audit_Program.docx` | All standards (universal) |
| 12 | Checklist (ISO 50001) | `T12_Checklist_ISO50001.docx` | EnMS (ISO 50001) |
| 13 | Auditor Assignment | `T13_Auditor_Assignment.docx` | All audits |
| 14 | Approval & Release | `T14_Approval_Release.docx` | All standards |

## Usage Rules
- **NEVER modify templates** — always populate with client data and save as new file
- Client doc code prefix applied to all saved files
- Templates are TÜV Austria CB property — immutable

## Workflow Order
Manday calc (03) → Questionnaire (01/02) → Audit Program (11) → Plan (04/05) → Auditor Assignment (13) → Checklist (08/09/12) → Participation list (07) → Report (06) → Approval & Release (14) → Certificate (10)

## Standard-Specific Selection
- **ISO 27001:** Plan 05 + Checklist 08
- **IMS (9001+14001+45001):** Plan 04 + Checklist 09
- **BCMS (22301):** Add Questionnaire 01
- **ISO 42001:** Use ISMS templates + AIMS-specific additions
- **ISO 50001:** Use IMS templates + Checklist 12 + EnMS-specific additions

## Template Codes (for naming convention)
| Code | Template |
|------|----------|
| Q01 | Questionnaire (BCM) |
| Q02 | Questionnaire (General) |
| MD | Manday Calculation |
| AP | Audit Program |
| AP-IMS | Audit Plan (General/IMS) |
| AP-ISMS | Audit Plan (ISMS) |
| AAS | Auditor Assignment |
| CL-ISMS | Audit Checklist (ISMS) |
| CL-IMS | Audit Checklist (Combined) |
| CL-EnMS | Audit Checklist (ISO 50001) |
| PL | Participation List |
| AR | Audit Report |
| RL | Approval & Release |
| CERT | Certificate Text |

**Naming pattern:** `<PREFIX>-<CODE>-<DATE>.<ext>` (e.g., `MSD-MOI-GRC-Q01-2026-08-10.docx`)

## Population Modes
- **RICH** (≥70% pre-fill): Projects with prior deliverables — e.g., MSD-MOI BIA feeds BCM questionnaire
- **SEMI** (40–69%): Projects without prior deliverables — e.g., Al-Ahsa new implementation
- **SPARSE** (<40%): Audit Clients — name + standard + date only, rest flagged

**Full population reference:** `templates/tuv-austria/POPULATION.md`
