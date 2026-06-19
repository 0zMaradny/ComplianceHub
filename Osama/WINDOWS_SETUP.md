# Windows Setup — Cherry Studio + OpenCode Desktop

**Tunnel URL:** `https://consortium-exports-sacramento-parent.trycloudflare.com`
(Check current URL on Android: `cat /tmp/compliancehub-url.txt`)

---

## Cherry Studio Setup

### Provider
1. **Settings → Model Provider → Add Provider**
2. Type: **OpenAI**
3. Name: `Antigravity`
4. API URL: `https://consortium-exports-sacramento-parent.trycloudflare.com/v1/chat/completions`
5. Model: `claude-sonnet-4-6`
6. API Key: any dummy value (e.g. `sk-antigravity`)
7. Save

### 3 Model Slots
| Slot | Model |
|------|-------|
| Default Assistant | `claude-sonnet-4-6` |
| Quick Model | `claude-sonnet-4-6` |
| Translate Model | `claude-sonnet-4-6` |

### 9 Agents (from `Osama/CHERRY_STUDIO_ASSISTANTS.md`)
Assign all to Antigravity provider. Knowledge files: `AGENTS.md`, `MEMORY.md`, `HUMANIZE.md`.

| # | Agent | Slot Assignment |
|---|-------|----------------|
| 1 | Lead Auditor | Default |
| 2 | Lead Implementer | Default |
| 3 | AI Developer | Quick |
| 4 | Excel Engineer | Quick |
| 5 | Arabic Writer | Translate |
| 6 | Personal Concierge | Quick |
| 7 | Platform Engineer | Default |
| 8 | Prompt Architect | Quick |
| 9 | Delivery Manager | Quick |

### Global Settings
- Language: English
- Enter to send: ON
- Font size: 14
- Auto-scroll: ON
- Memories: ON
- Document processing: all formats, 50MB, OCR OFF

---

## OpenCode Desktop Setup

### Provider
1. **Settings → Providers → Add**
2. Type: **OpenAI-compatible**
3. Name: `Antigravity`
4. Base URL: `https://consortium-exports-sacramento-parent.trycloudflare.com/v1/chat/completions`
5. Model: `claude-sonnet-4-6`
6. API Key: any dummy value
7. Save

### Backup Provider (for when tunnel is down)
1. **Settings → Providers → Add**
2. Type: **OpenRouter**
3. API Key: `<openrouter-key-from-backend-.env>`
4. Model: `nvidia/nemotron-3-ultra-550b-a55b:free`
5. Save

### System Prompt (Settings → Instructions)
```
You are ComplianceHub — an ISO compliance automation assistant.

Always read AGENTS.md and HUMANIZE.md before responding.

Arabic MSA for deliverables, English for technical notes.
ISO clause refs stay in English.

For audit work: prioritize NC precision over general advice.
For code: modular Python, CONFIG block at top, zero pyflakes errors.
Client formulas are non-negotiable. Client isolation is required.
```

### MCP (Settings → Servers → Add)
Search for `mcp-server.cjs`:
```powershell
Get-ChildItem -Path "$env:LOCALAPPDATA\claude\plugins" -Recurse -Filter "mcp-server.cjs" | Select FullName
```
- Type: **stdio**
- Command: `node`
- Args: `<path-to-mcp-server.cjs>`
- Env: `NODE_PATH=<parent-node_modules>;CLAUDE_MEM_WORKER_PORT=37700`

### Skills
- Settings → Skills → Enable `.opencode/skills/`

### Workspace
- Settings → Workspace → `C:\Users\eos\ComplianceHub`

---

## go.ps1 (ComplianceHub Launcher)
Run in PowerShell:
```powershell
cd C:\Users\eos\ComplianceHub
.\go.ps1
```

### What it does:
1. `git pull` — syncs latest changes (MEMORY.md, code, configs)
2. Starts the backend on Windows (not needed for tunnel mode)
3. On exit: `git add -A && git commit -m "sync" && git push`

### Sync script (for manual run):
```powershell
.\sync.ps1
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tunnel URL changed | Run `cat /tmp/compliancehub-url.txt` on Android, update provider URL |
| Antigravity model fails (502) | Backend auto-falls to OpenRouter → Groq → Local |
| Backend down | Watchdog restarts within 10 min, or run `bash backend/start.sh` |
| Cherry Studio can't connect | Check tunnel URL is current, check Android internet |
| Wrong tunnel URL | It changes each restart — always check current value |
