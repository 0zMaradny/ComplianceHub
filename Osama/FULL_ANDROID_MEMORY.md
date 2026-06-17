# FULL ANDROID MEMORY — Complete Chat History

## Initial Problem & Goal

### Problem
ComplianceHub running on Android (proot) with opencode CLI. Railway deployment expiring ($4.62/23 days remaining). Need to replicate environment on Windows laptop with:
- **No admin rights** — all per-user installs
- **No WSL** (can't install without admin)
- **Python 3.14.5**, no Node.js, no Git on Windows
- **GitHub Desktop** available for git

### Goal
Full dual-device system:
- **Android**: Mobile coding + tunnel host (cloudflared)
- **Windows**: Heavy lifter — local backend, documents, Cherry Studio
- **Cross-device**: MEMORY.md + tunnel URL shared via git

---

## What Was Built

### 1. claude-mem MCP Server
- 21 tools registered, most need cloud backend
- `smart_search`/`smart_outline`/`smart_unfold` work via tree-sitter CLI
- `search` works via SQLite FTS5 fallback
- `timeline`/`get_observations`/`observation_*`/`memory_*` — broken (chroma or server-beta)
- 7 observations seeded directly into SQLite

### 2. Cross-Device Sync System
- **go.sh**: Android — git pull on start, git commit+push MEMORY.md + tunnel URL on exit
- **sync.sh**: Android convenience script
- **sync.ps1**: Windows PowerShell sync script
- **tunnel.sh**: Watchdog with Cloudflare → Serveo fallback
- **Osama/.tunnel-url**: Git-tracked tunnel URL file

### 3. File Parser Enhancement
- Added `markitdown` (base package) for PDF/XLSX/PPTX/HTML/CSV/JSON/XML parsing

### 4. AI Router Updates
- `response_format` JSON schema in `extract_structured()` — API-enforced valid JSON
- `provider.sort: price` removed — quality preferred over cheapest

### 5. Windows Setup Files
- `setup-windows.ps1`, `go.ps1`, `WINDOWS_SETUP.md`, `sync.ps1`

### 6. Git Commits
- `05086e1`: 46 files (AGENTS.md, HUMANIZE.md, Cherry config, routes, tests, scripts)
- `58c046e`: Windows setup files
- `850b505`: Find-Git auto-detect + auto-sync + memory files

---

## Current Session — Cherry Studio + OpenCode Desktop Config

### Cherry Studio — Provider Status
| Provider | Key? | Status |
|----------|------|--------|
| **cherryIn** | No key | ✅ Works (free models) |
| **OpenRouter** | Has key | ✅ Works (free models, $0 balance) |
| **DeepSeek** direct | Needs key | ❌ Not configured |
| **SiliconFlow** | Needs key | ❌ Not configured |
| **BigModel** | Needs key | ❌ Not configured |
| **Anthropic** | Has key | ❌ Connection failed in KSA |
| **OpenAI** | Invalid key | ❌ Auth failed |
| **Groq** | None added | ❌ Models no longer supported |
| **Google Gemini** | — | ❌ Not available in provider list |

### Cherry Studio — 3 Model Slots
| Slot | Provider | Model |
|------|----------|-------|
| Default Assistant | **cherryIn** | TBD (need free model names from dropdown) |
| Quick Model | **cherryIn** | TBD |
| Translate Model | **cherryIn** | TBD |

### Cherry Studio — Settings Done
- General: English, Enter to send
- Display: Font 14, auto-scroll ON
- Memories: ON
- Document Processing: All formats, 50MB, OCR OFF
- MCP/API/Channels/Tasks/Phrases/Quick Assistant/Selection Assistant: SKIP
- Skills/Web Search/Keyboard Shortcuts: SKIP

### Cherry Studio — 9 Agents to Create
Each with per-agent model + system prompt. Knowledge files: AGENTS.md, MEMORY.md.
1. **Lead Auditor** — NC precision, assessment role
2. **Lead Implementer** — Systems builder, client formulas
3. **AI Developer** — Python automation, CONFIG block
4. **Excel Engineer** — openpyxl, live formulas
5. **Arabic Writer** — MSA, ISO docs, RTL
6. **Personal Concierge** — Lifestyle, KSA context
7. **Platform Engineer** — FastAPI+React, ComplianceHub
8. **Prompt Architect** — 12-part anatomy framework
9. **Delivery Manager** — Six-Gate pipeline

### Cherry Studio — New UI
- **Agents tab** (separate from Assistants) — supports per-agent model + tools
- **OpenClaw plugin** installed — features TBD

### Windows Scripts Status
- `setup-windows.ps1` — Find-Git function added ✅
- `go.ps1` — Find-Git + auto-sync on start/exit ✅
- `sync.ps1` — Find-Git function added ✅

---

## Blocked Items

| Issue | Workaround |
|-------|-----------|
| Anthropic blocked in KSA | Use Claude through OpenRouter (add $1 at https://openrouter.ai/settings/credits) |
| OpenAI key invalid | Get fresh key at https://platform.openai.com/api-keys |
| Groq removed from Cherry Studio | Not usable |
| Google Gemini not available | Not usable |
| Railway expiring | Replaced by Android tunnel + Windows local backend |

---

## NTIS IMS Audit (ISO 27001 + ISO 22301)

- **Date**: 2-day audit (ongoing)
- **Tools**: ComplianceHub doc gen, Cherry Studio assistants, OpenCode for code
- **Daily flow**: Morning `.\go.ps1` (pulls Android tunnel), evening Enter to stop (pushes MEMORY.md)
- Android: `bash go.sh` for tunnel + backend

---

## OpenCode Desktop Setup Guide (Windows)

### Step 1: Settings → Providers
Add these API keys (user pastes them):

| Provider | Key prefix |
|----------|-----------|
| OpenRouter | `sk-or-...` |
| OpenAI | `sk-proj-...` |
| Anthropic | `sk-ant-...` (may fail in KSA — skip if so) |

If user has only OpenRouter working, use OpenRouter for everything.

### Step 2: Settings → Model
- Default model: `nvidia/llama-3.3-nemotron-super-49b-v1` (OpenRouter, free, 128K context)
- Reasoning: ON

### Step 3: Settings → Instructions (System Prompt)
Paste this exactly:

```
You are ComplianceHub — an ISO compliance automation assistant. The project is at C:\Users\eos\ComplianceHub.

Always read AGENTS.md and HUMANIZE.md before responding. All output must sound human-written — scan for AI patterns before responding.

Arabic MSA for MSD-MOI outputs, English for technical notes. ISO clause refs stay in English.

For audit work: prioritize NC precision over general advice.
For code: modular Python, CONFIG block at top, zero pyflakes errors.
For document generation: work through the 7-phase pipeline.
For Excel: openpyxl with live formulas, hidden _Data sheets, A4 print layout.

Client formulas are non-negotiable. Client isolation is required.

Available commands: see AGENTS.md for full reference.
```

### Step 4: Settings → Servers (MCP)
Add claude-mem server. Find the mcp-server.cjs path first by running in PowerShell:

```powershell
Get-ChildItem -Path "$env:LOCALAPPDATA\claude\plugins" -Recurse -Filter "mcp-server.cjs" | Select FullName
```

Then add:

| Field | Value |
|-------|-------|
| Name | `claude-mem` |
| Type | Command (stdio) |
| Command | `node` |
| Arguments | Full path to mcp-server.cjs |
| Environment | `NODE_PATH=<node_modules_path>;CLAUDE_MEM_WORKER_PORT=37700` |
| Working Directory | `C:\Users\eos\ComplianceHub` |

Find node_modules path by looking in:
```
$env:LOCALAPPDATA\claude\plugins\cache\thedotmack\claude-mem\*\node_modules
```

### Step 5: Settings → Skills
- Enable any skills found at `.opencode/skills/`
- Should include: humanize-voice, and any skills defined in the repo

### Step 6: Workspace
- Set project root to `C:\Users\eos\ComplianceHub`
- OpenCode will auto-detect the project structure

---

## ComplianceHub Backend

### API Keys (`backend\.env`)
Open `C:\Users\eos\ComplianceHub\backend\.env` in Notepad and paste:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=
```

### Start Backend
```powershell
cd C:\Users\eos\ComplianceHub
.\go.ps1
```
Auto-pulls from git, starts backend on localhost:8000, on Enter auto-pushes MEMORY.md.

---

## Next Steps
1. Read cherryIn free model names → assign 3 model slots
2. Create 9 Agents in Cherry Studio
3. Configure OpenCode Desktop + MCP
4. Add API keys to `backend\.env`
5. Test `.\go.ps1`
6. Set up Windows Task Scheduler for daily sync
