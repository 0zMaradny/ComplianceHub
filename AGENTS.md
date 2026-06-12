# ComplianceHub — Agent Instructions

## AI Provider Architecture (4-Tier Fallback, 11 Models)

```
generate() / extract_structured()
  ├─ Cache check (md5, 1h TTL)
  ├─ Tier 1: Frontier OpenRouter (Nemotron 550B, Qwen3 Coder 480B, Kimi K2.6, Owl Alpha 1M) — parallel batch=2
  │   └─ all fail → Tier 2: Strong OpenRouter (Nemotron 120B, Llama 70B, Qwen3 Next 80B, Hermes 405B) — parallel batch=2
  │       └─ all fail → Tier 3: Groq (Llama 3.3 70B, ~800 t/s)
  │           └─ all fail → Tier 4: Local AI (Qwen2.5-3B or Qwen2.5-0.5B, localhost:8080)
  │               └─ fail → return error
```

| Tier | Provider | Models | Cost | Context | Speed |
|------|----------|--------|------|---------|-------|
| **1** | OpenRouter | Nemotron 3 Ultra 550B, Qwen3 Coder 480B, Kimi K2.6, **Owl Alpha** | **Free** | Up to 1M | Good |
| **2** | OpenRouter | Nemotron 3 Super 120B, Llama 3.3 70B, Qwen3 Next 80B, Hermes 405B | **Free** | Up to 1M | Good |
| **3** | Groq | Llama 3.3 70B Versatile | **Free** (~800 t/s) | 131k | **Fastest** |
| **4** | Local (llama-server) | Qwen2.5-3B or Qwen2.5-0.5B GGUF | $0 | 8k / 4k | ~60s / ~20s per doc |
| **Offline** | Template engine | Static generation | $0 | Instant (3.2s/8docs) | Professional |

### API Key Setup
- `.env` keys: `OPENROUTER_API_KEY`, `GROQ_API_KEY`
- OpenRouter: https://openrouter.ai/keys (free tier available)
- Groq: https://console.groq.com/keys (free, no CC)

## Supported Standards (14 total)

| Key | Standard | Structure | Annex |
|-----|----------|-----------|-------|
| `iso_9001` | ISO 9001:2015 — Quality Management | HLS Clause 1-10 | — |
| `iso_14001` | ISO 14001:2015 — Environmental | HLS Clause 1-10 | — |
| `iso_45001` | ISO 45001:2018 — OH&S | HLS Clause 1-10 | — |
| `iso_50001` | ISO 50001:2018 — Energy | HLS Clause 1-10 | — |
| `iso_13485` | ISO 13485:2016 — Medical Devices | HLS Clause 1-10 | — |
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
- **`app/services/manday_calculator.py`**: IAF MD 5 reference tables for all 14 standards, audit type multipliers (initial=1.0, surv=1/3, recert=2/3, transfer=2/3), IAF MD 11 IMS reduction matrix (15 per-pair reductions, max 20%), `compute_mandays()`, `detect_audit_type()`, `compute_ims_reduction()`, `compute_audit_team()`, `lookup_base_mandays()`.
- **`app/services/template_manager.py`**: Maps doc types to TÜV template files. `CHECKLIST_TEMPLATES` covers 8 standards (iso_9001, 14001, 45001, 50001, 20000, 22301, 27001 via Excel); remaining 7 standards generate from scratch.
- **`app/services/ai/router.py`**: 3-tier fallback architecture — Frontier OpenRouter (4 free frontier models) → Strong OpenRouter (4 free strong models) → Groq (Llama 3.3 70B, ~800 t/s). Uses `ThreadPoolExecutor` with future cancellation for parallel execution. Peak-hours awareness: weekdays 12-18 UTC, low-priority tasks skip OpenRouter, go direct to Groq. Rate limiter, health tracking, quality scoring, response cache, and autodebugger self-healing integrated per provider.
- **`app/services/ai/groq_provider.py`**: OpenAI-compatible client for Groq (`api.groq.com/openai/v1`). Model: `llama-3.3-70b-versatile`. Fastest free inference (~800 t/s). Tier 3 fallback.
- **`app/services/ai/openrouter_provider.py`**: OpenAI-compatible client for OpenRouter (`openrouter.ai/api/v1`). Handles Tier 1 (frontier) and Tier 2 (strong) free models.
- **`frontend/src/components/MandayForm.jsx`**: Collapsible form — audit type dropdown, employee/site inputs, per-standard risk/complexity table, IMS reduction %, real-time calculation preview (total, per-standard, team). Auto-fills from `mandayExtracted`.
- **`generate_document_file`** in `document_generator.py`: `safe_name` capped to 60 chars with regex sanitization to prevent 500+ char filenames. Merged-cell tables handled gracefully in `set_col_widths` and `_inject_into_template_table`.

