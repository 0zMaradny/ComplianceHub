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
- **`app/services/ai_pipeline.py`**: Injects standard family context (main + supporting standards) and Annex A structure into all AI prompts. Includes few-shot evidence examples for all doc types.

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
- `/opt/llama-server/llama-server -m models/qwen-0.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080` — Start local 0.5B model (fast)
- `/opt/llama-server/llama-server -m models/qwen-1.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080` — Start local 1.5B model (better quality)
- Models: `models/qwen-0.5b.gguf` (~469 MB, Q4_K_M), `models/qwen-1.5b.gguf` (~941 MB, Q4_K_M)
- ARM64 optimization: `-t 4` (4 threads, memory-bound), `-b 2048` (batch size), `--mlock` (lock in RAM), `--cache-type-k q8_0 --cache-type-v q8_0` (halve KV cache)

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

### Git
- Git auto-pushes every commit on `main` via `.git/hooks/post-commit`
- PAT token stored in `~/.git-credentials`
- Manual push: `git push origin main`
