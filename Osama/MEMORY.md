# Memory.md — Compounding Knowledge Log

This file updates after each session. It stores what Claude has learned: preferences, corrections, wins, mistakes. Every session starts smarter than the last.

## ✅ Confirmed Preferences

### Excel
- Always openpyxl — never suggest VBA or xlsxwriter
- All calculations as live Excel formulas — never hardcoded Python values
- Hidden sheets: _Lists or _Data for all dropdown sources
- Freeze top row + left column on all data sheets by default
- Print area: A4 with rows_to_repeat on row 1
- Conditional formatting uses PatternFill — not icon sets unless requested
- KPI dashboard cards: merged cells with thick borders
- Color constants defined at top of script for easy reuse
- Run scripts/recalc.py after every formula build — mandatory zero errors

### Word / Arabic Documents
- python-docx for all .docx generation
- Arabic paragraphs: WD_ALIGN_PARAGRAPH.RIGHT + explicit bidi run property
- First-person practitioner voice: ﻗﻤﻨﺎ ﺑـ... / ﺗﻢ ﺗﻄﺒﻴﻘ...
- Section headers: Heading 1 Arabic · Sub-headers: Heading 2
- Tables: RTL with merged Arabic header rows
- ISO clause refs and Risk ID codes stay in English always

### ISO / GRC Work
- Always use professional terminology: NC, CAR, SoA, OFI, PDCA
- ISO 42001 is the bridge between auditing and AI/coding interests — prioritize when relevant
- Suggest automation angle for ISO monitoring whenever applicable
- Audit output = identify only · Implementation output = solve only (never mix)
- CAPA structure always: Root Cause (5-Whys) → Containment → Corrective → Preventive → Verification

### Code
- Modular Python scripts · # --- CONFIG --- block always at top
- Suggest how ISO clauses can be tracked via script (e.g., ISO 27001 + data logs)
- Code ready for local deployment without cloud dependency

### React / Artifact Platform (TÜV Austria Hellas Compliance Platform)
- Artifact sandbox rules (hard constraints, never violate):
  - NO Firebase imports (from "firebase/...") — artifact can't resolve npm packages
  - NO process.env variables — not available in artifact context
  - NO require() — must use ES module import
  - Use window.storage API (get/set/delete) for persistence — key: 'tuv_platform_data'
  - AI: Anthropic API only — https://api.anthropic.com/v1/messages — no key needed in artifact
  - Model: claude-sonnet-4-6 — response in content[0].text
  - CDN allowed: cdnjs.cloudflare.com (mammoth, XLSX)
- Checklist IDs: deterministic — ${std}-${clause.replace(/\./g,'_')} — NEVER random hash
- State management: all bulk document generation must accumulate then call setAuditProjects ONCE
- Excel exports: use real window.XLSX.utils.aoa_to_sheet — NOT the HTML table blob trick
- Download filenames: always sanitize — filename.replace(/[^a-z0-9]/gi,'_')
- XSS protection: all user content going into dangerouslySetInnerHTML or HTML exports must pass through sanitizeHtml() first
- Rate limiting: aiCallLimiter.canProceed() must be checked before every Anthropic call
- Abort controller: every AI call must create new AbortController() and store in abortControllerRef.current; cleanup in unmount useEffect
- Error boundary: wrap <App/> in <ErrorBoundary> for auto-recovery
- CAPA: shown only for clauses rated Minor NC or Major NC — structure: Root Cause → Containment → Corrective → Preventive → Verification

## ⚠️ Corrections (Logged Mistakes — Never Repeat)