## Commands

### Run Servers
- `bash run.sh` — Start backend + frontend (offline mode)
- `bash run.sh --local-ai` — Start with local AI (auto-selects: qwen-3b if available, else qwen-0.5b)
- `bash run.sh --local-model=qwen-3b` — Start with Qwen2.5-3B (~2.1 GB, ~60s/doc)
- `bash run.sh --local-model=qwen-0.5b` — Start with Qwen2.5-0.5B (469 MB, ~20s/doc)
- `bash run.sh --no-local-ai` — Explicitly skip local AI

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
- `/opt/llama-server/llama-server -m /opt/llama-server/models/qwen-3b.gguf -c 8192 -t 4 -b 2048 --mlock --port 8080` — Start Qwen2.5-3B (~2.1 GB, ~60s/doc, 8k context)
- `/opt/llama-server/llama-server -m /opt/llama-server/models/qwen-0.5b.gguf -c 4096 -t 4 -b 2048 --mlock --port 8080` — Start Qwen2.5-0.5B (469 MB, ~20s/doc)
- Models: canonical copies at `/opt/llama-server/models/` (`qwen-3b.gguf`, `qwen-0.5b.gguf`); repo `models/` is a symlink to `/opt/llama-server/models/`
- ARM64 optimization: `-t 4` (4 threads, memory-bound), `-b 2048` (batch size), `--mlock` (lock in RAM), `--cache-type-k q8_0 --cache-type-v q8_0` (halve KV cache)
- Qwen2.5-3B uses `-c 8192` (6x params, needs ~2.5 GB RAM at Q4_K_M)
- **RAM watchdog**: Background loop (5 min interval) monitors `MemAvailable` — kills non-essential processes when below 500 MB
- **Fallback**: If no model or server not running, the pipeline falls back to offline generator automatically

### Model Benchmarks (ARM64, 4 threads, CPU-only)

| Model | Size | Context | Time/doc | JSON | Quality Score | Verdict |
|-------|------|---------|----------|------|---------------|---------|
| **qwen-3b** (Qwen2.5-3B Q4_K_M) | **~2.1 GB** | **8k** | **~60s** | ✅ Valid | **65** (est.) | **Best local quality** |
| qwen-0.5b (Qwen2.5-0.5B) | 469 MB | 4k | ~20s | ✅ Valid | 45 | Reliable fallback |
| ~~Phi-4 Mini (3.8B)~~ | ~~2.4 GB~~ | ~~4k~~ | ~~~65s~~ | ✅ Valid, nested | ~~65~~ | ❌ Removed (too slow) |
| ~~Qwen3-4B~~ | ~~2.4 GB~~ | ~~4k~~ | ~~~90s~~ | ❌ Non-JSON | ~~50~~ | ❌ Removed (too slow) |

- Qwen2.5-3B Q4_K_M (~2.1 GB) delivers **6x more parameters** than qwen-0.5b at the cost of 3x slower inference — best quality/speed tradeoff for this device.
- Cloud AI (HF/OpenAI/Gemini/Claude) provides better quality at higher speed when API keys are available.
- Offline mode completes all 8 docs in **3.2s total** (0.4s avg/doc) — the fastest option.

### Code Quality
- `cd backend && python -m pyflakes app/` — Check for unused imports, undefined vars, bugs (should return **zero**)
- `cd backend && python -m compileall . -q` — Check syntax errors
- `cd frontend && npm run lint` — ESLint check

