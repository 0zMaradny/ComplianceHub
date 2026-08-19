# Skills — DEV Domain
_Load on demand when coding, debugging, or working on ComplianceHub._

**Skills:** 08, 11, 17, 38 | **Agent 3 (Developer)** + Agent 7 (Platform)

---

## Skill 08 — Code Quality & Automation
**Trigger:** "Script" / "Automate" / "Python"
- Modular scripts with `# --- CONFIG ---` at top
- CLI via argparse with `--help`
- Zero pyflakes/compileall errors before commit
- Locally deployable (no cloud deps for Phase 1)

## Skill 11 — ComplianceHub Feature Build
**Trigger:** "ComplianceHub" / "Feature" / "Backend" / "Frontend"
- **NEVER build without written scope approval** (SOUL.md Law #4)
- Backend: FastAPI (8000) → new endpoint = router + schema + service + test
- Frontend: React + Vite (5173) → TÜV branding #003D7A / #C00000
- **Hard:** No Firebase, no setAuditProjects in forEach, no Excel as HTML blob, always sanitizeHtml, always AbortController, always ErrorBoundary

## Skill 17 — Debugging & Error Resolution
**Trigger:** "Debug" / "Error" / "Build fails" / "Not working"
- Read error completely → identify type → check MEMORY.md → fix ROOT cause → test → log if new

## Skill 38 — Code Review Gate
**Trigger:** "Review code" / "PR review" / "Pre-commit check"
- Static: compileall + pyflakes + lint
- Logic: edge cases, error handling, validation
- Security: no hardcoded secrets, no SQL injection, no XSS
- Approve / Request Changes / Block

_Last updated: 2026-08-09 · OWL v4.0_
