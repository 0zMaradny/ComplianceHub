# ComplianceHub — Windows Setup Guide

Two paths depending on whether you have admin rights:

| Path | Admin needed | How backend runs |
|------|-------------|-----------------|
| **A — Native (no admin)** ⭐ | No | Python directly on Windows |
| **B — WSL** | Yes (one-time) | Python in WSL Ubuntu |

---

## Path A: Native Windows (No Admin)

### Step 1 — Install Git Portable

```cmd
# Download from:
https://github.com/git-for-windows/git/releases
# Look for: PortableGit-2.49.0-64-bit.7z.exe
# Extract to: C:\Users\eos\git
```

Add to PATH (PowerShell):
```powershell
[Environment]::SetEnvironmentVariable("Path", "$env:USERPROFILE\git\cmd;" + [Environment]::GetEnvironmentVariable("Path", "User"), "User")
```

Close and reopen PowerShell. Verify:
```
git --version
```

### Step 2 — Install Node.js Portable

```cmd
# Download from:
https://nodejs.org/dist/latest/
# Look for: node-v22.x.x-win-x64.zip
# Extract to: C:\Users\eos\node
```

Add to PATH (PowerShell):
```powershell
[Environment]::SetEnvironmentVariable("Path", "$env:USERPROFILE\node;" + [Environment]::GetEnvironmentVariable("Path", "User"), "User")
```

Close and reopen PowerShell. Verify:
```
node --version
npm --version
```

### Step 3 — Clone + Setup

```powershell
# Clone the repo
cd ~
git clone https://github.com/0zMaradny/ComplianceHub.git
cd ComplianceHub

# Run setup script (installs Python deps, frontend, claude-mem)
.\setup-windows.ps1
```

### Step 4 — Add API Keys

```cmd
notepad backend\.env
```

Fill in:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
GROQ_API_KEY=gsk_...
```

### Step 5 — Start the Backend

```powershell
.\go.ps1
# Opens http://localhost:8000
# Press Enter to stop
```

### Step 6 — Configure opencode Desktop

| Setting | Value |
|---------|-------|
| **Custom Instructions** | Add `AGENTS.md` + `HUMANIZE.md` from repo |
| **MCP → Add Server** | command: `node`, args: path to claude-mem `mcp-server.cjs` |
| **MCP environment** | `NODE_PATH` + `CLAUDE_MEM_CHROMA_ENABLED=false` |
| **Working directory** | `C:\Users\eos\ComplianceHub` |

Find the MCP server path:
```
dir /s %LOCALAPPDATA%\claude\plugins\mcp-server.cjs
```

### Step 7 — Cherry Studio

Create 9 assistants following `Osama/CHERRY_STUDIO_ASSISTANTS.md`

---

## Path B: WSL (if you get admin rights later)

```bash
# 1. Enable WSL (needs admin once)
wsl --install -d Ubuntu

# 2. In WSL terminal
cd ~
git clone https://github.com/0zMaradny/ComplianceHub.git
cd ComplianceHub
bash setup-wsl.sh

# 3. Add API keys
nano backend/.env

# 4. Start
bash go.sh
```

---

## Daily Workflows

| What | Command |
|------|---------|
| Start backend | `.\go.ps1` |
| Start opencode | Open opencode Desktop → set working dir to repo |
| See Android tunnel | `git pull` → `type Osama\.tunnel-url` |
| Sync MEMORY.md | `bash sync.sh` (if Git Bash installed) or `git add Osama\MEMORY.md && git commit -m "update" && git push` |
| Stop backend | Press Enter in `go.ps1` window |

---

## Shared vs Per-Device

| Asset | Where | Sync? |
|-------|-------|-------|
| Project code | repo | Via git push/pull |
| MEMORY.md | `Osama/MEMORY.md` | Auto-committed on exit |
| Tunnel URL | `Osama/.tunnel-url` | Auto-committed on tunnel start (Android) |
| API keys | `backend/.env` | Per-device (never shared) |
| claude-mem DB | `~/.claude-mem/` | Per-device SQLite |
| Cherry Studio config | `Osama/CHERRY_STUDIO_ASSISTANTS.md` | Same file, manual setup |
