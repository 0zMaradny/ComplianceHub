# ComplianceHub

Audit & Compliance Document Generation Platform — AI-powered audit documentation with 13 ISO standard support, IAF-compliant Manday calculation, and full audit workflow management.

## Quick Start

```bash
bash run.sh              # Offline mode (no AI)
bash run.sh --local-ai   # With local AI model
```

Then open http://localhost:5173

## Architecture

```
backend/                  # FastAPI (Python 3.12)
  app/
    main.py               # 43 API routes
    services/             # Business logic (16 modules)
    config.py             # Configuration
    utils.py              # Helpers
  tests/                  # 181 tests (pytest)
frontend/                 # React + Vite
  src/
    pages/                # Dashboard, Audit, History, Compliance, Projects
    components/           # Reusable components
```

## Content Modes

| Mode | Requires | Provider Chain |
|------|----------|---------------|
| Offline | Nothing | Built-in generator (instant) |
| Local AI | llama-server + GGUF model | local → offline |
| HuggingFace | `HF_API_KEY` | hf → local → offline |
| Cloud AI | Gemini/OpenAI key | gemini → openai → hf → local |

## 13 Supported Standards

ISO 9001, 14001, 45001, 50001, 27001, 20000, 22301, 37301, 42001, 30401, 27701, 31000, 10002.

## Key Features

- **8 document types**: Audit Plan, Report, Certificate (Text + Image), Checklist, TNL, Participation List, ISO Summary
- **DOCX + PDF** generation with TÜV Austria template injection
- **Manday calculator**: IAF MD 5 tables, audit type multipliers, IAF MD 11 IMS reduction
- **Audit workflow**: 6-gate pipeline with NC/CAPA tracking and evidence management
- **SQLite persistence**: job history, dashboard analytics, compliance assessments
- **SSE streaming**: real-time progress for long-running generations
- **Excel export**: risk register, BIA workbook, ENMS register, KPI dashboard
- **Bilingual**: Turkish/English document output

## Commands

```bash
# Backend
cd backend && uvicorn app.main:app --port 8000

# Frontend
cd frontend && npm run dev

# Tests
cd backend && python -m pytest tests/ -v          # 181 tests
cd frontend && npm test                            # Frontend tests

# Code quality
cd backend && python -m pyflakes app/
cd frontend && npm run lint
cd frontend && npm run build

# Docker
docker compose up -d
```