### Cloud AI Keys
- `backend/.env` — Current keys: AGENTROUTER_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, HF_API_KEY (legacy: GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY)
- AgentRouter: https://agentrouter.org — key prefix `sk-`
- Groq: https://console.groq.com/keys — free, sign up → copy key (`gsk_` prefix)
- OpenRouter: https://openrouter.ai/keys — free tier available, key prefix `sk-or-`
- HF: https://huggingface.co/settings/tokens — free
  - **enable Inference Providers** at https://huggingface.co/settings/inference-providers
  - Default model: `meta-llama/Meta-Llama-3-8B-Instruct` (fast, good quality)
  - Override via `HF_MODEL` env var in `.env`
  - Token provided (`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`) works with Llama-3-8B and Llama-3.2-1B

### Database (PostgreSQL / Railway)
- `backend/app/services/db.py` — Auto-detects `DATABASE_URL` env var at import time
- If `DATABASE_URL` starts with `postgresql://` or `postgres://`, uses **psycopg2** (via `psycopg2-binary==2.9.10`)
- Otherwise falls back to **SQLite** (`backend/compliancehub.db`) with WAL mode
- All queries abstracted through `_exec()`, `_fetchone()`, `_fetchall()` helpers
- SQLite uses `?` placeholders; PostgreSQL uses `%s` (auto-translated via `_fix_sql()`)
- `INSERT OR REPLACE` → PostgreSQL `INSERT ... ON CONFLICT ... DO UPDATE`
- Railway auto-injects `DATABASE_URL`; no manual config needed

### Railway Deployment
- `railway.json` — Dockerfile builder, healthcheck at `/api/health`, 3 retries
- `Dockerfile.railway` — Multi-stage: Node 20 builds FE → Python 3.12-slim serves both
- Backend runs via `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- `.env.example` documents `DATABASE_URL`, `OPENROUTER_API_KEY`, `GROQ_API_KEY`, `HF_API_KEY`
- First deploy: `railway login` → `railway init` → `railway up`
- Set env vars in Railway Dashboard (Variables tab) — keys are auto-injected

### Docker Deployment
- `docker compose build` — Build backend + frontend images
- `docker compose up -d` — Start services (backend:8000, frontend:80)
- `docker compose down` — Stop services
- Backend API: `http://localhost:8000/api/standards`
- Frontend UI: `http://localhost/`
- Backend `.env` is mounted read-only from `backend/.env`
- Upload volume persists across restarts via `uploads` named volume

### Tests
- `cd backend && python -m pytest tests/ -v` — Run 285 tests (unit + integration)
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
- 7 standards from scratch: iso_37301, iso_42001, iso_30401, iso_27701, iso_31000, iso_10002, iso_13485
- **iso_22301 fix**: table with merged cells (`no 'tc' element`) — graceful fallback to from-scratch generation

### Provider Rate Limiting
- `rate_limiter.py` — sliding window per provider, checked in `router.py` before each call
- Limits: hf=10, gemini=60, openai=60, claude=50, local=30, groq=30, openrouter=30, agentrouter=60 req/min
- Thread-safe via `threading.Lock()`

### Provider Health Tracking
- `router.py` tracks consecutive failures per provider in `_provider_health` dict
- After **3 consecutive fails**, provider is skipped (logged as "degraded")
- Counter resets to 0 on any successful call

### Response Cache
- `router.py` caches results by md5 hash of `task_type:prompt`
- TTL: 1 hour (`_CACHE_TTL = 3600`)
- Cache hit skips the provider chain entirely

### HF Cooldown
- `hf_provider.py` detects 402/429/503 errors from HuggingFace Inference API
- Sets exponential cooldown: 60s → 120s → 300s → 600s max
- 0.8s inter-request minimum gap
- Quick-fails on cooldown without wasting an API call

### Thread Safety
- `generate_background` wrapper catches all `Exception`, logs traceback, sets `status=error` in progress_store
- Server restart: `fuser -k 8000/tcp` to release bound port

### Git
- Git auto-pushes every commit on `main` via `.git/hooks/post-commit`
- PAT token stored in `~/.git-credentials`
- Manual push: `git push origin main`
