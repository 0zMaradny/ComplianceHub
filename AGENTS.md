# ComplianceHub — Agent Instructions

## Content Modes (API Key → Provider Chain)

| Mode | API Key | Provider Chain | Speed | Quality |
|------|---------|----------------|-------|---------|
| **HF Free** | HF_API_KEY set | hf → local → offline | Fast | 7/8 docs via Llama-3-8B |
| **Cloud AI** | Valid Gemini/OpenAI key | gemini → openai → hf → local | Fast | Best (all 8) |
| **Local AI** | Empty (+ model running) | local → offline | Slow | ~6-7/8 docs |
| **Offline** | Empty (no model) | offline only | Instant | Professional |

## Supported Standards (13 total)

| Key | Standard | Structure | Annex |
|-----|----------|-----------|-------|
| `iso_9001` | ISO 9001:2015 — Quality Management | HLS Clause 1-10 | — |
| `iso_14001` | ISO 14001:2015 — Environmental | HLS Clause 1-10 | — |
| `iso_45001` | ISO 45001:2018 — OH&S | HLS Clause 1-10 | — |
| `iso_50001` | ISO 50001:2018 — Energy | HLS Clause 1-10 | — |
| `iso_27001` | ISO 27001:2022 — InfoSec | HLS + Annex A (4 themes, grouped) | A.5–A.8 (93 controls) |
| `iso_20000` | ISO 20000-1:2018 — Service Mgmt | HLS Clause 1-10 | — |
| `iso_22301` | ISO 22301:2019 — Business Continuity | HLS Clause 1-10 | — |
| `iso_37301` | ISO 37301:2021 — Compliance | HLS Clause 1-10 | — |
| `iso_42001` | ISO 42001:2023 — AI Management | HLS + Annex A (9 objectives) | A.9.1–A.9.9 (40 controls) |
| `iso_30401` | ISO 30401:2018 — Knowledge Mgmt | HLS Clause 1-10 | — |
| `iso_27701` | ISO 27701:2025 — Privacy | HLS + PIMS-specific 5-7,9-10 | — |
| `iso_31000` | ISO 31000:2018 — Risk (Guidelines) | Framework: Principles, Framework, Process | — |
| `iso_10002` | ISO 10002:2018 — Complaints | Framework: 5 sections | — |

## Architecture

- **`app/services/clause_data.py`**: Data-driven clause database. Contains `HLS_CORE` (shared Clauses 1-3, 4-7, 9-10), `CLAUSE_8` (per-standard variants with sub-sub-clauses), `ANNEX_A_27001` (4 grouped themes), `ANNEX_A_42001` (9 control objectives), `PIMS_27701` (stand-alone privacy clauses), `FRAMEWORK_31000` and `FRAMEWORK_10002` (framework sections), `SUPPORTING_STANDARDS_EVIDENCE` (cross-references). Helper functions: `get_clause_data()`, `get_annex_a_data()`, `flatten_clauses()`, `get_evidence_for_clause()`.
- **`app/services/offline_generator.py`**: Uses `clause_data` module to generate dynamic standard-specific checklists and evidence. No hardcoded ISO 9001 sections — all standards get proper clause coverage.
- **`app/services/ai_pipeline.py`**: Injects standard family context (main + supporting standards) and Annex A structure into all AI prompts. Includes few-shot evidence examples for all doc types. Accepts `manday_info` — injects `{manday_summary}` block (audit type, total days, per-standard breakdown, team, IMS reduction) before raw manday text in every prompt.
- **`app/services/manday_calculator.py`**: IAF MD 5 reference tables for all 13 standards, audit type multipliers (initial=1.0, surv=1/3, recert=2/3, transfer=2/3), IAF MD 11 IMS reduction matrix (15 per-pair reductions, max 20%), `compute_mandays()`, `detect_audit_type()`, `compute_ims_reduction()`, `compute_audit_team()`, `lookup_base_mandays()`.
- **`app/services/template_manager.py`**: Maps doc types to TÜV template files. `CHECKLIST_TEMPLATES` covers 8 standards (iso_9001, 14001, 45001, 50001, 20000, 22301, 27001 via Excel); remaining 5 standards generate from scratch.
- **`frontend/src/components/MandayForm.jsx`**: Collapsible form — audit type dropdown, employee/site inputs, per-standard risk/complexity table, IMS reduction %, real-time calculation preview (total, per-standard, team). Auto-fills from `mandayExtracted`.
- **`generate_document_file`** in `document_generator.py`: `safe_name` capped to 60 chars with regex sanitization to prevent 500+ char filenames. Merged-cell tables handled gracefully in `set_col_widths` and `_inject_into_template_table`.

## Commands

