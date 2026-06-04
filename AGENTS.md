# ComplianceHub — Agent Instructions

## Commands

### Backend (Python / FastAPI)
- `cd backend && python -m compileall . -q` — Check all Python syntax
- `cd backend && python -c "from app.main import app; print('OK')"` — Verify imports
- `cd backend && uvicorn app.main:app --port 8000` — Start development server
- `cd backend && curl http://localhost:8000/api/standards` — Smoke-test API

### Frontend (React / Vite)
- `cd frontend && npm run lint` — ESLint check
- `cd frontend && npm run build` — Production build
- `cd frontend && npm run dev` — Development server (port 5173)

### Git
- Git auto-pushes every commit on `main` via `.git/hooks/post-commit`
- PAT token stored in `~/.git-credentials`
- Manual push: `git push origin main`