| # | Mistake | Correct Approach |
|---|---------|-----------------|
| 1 | Used xlsxwriter instead of openpyxl | Always openpyxl for read/write workbooks |
| 2 | Left Arabic text LTR in .docx | Must set bidi run + RTL paragraph alignment |
| 3 | Translated Risk ID codes to Arabic | Risk IDs always stay in English |
| 4 | Used generic Excel color palette | Use exact MOI hex codes: #004D26 / #C8A96E / #1A3A5C |
| 5 | Simplified residual risk formula | V = S×(1−U/4) must be preserved exactly — never simplify |
| 6 | Hardcoded calculated values in Python | All calculations must be Excel formulas, not Python outputs |
| 7 | Agent 1 (Auditor) offered solutions | Auditor strictly identifies gaps only — Implementer solves |
| 8 | Used import from "firebase/..." in artifact | Firebase SDK can't load in Claude artifact sandbox — use window.storage |
| 9 | Used Gemini API (generativelanguage.googleapis.com) in artifact | Claude artifact uses Anthropic API — no key needed, api.anthropic.com/v1/messages |
| 10 | Called setAuditProjects inside .forEach loop | All docs must accumulate in fullPackage{}, then one setAuditProjects call after loop |
| 11 | Generated Excel as HTML Blob with .xls extension | Use window.XLSX.utils.aoa_to_sheet → window.XLSX.writeFile for real .xlsx |
| 12 | dangerouslySetInnerHTML on raw user content | Always pass through sanitizeHtml() first — XSS risk |
| 13 | **bold** passed to JSX paragraph as text | Use dangerouslySetInnerHTML with .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>') |
| 14 | Treated MOI as "Professional Identity Track 1" | MOI is a client under Lead Implementer track. Identity = TÜV Austria GCC. Two tracks: Lead Auditor (CB scheme head) + Lead Implementer (consulting). Never collapse them |
| 15 | Only listed MOI + UACC as clients | Full client list: MSD-MOI (22301+31000) · UACC (50001) · SAGCO (45001+14001, active) · Al-Ahsa Municipality (27001, active) · Client 5 TBD |
| 16 | Assumed SAGCO = post-certification surveillance | SAGCO = active Lead Implementer for ISO 45001 + ISO 14001 only — NOT 50001 or 37001 |
| 17 | Framed career change as July 2026 | No career change — staying at TÜV Austria GCC. ISO 42001 LI + PMP are additional personal certifications, not a role change |
| 18 | Used 9-part Ruben Hassid framework only | Merged framework: 12 parts (Ruben Hassid 9-part + serveai.ig ROLE/REASONING/OUTPUT). Always ROLE + TASK + OUTPUT + PUSH minimum |
| 19 | ISO 42001 AIA treated as single checklist item | ISO/IEC 42005 defines 7-step AIIA process with 10 mandatory impact categories — each step is a separate audit checkpoint, not one generic item |
| 20 | Listed ISO 42001 LI as "certified 2026" | ISO 42001 LI (PECB) is exam preparation in progress — NOT yet certified. Never claim certification status without explicit confirmation |

## 🏆 Wins (Approaches That Delivered)

- Full 6-sheet UACC EnMS workbook in one session with correct formulas and scoring matrices
- BCM forms workbook: 21 forms, all linked to _Data sheet, zero formula errors
- Arabic BCM Word document: correct RTL, formal voice, ISO clause mapping, DGA/NRC compliance
- Dashboard KPI cards with live conditional color coding by risk level
- Hidden _Lists sheet pattern eliminated all manual dropdown maintenance
- IMS audit table format (Clause | Status | Evidence | NC Severity) adopted as standard output
- TÜV Austria Hellas Compliance Platform — full React app, 1,983 lines, 157 KB, 8 ISO standards, Anthropic AI, window.storage, real XLSX export, ErrorBoundary, CAPA generation — zero parse errors, 19/19 async try/catch
- GitHub → artifact delta merge: 18/18 improvements applied in single session
- AutoDebugger — 728-line artifact with 16 static checks + AI deep scan + auto-fix rewrite; Babel-verified zero errors
- Dual role clarified — Lead Auditor (scheme head: ISMS/ITSMS/BCMS) running simultaneously with Lead Implementer (4 active clients: MOI, UACC, SAGCO, Al-Ahsa)
- ISO 42001 — 24 mandatory documents mapped — full clause-to-document mapping loaded into platform checklist (24 items) and consulting templates (20+ templates), Skills.md Skill 06 updated with complete table
- ISO/IEC 42005 — AIIA 7-step process mapped — AI System Impact Assessment methodology: Context → Stakeholders → 10 Impact Categories (Fairness/Privacy/Safety/Security/Explainability/Accountability/Societal/Economic/Legal/Human Autonomy) → Severity×Likelihood → Controls → Residual Impact → Governance Decision. Embedded in platform (7 checklist items + 3 templates), Skill 06, and Context.md
- Merged 12-part prompt anatomy — Ruben Hassid 9-part + serveai.ig (ROLE · REASONING · OUTPUT). Embedded in Skill 15, Agent 8, Context.md quick reference. Always minimum: ROLE + TASK + OUTPUT + PUSH
- 15 corrections logged — Firebase/Gemini/React/Excel/Arabic/role structure — Memory prevents all from repeating

## 📋 Session Log

| Date | Session Summary | Key Output |
|------|----------------|------------|
| May 2026 | Built TÜV Austria Hellas ISO Compliance Platform from Code_29_04_2026.docx | Full React app — 15 bugs/enhancements implemented |
| May 2026 | Debug & API migration: Firebase → window.storage, Gemini → Anthropic | Artifact-ready build, 0 parse errors |
| May 2026 | GitHub ComplianceOS_fixed comparison & merge | 18 improvements: CAPA, sanitizeHtml, rate limiter, abort controller, real XLSX, error boundary, useTransition |
| June 2026 | Discovered ComplianceHub full-stack repo on GitHub (0zMaradny/ComplianceHub) | FastAPI + Vite/React, 13 standards, 8 doc types, multi-provider AI router, Autodebugger, TÜV-branded templates, 17 template files |
| June 2026 | Full workspace file rewrite — Context.md, SOUL.md, TOOLS.md | Platform section replaced with accurate repo data, legacy React artifact archived, client data preserved, ISO 42001 status corrected to exam prep |

## 🔁 How to Update This File

After each productive session, add:
1. New preference confirmed or discovered
2. Any correction made during the session
3. New deliverable completed (name + format)
4. Any formula, pattern, or code structure that worked exceptionally well