### Run Servers
- `bash run.sh` — Start backend + frontend (offline mode)
- `bash run.sh --local-ai` — Start with local AI model (qwen-1.5b)

### Backend (Python / FastAPI)
- `cd backend && python -m compileall . -q` — Check all Python syntax
- `cd backend && python -c "from app.main import app; print('OK')"` — Verify imports
- `cd backend && python -c "from app.services.clause_data import get_clause_data; d=get_clause_data('iso_27001'); print('OK', len(d))"` — Verify clause_data module
- `cd backend && uvicorn app.main:app --port 8000` — Start backend only
- `cd backend && curl http://localhost:8000/api/standards` — Smoke-test API

### Frontend (React / Vite)
- `cd frontend && npm run lint` — ESLint check
- `cd frontend && npm run build` — Production build
- `cd frontend && npm run dev` — Development server (port 5173)

### Local AI (llama.cpp server)
- `/opt/llama-server/llama-server -m /opt/llama-server/models/qwen-0.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080` — Start local 0.5B model (fast)
- `/opt/llama-server/llama-server -m /opt/llama-server/models/qwen-0.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080 --cache-type-k q8_0 --cache-type-v q8_0` — With KV cache optimization
- Models: `/opt/llama-server/models/qwen-0.5b.gguf` (~469 MB, Q4_K_M) — downloaded from `Qwen/Qwen2.5-0.5B-Instruct-GGUF`
- ARM64 optimization: `-t 4` (4 threads, memory-bound), `-b 2048` (batch size), `--mlock` (lock in RAM), `--cache-type-k q8_0 --cache-type-v q8_0` (halve KV cache)
- **Model download**: `curl -L -H "Authorization: Bearer $HF_TOKEN" -o /opt/llama-server/models/qwen-0.5b.gguf "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"`
- **Fallback**: If no model or server not running, the pipeline falls back to offline generator automatically

### Code Quality
- `cd backend && python -m pyflakes app/` — Check for unused imports, undefined vars, bugs (should return **zero**)
- `cd backend && python -m compileall . -q` — Check syntax errors
- `cd frontend && npm run lint` — ESLint check

### Cloud AI Keys
- `backend/.env` — Set GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY, or HF_API_KEY
- HF_API_KEY: Get a free token at https://huggingface.co/settings/tokens
  - Then **enable Inference Providers** at https://huggingface.co/settings/inference-providers
  - Default model: `meta-llama/Meta-Llama-3-8B-Instruct` (fast, good quality)
  - Override via `HF_MODEL` env var in `.env`
  - Token provided (`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`) works with Llama-3-8B and Llama-3.2-1B

### Docker Deployment
- `docker compose build` — Build backend + frontend images
- `docker compose up -d` — Start services (backend:8000, frontend:80)
- `docker compose down` — Stop services
- Backend API: `http://localhost:8000/api/standards`
- Frontend UI: `http://localhost/`
- Backend `.env` is mounted read-only from `backend/.env`
- Upload volume persists across restarts via `uploads` named volume

### Tests
- `cd backend && python -m pytest tests/ -v` — Run 96 unit tests
- `cd backend && python -m pytest tests/ --coverage` — With coverage report
- Test files: `tests/test_manday_calculator.py` (55 tests), `tests/test_offline_generator.py` (25 tests), `tests/test_template_manager.py` (16 tests)

### End-to-End Test
- Start: `bash run.sh` (or backend + frontend separately)
- Upload: `curl -X POST http://localhost:8000/api/upload -F "audit_notes=@file.docx" -F "manday=@file.docx" -F 'standards=["iso_9001"]' -F "api_key="`
- Generate: `curl -X POST http://localhost:8000/api/generate -F "job_id=JOBID" -F 'standards=["iso_9001"]' -F "api_key=" -F 'manday_config={"audit_type":"initial","employee_count":50}'`
- Status: `curl http://localhost:8000/api/status/JOBID`
- Download: `curl -o package.zip http://localhost:8000/api/download/JOBID`

### Checklist Template Coverage
- 8 standards with template injection: iso_9001, iso_14001, iso_45001, iso_50001, iso_20000, iso_22301, iso_27001 (Excel), iso_45001/50001 (shared combined template)
- 5 standards from scratch: iso_37301, iso_42001, iso_30401, iso_27701, iso_31000, iso_10002
- **iso_22301 fix**: table with merged cells (`no 'tc' element`) — graceful fallback to from-scratch generation

### Thread Safety
- `generate_background` wrapper catches all `Exception`, logs traceback, sets `status=error` in progress_store
- Server restart: `fuser -k 8000/tcp` to release bound port

### Git
- Git auto-pushes every commit on `main` via `.git/hooks/post-commit`
- PAT token stored in `~/.git-credentials`
- Manual push: `git push origin main`
