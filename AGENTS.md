# ComplianceHub — Agent Instructions

## Content Modes (API Key → Provider Chain)

| Mode | API Key | Provider Chain | Speed | Quality |
|------|---------|----------------|-------|---------|
| **Cloud AI** | Valid key | gemini → openai → claude → hf → local | Fast | Best |
| **HF Free** | HF_API_KEY set | hf → local → offline | Medium | Good |
| **Local AI** | Empty (+ model running) | local → offline | Slow | OK |
| **Offline** | Empty (no model) | offline only | Instant | Professional |

## Commands

### Run Servers
- `bash run.sh` — Start backend + frontend (offline mode)
- `bash run.sh --local-ai` — Start with local AI model (qwen-1.5b)

### Backend (Python / FastAPI)
- `cd backend && python -m compileall . -q` — Check all Python syntax
- `cd backend && python -c "from app.main import app; print('OK')"` — Verify imports
- `cd backend && uvicorn app.main:app --port 8000` — Start backend only
- `cd backend && curl http://localhost:8000/api/standards` — Smoke-test API

### Frontend (React / Vite)
- `cd frontend && npm run lint` — ESLint check
- `cd frontend && npm run build` — Production build
- `cd frontend && npm run dev` — Development server (port 5173)

### Local AI (llama.cpp server)
- `/opt/llama-server/llama-server -m models/qwen-1.5b.gguf -c 4096 -t 8 --port 8080` — Start local model
- Model stored at `models/qwen-1.5b.gguf` (~941 MB, Q4_K_M)
- Download: `curl -L -o models/qwen-1.5b.gguf https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf`

### Cloud AI Keys
- `backend/.env` — Set GEMINI_API_KEY, OPENAI_API_KEY, CLAUDE_API_KEY, or HF_API_KEY
- HF_API_KEY: Get a free token at https://huggingface.co/settings/tokens (free inference API)

### Git
- Git auto-pushes every commit on `main` via `.git/hooks/post-commit`
- PAT token stored in `~/.git-credentials`
- Manual push: `git push origin main`
