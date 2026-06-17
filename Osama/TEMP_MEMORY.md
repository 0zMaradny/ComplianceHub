# TEMP MEMORY — OpenCode Desktop Setup (Windows)

## Context
The user is setting up ComplianceHub on Windows. Cherry Studio is partially configured. Now need to configure OpenCode Desktop (v1.17.1) and finish remaining setup.

## Working Directory
`C:\Users\eos\ComplianceHub`

## OpenCode Desktop Configuration

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

This auto-pulls from git, starts backend on localhost:8000, and on Enter auto-pushes MEMORY.md back.

## Cherry Studio Status (already configured)
- 3 model slots: all cherryIn (free models)
- Providers: cherryIn, OpenRouter, DeepSeek (needs key), SiliconFlow (needs key), BigModel (needs key)
- 9 Agents not yet created — system prompts ready in AGENTS.md
- Settings done: General, Display, Memories, Document Processing
- OpenClaw plugin installed

## Next Steps After OpenCode Setup
1. Test backend: visit http://localhost:8000/api/health
2. Create 9 Agents in Cherry Studio
3. Test git sync: run `.\sync.ps1`
4. Set up Windows Task Scheduler for automatic daily sync
5. Good to go for NTIS IMS Audit (ISO 27001 + ISO 22301)

## Daily Workflow
- **Morning**: `.\go.ps1` → auto-pulls Android tunnel URL + latest MEMORY.md
- **During audit**: Cherry Studio agents for Q&A, ComplianceHub for doc gen
- **Evening**: Press Enter in go.ps1 → auto-commits + pushes MEMORY.md
- Android runs `bash go.sh` at the same time for tunnel
