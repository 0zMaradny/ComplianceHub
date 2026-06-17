# MEMORY.md — Current Session State

## Cherry Studio Setup (Windows)

### Provider Status
| Provider | Key? | Status |
|----------|------|--------|
| **cherryIn** | No key | ✅ Works |
| **OpenRouter** | Has key | ✅ Works (free models, $0 balance) |
| **DeepSeek** direct | Needs key | ❌ Not configured |
| **SiliconFlow** | Needs key | ❌ Not configured |
| **BigModel** | Needs key | ❌ Not configured |
| **Anthropic** | Has key | ❌ Connection failed in KSA |
| **OpenAI** | Invalid key | ❌ Auth failed |
| **Groq** | — | ❌ Models no longer supported |
| **Google Gemini** | — | ❌ Not available |

### 3 Model Slots
| Slot | Provider | Model |
|------|----------|-------|
| Default Assistant | **cherryIn** | TBD |
| Quick Model | **cherryIn** | TBD |
| Translate Model | **cherryIn** | TBD |

### Settings Done
- General: English, Enter to send
- Display: Font 14, auto-scroll ON
- Memories: ON
- Document Processing: All formats, 50MB, OCR OFF
- MCP/API/Channels/Tasks/Phrases/Quick/Selection Assistant: SKIP

### 9 Agents to Create
Knowledge files: AGENTS.md, MEMORY.md.
1. **Lead Auditor** — NC precision
2. **Lead Implementer** — Client formulas non-negotiable
3. **AI Developer** — CONFIG block at top
4. **Excel Engineer** — openpyxl, hidden _Data sheets
5. **Arabic Writer** — MSA, ISO refs in English
6. **Personal Concierge** — KSA context
7. **Platform Engineer** — FastAPI+React, ComplianceHub
8. **Prompt Architect** — 12-part anatomy
9. **Delivery Manager** — Six-Gate pipeline

### New UI
- **Agents tab**: per-agent model + tools
- **OpenClaw plugin**: installed, features TBD

---

## OpenCode Desktop Setup Guide (Windows)

### Step 1: Settings → Providers
| Provider | Key |
|----------|-----|
| OpenRouter | `sk-or-...` |
| OpenAI | `sk-proj-...` |
| Anthropic | `sk-ant-...` (skip if blocked) |

### Step 2: Settings → Model
- Default: `nvidia/llama-3.3-nemotron-super-49b-v1` (OpenRouter, free, 128K)

### Step 3: Settings → Instructions (System Prompt)
```
You are ComplianceHub — an ISO compliance automation assistant. The project is at C:\Users\eos\ComplianceHub.

Always read AGENTS.md and HUMANIZE.md before responding. All output must sound human-written — scan for AI patterns before responding.

Arabic MSA for MSD-MOI outputs, English for technical notes. ISO clause refs stay in English.

For audit work: prioritize NC precision over general advice.
For code: modular Python, CONFIG block at top, zero pyflakes errors.
For document generation: work through the 7-phase pipeline.
For Excel: openpyxl with live formulas, hidden _Data sheets, A4 print layout.

Client formulas are non-negotiable. Client isolation is required.
```

### Step 4: Settings → Servers (MCP)
Find the mcp-server.cjs path:
```powershell
Get-ChildItem -Path "$env:LOCALAPPDATA\claude\plugins" -Recurse -Filter "mcp-server.cjs" | Select FullName
```
Add server with Type=stdio, Command=node, Env=`NODE_PATH=...;CLAUDE_MEM_WORKER_PORT=37700`

### Step 5: Settings → Skills → Enable `.opencode/skills/`

### Step 6: Settings → Workspace → `C:\Users\eos\ComplianceHub`

---

## ComplianceHub Backend

### API Keys (`backend\.env`)
```
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=
```

### Start
```powershell
cd C:\Users\eos\ComplianceHub
.\go.ps1
```
Auto-sync: pulls on start, pushes MEMORY.md + `.tunnel-url` on exit.

---

## Blocked Items
| Issue | Workaround |
|-------|-----------|
| Anthropic blocked | Use through OpenRouter (add $1 at https://openrouter.ai/settings/credits) |
| OpenAI key invalid | Fresh key at https://platform.openai.com/api-keys |
| Groq removed | Not usable |
| Gemini not available | Not usable |
| Railway expiring | Android tunnel + Windows local backend |

---

## NTIS IMS Audit (ISO 27001 + ISO 22301)
- 2-day audit (ongoing)
- Tools: ComplianceHub doc gen, Cherry Studio agents, OpenCode
- Windows: `.\go.ps1` morning/evening
- Android: `bash go.sh` for tunnel + backend

---

## Next Steps
1. Read cherryIn free model names → assign 3 slots
2. Create 9 Agents in Cherry Studio
3. Configure OpenCode Desktop + MCP
4. Add API keys to `backend\.env`
5. Test `.\go.ps1`
6. Set up Windows Task Scheduler
