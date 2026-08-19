# Skills — IMPLEMENT Domain
_Load on demand when building deliverables, client docs, Excel, Arabic tasks._

**Skills:** 03, 04, 05, 06, 09, 16, 20, 24, 25 | **Agent 2 (Implementer)** + Agent 4 (Excel) + Agent 5 (Arabic)

---

## Skill 03 — Risk Register Design
**Trigger:** "Risk register" / "Risk matrix" / "L×S"
**Formulas (NEVER mix):** MOI: V=S×(1−U/4) | SAGCO: L×S | Al-Ahsa: L×I | UACC: L×S
- Build Excel: Risk ID, Description, Category, L, S, Score, Level, Treatment, Owner, Date
- Apply client visual identity → hidden `_Lists`/`_Data` → A4 print → recalc.py

## Skill 04 — BIA Workbook Design
**Trigger:** "BIA" / "RTO" / "RPO" / "MTD"
- Sheets: Process Inventory → Impact Assessment → Dependency Map → Recovery Priorities
- Impact: Financial, Operational, Regulatory, Reputational
- Link to risk register (Skill 03)

## Skill 05 — Arabic Document Production
**Trigger:** "Arabic" / "BCM" / "RTL" / "BCP"
- RTL via python-docx bidi, `WD_ALIGN_PARAGRAPH.RIGHT`
- Voice: قمنا بـ / تم (practitioner, never passive bureaucratic)
- ISO clause refs ALWAYS in English inside Arabic
- Run humanizer → Skill 21 → Skill 22

## Skill 06 — ISO 42001 AI Management System
**Trigger:** "ISO 42001" / "AI management" / "AIMS"
- Build AIMS: AI Policy + Risk Assessment + System Inventory + Impact Assessment + Human Oversight
- Apply SDAIA AI Ethics overlay (7 principles × 30 controls)
- Cross-ref ISO 27001 for PDPL, DGA Qiyas AI dimension

## Skill 09 — Risk Treatment Plan
**Trigger:** "Treatment plan" / "Risk action"
- Load risk register → treat each risk above threshold
- Types: Avoid / Transfer / Mitigate / Accept
- Cost-benefit + residual risk update

## Skill 16 — Certification Project Management
**Trigger:** "Certification project" / "Project gates" / "Timeline"
- G1: Scope → G2: Gap Analysis → G3: Risk Register → G4: Implementation → G5: Internal Audit → G6: Certification
- Track gate status, escalate blockers (never unblock unilaterally)

## Skill 20 — Training Course Production
**Trigger:** "Training" / "Slides" / "Awareness course"
- Agent 2: structure → Agent 5: Arabic → Agent 7: PPTX → Visual QA

## Skill 24 — Document Version Control
**Trigger:** "Version control" / "Approval block" / "Revision"
- Every doc: Code | Version | Date | Author | Reviewer | Approver
- Blank approval block = G1 failure. Never stack versions — bump and edit in place.

## Skill 25 — Client Onboarding
**Trigger:** "New client" / "Onboard" / "Client setup"
- Collect info → create profile from TEMPLATE.md → add to CONTEXT.md → classify sensitivity

_Last updated: 2026-08-09 · OWL v4.0_
