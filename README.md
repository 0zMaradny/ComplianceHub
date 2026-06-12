# ComplianceHub

Audit & Compliance Document Generation Platform — AI-powered audit documentation with **14 ISO standards**, **32 document types**, IAF-compliant Manday calculation, and full audit workflow management.

## Quick Start

```bash
bash run.sh              # Offline mode (no AI) — instant, all 32 docs
bash run.sh --local-ai   # With local AI model (Qwen2.5-0.5B)
```

Then open **http://localhost:5173**

## Architecture

```
backend/                  # FastAPI (Python 3.12)
  app/
    main.py               # 43 API routes
    services/             # 22 business logic modules
      clause_data.py      # Clause database (14 standards)
      offline_generator.py # Template-based doc content (32 types)
      document_generator.py # DOCX generation with TÜV templates
      ai/                 # 3-tier AI router (9 free models)
    config.py             # Standards, docs, labels configuration
  tests/                  # 342 tests (pytest)
frontend/                 # React 19 + Vite 8 + Tailwind CSS v4
  src/
    pages/                # 12 pages (Dashboard, Audit, History, etc.)
    components/           # Shared UI components
```

## Deployment (Railway)

1. Push to GitHub → connect repo at https://railway.app
2. Railway auto-detects `railway.json` → builds via `Dockerfile.railway`
3. Set these **Variables** in Railway dashboard:

| Variable | Required | Purpose |
|---|---|---|
| `OPENROUTER_API_KEY` | ✅ | 8 free frontier+strong AI models |
| `GROQ_API_KEY` | ✅ | Groq Llama 3.3 70B (fastest ~800 t/s) |
| `HF_API_KEY` | Optional | HuggingFace free tier fallback |

4. Open your `*.up.railway.app` URL in browser — zero installs.

## Content Modes

| Mode | API Keys | Speed | Quality |
|---|---|---|---|
| **Offline** (default) | None needed | **Instant** (0.8s / 32 docs) | Professional, template-based |
| **OpenRouter** | `OPENROUTER_API_KEY` | ~3-8s/doc | 9 frontier/strong models, all free |
| **Groq** | `GROQ_API_KEY` | ~1-2s/doc | Llama 3.3 70B, fastest |
| **HuggingFace** | `HF_API_KEY` | ~5-10s/doc | Llama-3-8B, free tier |
| **Local AI** | llama-server + GGUF | ~20s/doc | Qwen2.5-0.5B (469 MB) |

## 14 ISO Standards

| Key | Standard | Doc Types |
|---|---|---|
| `iso_9001` | ISO 9001:2015 — Quality | 32 |
| `iso_14001` | ISO 14001:2015 — Environmental | 32 |
| `iso_45001` | ISO 45001:2018 — OH&S | 32 |
| `iso_50001` | ISO 50001:2018 — Energy | 32 |
| `iso_27001` | ISO 27001:2022 — InfoSec | 32 |
| `iso_20000` | ISO 20000-1:2018 — Service Mgmt | 32 |
| `iso_22301` | ISO 22301:2019 — Business Continuity | 32 |
| `iso_37301` | ISO 37301:2021 — Compliance | 32 |
| `iso_42001` | ISO 42001:2023 — AI Management | 32 |
| `iso_30401` | ISO 30401:2018 — Knowledge Mgmt | 32 |
| `iso_27701` | ISO 27701:2025 — Privacy | 32 |
| `iso_31000` | ISO 31000:2018 — Risk (Guidelines) | 32 |
| `iso_13485` | ISO 13485:2016 — Medical Devices | 32 |
| `iso_10002` | ISO 10002:2018 — Complaints | 32 |

All 14 standards produce the same 32 document types — content adapts to each standard's clause structure.

## 32 Document Types

**Audit Package (8):** Audit Plan Stage 1 & 2, Participation List, Audit Report, ISO Checklist, Certificate Text, TNL (Nonconformity List), Certificate

**Standalone (24):** Management Review Minutes, Corrective Action Report, Gap Analysis Report, Statement of Applicability, Business Impact Analysis, Records of Processing Activities, Risk Treatment Plan, Incident Investigation Report, Internal Audit Program, Environmental Aspect Register, Hazard Identification Register, Energy Review, Compliance Obligations Register, Service Portfolio, Service Catalogue, Supplier Agreement Register, Business Relationship Register, Capacity Management Plan, Change Management Register, Release Deployment Plan, Incident Management Log, Problem Management Register, Service Continuity Plan, Availability Management Report

## Key Features

- **DOCX + PDF** generation with TÜV Austria template injection (15 templates)
- **Manday calculator**: IAF MD 5 tables, audit type multipliers, IAF MD 11 IMS reduction matrix
- **Audit workflow**: 6-gate pipeline with NC/CAPA tracking and evidence management
- **AI Router**: 3-tier parallel fallback (4 frontier → 4 strong → Groq), 9 free models
- **Offline generator**: Zero-dependency template engine produces all 32 docs in ~0.8s
- **Data-driven findings**: Parses NCs, OFIs, positives from audit notes → real content in documents
- **SQLite persistence**: Job history, NC tracking, compliance assessments, CAPA metrics
- **SSE streaming**: Real-time progress updates during long-running AI generations
- **Dark mode**: Toggleable light/dark theme, persisted to localStorage
- **Responsive**: Mobile sidebar drawer, touch-friendly inputs, horizontal table scroll
- **Bilingual**: Turkish/English document output

## Commands

```bash
# Backend
cd backend && uvicorn app.main:app --port 8000
cd backend && python -m pytest tests/ -v          # 342 tests
cd backend && python -m pyflakes app/             # Zero warnings

# Frontend
cd frontend && npm run dev          # Dev server (port 5173)
cd frontend && npm run build        # Production build (~422ms)
cd frontend && npm run lint         # ESLint check

# Docker
docker compose up -d                # Backend:8000 + Frontend:80
```

## Code Quality

| Check | Status |
|---|---|
| Backend tests | **342 pass** (unit + integration) |
| Python syntax | `compileall` — zero errors |
| Pyflakes | `pyflakes app/` — zero warnings |
| Frontend build | Clean, ~422ms, ~17KB CSS (tree-shaken Tailwind) |
| Frontend lint | ESLint — clean |
