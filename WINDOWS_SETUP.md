# ComplianceHub — Windows Setup Guide

Both devices share the same repo. Each device has its own role, its own `~/.claude-mem/` database (no cross-device sync), and they coordinate through git (MEMORY.md + tunnel URL).

---

## Device Roles

| | Android (mobile) | Windows (heavy) |
|---|---|---|
| **Use case** | Mobile coding, quick edits | Heavy AI work, full backend, document generation |
| **Backend** | Serves `:8000` + tunnel 24/7 | Runs local `:8000` or uses Android tunnel |
| **Local AI** | Qwen3-4B (ARM64) | Yes (x86_64, faster) |
| **opencode** | Connected + claude-mem | Connected + claude-mem |
| **Tunnel** | Cloudflare → Serveo fallback | Optional (local is fine) |

---

## Quick Install (one-time)

### Prerequisites
- Windows with **WSL2** + **Ubuntu** installed (from Microsoft Store)
- **Git for Windows** (comes with Git Credential Manager)
- Internet connection

### Run in WSL terminal

```bash
# 1. Clone the repo (one time)
cd ~
git clone https://github.com/YOUR-ORG/ComplianceHub.git
cd ComplianceHub

# 2. Run setup (installs everything)
bash setup-wsl.sh
```

The script installs:
- Node.js 22 + npm → `opencode-ai` → `claude-mem` → tree-sitter CLI
- Python 3 + venv → pip deps
- cloudflared (for tunnels)
- Frontend deps (`npm install`)
- `opencode.json` with claude-mem MCP paths
- Git config (tries GCM, falls back to PAT)

### After setup

```bash
# Add your API keys
nano backend/.env
# Fill in: ANTHROPIC_API_KEY, OPENROUTER_API_KEY, GROQ_API_KEY

# Start the app
bash go.sh

# Or start opencode
opencode
```

---

## Daily Workflows

### Heavy work on Windows (local backend)

```bash
bash go.sh
# Opens http://localhost:8000
# Backend runs locally with full AI pipeline
```

### Light work (use Android's tunnel)

```bash
bash sync.sh                    # Pull latest (gets Android tunnel URL)
cat Osama/.tunnel-url           # Show Android's current URL
# Open that URL in browser — Android serves the backend
# Or configure Cherry Studio to point to that URL
```

### Mobile coding on Android

```bash
bash go.sh                      # Auto-pulls → starts backend + tunnel → pushes URL to git
# On Windows later: git pull → has the URL
```

### Session end (any device)

`go.sh` auto-commits MEMORY.md changes and tunnel URL on exit. Just `Ctrl+C`.

### Manual sync anytime

```bash
bash sync.sh                    # Shortcut: pull → commit changes → push
```

---

## Cherry Studio

Create **9 assistants** on each device's Cherry Studio. Config is the same:

```
Open Osama/CHERRY_STUDIO_ASSISTANTS.md
```

Each assistant entry specifies:
- **System prompt** — copy verbatim
- **Knowledge Base** — files to attach (all in the repo)
- **Model** — use what your Cherry Studio provider offers

Changes to the assistant config are tracked in git — keep both devices in sync.

---

## Shared vs Per-Device

| Asset | Where | Synchronized? |
|-------|-------|---------------|
| Project code | repo | Via git push/pull |
| MEMORY.md | `Osama/MEMORY.md` | Yes — auto-committed by go.sh on exit |
| Tunnel URL | `Osama/.tunnel-url` | Yes — auto-committed by go.sh after tunnel starts |
| API keys | `backend/.env` | **No** — each device has its own keys |
| claude-mem DB | `~/.claude-mem/` | **No** — per-device SQLite, no sync |
| Cherry Studio config | `Osama/CHERRY_STUDIO_ASSISTANTS.md` | Yes — same file, manual setup per device |
| AGENTS.md, Context.md, Skills | repo | Via git push/pull |

---

## Cherry Studio Assistants (9)

Create these 9 assistants in Cherry Studio on each device. Use the full config at `Osama/CHERRY_STUDIO_ASSISTANTS.md`.

Quick reference:

| # | Name | Model (Windows) | Model (Android) |
|---|------|-----------------|-----------------|
| 1 | Lead Auditor | Claude Sonnet 4 | Claude Sonnet 4 |
| 2 | Lead Implementer | Claude / Nemotron 550B | Claude / Nemotron 550B |
| 3 | AI Developer | Qwen3 Coder 480B | Qwen3 Coder 480B |
| 4 | Excel Engineer | Claude / Qwen3 Coder | Claude / Qwen3 Coder |
| 5 | Arabic Writer | Claude | Claude |
| 6 | Personal Concierge | Any fast model | Any fast model |
| 7 | Platform Engineer | Claude / Nemotron 550B | Claude / Nemotron 550B |
| 8 | Prompt Architect | Any | Any |
| 9 | Delivery Manager | Any | Any |

---

## Memory Architecture

```
Three-tier memory:

1. Anthropic Memory (claude.ai web only)
   └─ Not available in opencode CLI or Cherry Studio

2. MEMORY.md (git-tracked, shared between devices)
   ├─ Session history, corrections, preferences
   ├─ Auto-committed by go.sh on exit
   └─ Primary shared memory — push/pull to sync

3. claude-mem (per-device local SQLite)
   ├─ Each device has its own ~/.claude-mem/claude-mem.db
   ├─ No cross-device sync (different conversations)
   ├─ MCP tools: search ✓, smart_search ✓, smart_outline ✓
   └─ Timeline/get_observations ✗ (need chroma-mcp cloud backend)
```

---

## Troubleshooting

**Git says "pull failed"**
```bash
# Likely network or no commits to pull. Run manually:
git pull --rebase --autostash
```

**opencode.json missing**
```bash
cp opencode.json.template opencode.json
```

**Tunnel URL stale**
```bash
git pull
cat Osama/.tunnel-url
# If empty: Android hasn't started go.sh yet, or no tunnel connected
```

**"tree-sitter: command not found" in smart tools**
```bash
find ~/.claude/plugins -path "*/tree-sitter-cli" -type d | while read d; do
  (cd "$d" && node install.js)
done
```

**Port 8000 in use**
```bash
fuser -k 8000/tcp
```
