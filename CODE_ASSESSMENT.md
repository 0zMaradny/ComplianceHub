# ComplianceHub — Full Code Assessment
**Date:** 2026-08-09
**Location:** `C:\Users\eos\ComplianceHub\`
**Repo:** https://github.com/0zMaradny/ComplianceHub.git (main branch)
**Domain:** TÜV Austria audit document generator for ISO standards

---

## 1. What this project is

A multilingual (AR/EN) web app that generates **TÜV-branded audit document packages**
for 14 ISO management-system standards (9001, 14001, 45001, 50001, 13485, 27001, 22301,
20000, 37301, 42001, 30401, 27701, 31000, 10002). It supports 3 audit types
(initial / surveillance / recertification) and produces checklists, audit plans, audit
reports, certificates, non-conformity lists, and participation lists in DOCX and PDF.

It is **not** a generic AI tool — it is a vertical product for TÜV Austria's
audit practice with deep domain data (per-standard clause structure, Annex A controls
for ISO 27001/42001, IAF MD 5 manday tables, IMS reduction matrix).

---

## 2. Active structure (what's actually used)

```
C:\Users\eos\ComplianceHub\          (3.7 MB backend + 2.9 MB frontend + 0.2 MB Osama)
├── backend/                         ← ACTIVE Python FastAPI service
│   ├── app/
│   │   ├── api/        (placeholder)
│   │   ├── core/       (placeholder)
│   │   ├── data/       (audit_programs)
│   │   ├── routes/     16 API routers
│   │   ├── services/   28 service modules
│   │   ├── settings.py ← new pydantic-style config
│   │   ├── config.py   ← legacy paths + ISO standards dict
│   │   ├── main.py     FastAPI app entry
│   │   ├── utils.py
│   ├── tests/          30 test files
│   ├── scripts/        preprocess, enrich_clause_data, e2e_template_test, model_bench
│   ├── templates/      TÜV audit templates (.docx)
│   ├── static/         CSS + TÜV logo
│   ├── compliancehub.db        ← live SQLite (20 KB)
│   ├── .env                    ← secrets (committed! see §6)
│   ├── pyproject.toml, requirements.txt, pytest.ini
│   ├── Dockerfile, start.sh, download_local_model.sh
│
├── frontend/                        ← ACTIVE React + Vite app
│   ├── src/
│   │   ├── components/  11 React components
│   │   ├── pages/       12 pages + __tests__
│   │   ├── hooks/       3 hooks
│   │   ├── locales/     ar.json + en.json
│   ├── public/          favicon, icons
│   ├── package.json, vite.config.js, eslint.config.js
│   ├── Dockerfile, nginx.conf
│   ├── app.zip (1 MB)   ← looks like a build artifact (?)
│   ├── payload.json (1.4 MB)  ← same (?)
│
├── Osama/                           ← Agent / chat work
│   ├── chat.py (28 KB)  ← recent FastAPI chat endpoint
│   ├── AGENTS.md (13 KB), AGENT_PROMPTS.md, Context.md, MEMORY.md, SKILLS.md, SOUL.md, TOOLS.md
│   ├── DISK_ALERTS.md, FULL_ANDROID_MEMORY.md, WINDOWS_SETUP.md
│   └── rubric.yaml
│
├── output/                          ← 3 generated .docx
│
├── .opencode/, .git/                ← tooling + git
│
└── [root files]                     AGENTS.md, go.ps1, go.sh, opencode.json, README.md, … (35 files)
```

**Total active surface:** ~250 files, ~7 MB, 4.5 KLOC of source.

---

## 3. The legacy dump (10,862 files, 267 MB)

```
ComplianceHub/                     ← ⚠️ LEGACY, untouched
├── .impeccable/    75.9 MB design skill source — should NOT be in repo
├── backend/        old copy (pre-consolidation)
├── frontend/       old copy + dist/ + node_modules
├── graphify-out/   10 MB graphify cache — should NOT be in repo
├── Old Platfroms/  pre-Refactor React source (15 .jsx files)
├── Osama/          duplicate of OWL pack files
├── .git/           a SECOND git repo (not the outer one)
├── [70+ root files including] *enhanced.md, *_GUIDE.md, AGENTS_enhanced.md, …
```

**This is a fat legacy dump that's still tracked or sitting untracked at the project
root.** It contains the OLD pre-consolidation project and duplicates of the OWL pack
files that already exist in the `Osama/` and OWL-system elsewhere.

---

## 4. What the codebase has grown into

### Backend (Python / FastAPI)
- **AI Router** with 4 tiers: Antigravity (free Claude Sonnet 4.6 / Opus 4.6 Thinking) → OpenRouter (8 free models) → Groq → Local. Plus Cohere and HuggingFace fallbacks. **Council Mode** is a new multi-model voting feature (env: `COUNCIL_MODE_ENABLED`, `COUNCIL_JUDGE_MODEL`).
- **30 test files**, 90 Python files total. ~544/585 tests pass (93%) in the old location; with my recent fixes the new copy goes to 584/585.
- **20 GB of AI logic** in `services/ai/` — caching (TTL response cache), PII scrubbing, rate limiting, prompt builders, debugger/validator/scoring, multi-provider fallbacks, exponential backoff.
- **Document generation:** DOCX (python-docx + custom OXML injection for page numbers, headers, footers), PDF (fpdf2 with TÜV fonts), Excel (openpyxl), template filling (template_filler.py, template_manager.py).
- **Audit workflow:** surveillance cycles, findings, manday calculator with IAF MD 5 + IAF MD 11 IMS reduction, 14 standards clause data, 3 audit types, offline template fallback.
- **OCR** (services/ocr.py, 13 KB) — multi-column layout support.
- **RAG retriever** (services/rag_retriever.py, 3 KB) — SQLite FTS5 keyword retrieval over historical audit results.

### Frontend (React + Vite)
- 12 page components: Analytics, Audit, AuditPlan, AuditProgram, Chat, Compliance, Dashboard, History, Projects, Reporting, Surveillance, Templates
- 11 components: DocPreview, EmptyState, ErrorBoundary, LanguageSwitcher, MandayForm, NotificationBell, PreferencesModal, Skeleton, Spinner, Toast
- i18n: ar.json (37 KB), en.json (30 KB)
- Vitest test files for all pages (currently all fail at import due to missing localStorage mock — pre-existing test infra bug)

### OWL system
- The OWL (Osama's Work Layer) agent system has **16 root .md files** at `Osama/`, plus `chat.py` (28 KB FastAPI service for chatting with the agent)
- 5 modified in working tree (not yet committed): `AGENT_PROMPTS.md`, `Context.md`, `SKILLS.md`, `SOUL.md`, `TOOLS.md`
- 1 untracked: `OWL_PENDING_EDITS.md` (24 KB — looks like the in-flight edits file)

---

## 5. Recent work (last 30 commits)

The last 30 commits show **active, focused development** with strong hygiene:

```
d2be22f Add TÜV diagnostic scripts (preserved from Desktop/verification)  ← latest
bceb8cd Port T4/T5 work + repair broken remote refactor
32640a2 Delete CHERRY_STUDIO_ASSISTANTS.md                                  ← cleanup
352443b Clean up pytest.ini configuration
812c409 Update test_validator.py
095f618 Enhance validation logic with additional keywords
bcf21f3 Update pytest.ini with naming conventions
14cf70c Refactor validator.py for improved logic and handling
… (older)
ee92107 Refactor generate_document with 10-gate validation                  ← quality bar
f3160cc Update and rename clause_data.py to iso_clause_database.json
2d59021 Update AI router with Council Mode and PII scrubbing
22298ec fix: Antigravity exponential backoff + provider alias resolution
9794e99 feat: Response cache with TTL + tests for caching and errors
685c880 feat: Developer experience — Docker, pre-commit, health check
e65d3e0 fix: Add MIME type validation for audit notes upload
f9edbb1 refactor: Extract prompt builders, standardize errors, clean up
… (older)
```

**Pattern:** Conventional Commits (`feat:`, `fix:`, `refactor:`), tight commits,
real fixes (race conditions, file-handle leaks, MIME validation, OCR multi-column,
exponential backoff, response caching), real features (Council Mode, PII scrubbing).

This is a well-maintained project.

---

## 6. Critical issues to fix

| # | Severity | Issue | Location |
|---|---|---|---|
| 1 | 🔴 **CRITICAL** | `.env` is committed to git with secrets (ANTIGRAVITY_*, possibly API keys) | `backend/.env` |
| 2 | 🔴 **CRITICAL** | 75.9 MB `.impeccable/` and 10 MB `graphify-out/` are in the legacy `ComplianceHub/` folder — bloat the tree | `ComplianceHub/.impeccable/`, `ComplianceHub/graphify-out/` |
| 3 | 🟠 HIGH | Nested `ComplianceHub/` (267 MB) at the project root is confusing — looks like a separate project but is the legacy dump | `ComplianceHub/ComplianceHub/` |
| 4 | 🟠 HIGH | Frontend tests all fail at import (`localStorage is not defined` in `src/i18n.js:6`) | `frontend/src/test-setup.js` |
| 5 | 🟡 MEDIUM | The OWL `Osama/` files are modified in working tree (5 files) + 1 untracked (OWL_PENDING_EDITS.md) — should be committed or stashed | `Osama/`, root |
| 6 | 🟡 MEDIUM | `frontend/app.zip` (1 MB) and `frontend/payload.json` (1.4 MB) look like build artifacts accidentally committed | `frontend/` |
| 7 | 🟡 MEDIUM | `output/*.docx` and `backend/compliancehub.db` are in source tree (should be gitignored) | `output/`, `backend/` |
| 8 | 🟡 MEDIUM | `backend/app/api/__init__.py` and `backend/app/core/__init__.py` are empty (0 bytes) — placeholders for future code | `backend/app/api/`, `backend/app/core/` |
| 9 | 🟢 LOW | `backend/scripts/` and `backend/app/data/audit_programs/` are empty placeholders | `backend/scripts/`, `backend/app/data/audit_programs/` |
| 10 | 🟢 LOW | `Osama/CHAT_SESSION.md` and `Osama/FULL_ANDROID_MEMORY.md` and `Osama/DISK_ALERTS.md` are personal dev notes in the project tree | `Osama/` |

---

## 7. The `Osama/` folder — what's actually there

The outer `Osama/` is **not just OWL pack files anymore**. It has become a real working
directory with operational tooling:

| File | Size | What it is |
|---|---|---|
| `chat.py` | 28 KB | A FastAPI chat endpoint — likely a CLI/agent interface |
| `AGENTS.md` | 13 KB | The agent roster |
| `AGENT_PROMPTS.md` | 13 KB | Prompt library for each agent |
| `Context.md` | 27 KB | Client context, ISO formulas, platform architecture |
| `SKILLS.md` | 40 KB | All 34 skills + SOPs |
| `SOUL.md` | 4 KB | Identity + non-negotiables |
| `TOOLS.md` | 9 KB | Tool registry |
| `MEMORY.md` | 12 KB | Session log + preferences |
| `USER.md`, `PLATFORMS.md` | <6 KB each | Smaller docs |
| `DISK_ALERTS.md` | 318 B | Alert thresholds |
| `FULL_ANDROID_MEMORY.md` | 8 KB | Some Android-related memory dump |
| `WINDOWS_SETUP.md` | 3.8 KB | Windows dev setup notes |
| `rubric.yaml` | 3.5 KB | Some YAML rubric config |
| `.chat_history`, `.tunnel-url` | small | Runtime state files |
| **`CHERRY_STUDIO_ASSISTANTS.md`** | — | **DELETED in commit 32640a2** (cleanup) |

This folder is a hybrid: half OWL system, half personal/operational files.
The `Osama/AGENTS.md` is the most up-to-date of the OWL system files
(recently modified, with newer content than `OWL_PENDING_EDITS.md` references).

---

## 8. What's NOT in the project but should be

| Missing | Why it matters |
|---|---|
| `.gitignore` updates | The current `.gitignore` doesn't exclude `compliancehub.db`, `output/`, `app.zip`, `payload.json`, `.impeccable/`, `graphify-out/`, `node_modules/`, `__pycache__/`, `*.docx` (template data should be versioned, generated ones shouldn't) |
| `backend/.env.example` | Only `backend/.env` exists with actual secrets — there's no template. Without one, new devs (or future you) can't reproduce. |
| A clean-up PR for the legacy `ComplianceHub/` folder | 267 MB and 10,862 files of legacy junk at the project root. |
| Working tree cleanup | 5 modified `Osama/*.md` files + 1 untracked `OWL_PENDING_EDITS.md` need to be either committed or stashed. |

---

## 9. Healthy patterns observed

✅ **Conventional Commits** — every commit is `feat:`, `fix:`, `refactor:`, etc.
✅ **Tight commit hygiene** — 1 concern per commit
✅ **Good test coverage of recent features** — test files added for caching, errors, validator
✅ **CI/lint ready** — `.pre-commit-config.yaml` with ruff + mypy
✅ **No dead code in the active tree** — `DEAD_CODE.md` documents what was removed
✅ **Domain data is structured** — clause_data.py is 209 KB but it's 14 ISO standards, that's the data
✅ **Council Mode and PII scrubbing are real features** — actual implementation
✅ **Multiple AI provider fallbacks** — robust, production-grade AI plumbing
✅ **SQLite for dev, PostgreSQL for prod** — `psycopg2-binary==2.9.10` in requirements
✅ **Docker + Railway ready** — Dockerfile, docker-compose.yml, railway.json, nginx.conf

---

## 10. Recommended next actions (in priority order)

1. **Rotate any secrets in `backend/.env`** (assuming the repo is or was public) — generate new keys for all 6 providers
2. **Add a real `.gitignore`** that excludes:
   - `__pycache__/`, `*.pyc`, `.pytest_cache/`
   - `node_modules/`, `frontend/dist/`
   - `output/*.docx`, `backend/compliancehub.db`, `backend/uploads/`
   - `frontend/app.zip`, `frontend/payload.json`
   - `**/.impeccable/`, `**/graphify-out/`
   - `.env` (but keep `.env.example`)
3. **Move `ComplianceHub/` legacy folder** to `archive/2026-08-pre-consolidation/` and add to git history as a single squash commit, or delete it
4. **Create `backend/.env.example`** with all 25+ env vars stubbed (no secrets)
5. **Commit or stash the working-tree changes** in `Osama/` (5 modified) and the untracked `OWL_PENDING_EDITS.md`
6. **Fix the frontend test-setup** (1 line: mock `localStorage` and `navigator`) — unblocks 13 vitest test files
7. **Move `chat.py` from `Osama/` to a proper backend route** — it's a FastAPI app that doesn't belong in an OWL/agent docs folder
8. **Add a top-level `README.md` "Quick Start"** that points to the real AGENTS.md / .env.example / go.ps1 entry points

---

## 11. Summary in one line

**A serious, well-engineered audit product with a clean active codebase (~250 files, 7 MB) and a 267 MB legacy dump still sitting at the project root pretending to be a second project — main risks are the committed `.env` and the legacy folder, both of which are easy fixes.**
