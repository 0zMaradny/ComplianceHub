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

## Antigravity API — Free Claude via Google (CONFIRMED June 18)

**Status: ✅ WORKING**
- Plugin client ID + PKCE OAuth → access + refresh tokens obtained
- **Claude Sonnet 4.6**: ✅ PASS (free, unlimited via Antigravity)
- **Claude Opus 4.6 Thinking**: ✅ PASS (free, unlimited via Antigravity)
- **Gemini 3 Pro**: ❌ FAIL (500/401 — different endpoint needed)
- Token refresh: ✅ Verified (works, 3599s expiry)

### Setup (values in `backend/.env`, never commit to git)
```
ANTIGRAVITY_CLIENT_ID=<plugin-client-id>
ANTIGRAVITY_CLIENT_SECRET=<plugin-client-secret>
ANTIGRAVITY_REFRESH=<refresh-token>
```
Saved to `backend/.env`.

### Auth Flow (Cross-Device)
1. Generate OAuth URL on Android with PKCE
2. Open URL in Windows browser
3. Google redirects to `localhost:51121/oauth-callback?code=...` (fails on Windows)
4. Copy redirect URL from address bar → paste into Android terminal
5. Script extracts code + state → exchanges for tokens
6. Refresh token reused indefinitely without re-auth

### User's Desktop OAuth Client (for custom use)
- Client ID: `<user-desktop-client-id>`
- Test user: `OsMaradny@gmail.com` added
- Note: Scopes insufficient for Antigravity API (use plugin client instead)

---

## Blocked Items
| Issue | Workaround |
|-------|-----------|
| Anthropic blocked | Use Antigravity free Claude Sonnet 4.6 + Opus 4.6 Thinking |
| OpenAI key invalid | Fresh key at https://platform.openai.com/api-keys |
| Groq removed | Not usable |
| Gemini not available (direct) | Different endpoint needed for Antigravity Gemini |
| Railway expiring | Android tunnel + Windows local backend |

---

## NTIS IMS Audit (ISO 27001 + ISO 22301)
- 2-day audit (ongoing)
- Tools: ComplianceHub doc gen, Cherry Studio agents, OpenCode
- Windows: `.\go.ps1` morning/evening
- Android: `bash go.sh` for tunnel + backend

---

## Watchdog Automation (Added June 18)

### How it works
```
crontab (every 10 min)
  └─ watchdog.sh
       ├─ Pings localhost:8000/api/health
       ├─ Checks /tmp/compliancehub-url.txt exists + non-empty
       ├─ Both OK → silent exit
       ├─ Backend down → start uvicorn → start tunnel → sync URL to git
       └─ Tunnel down → start tunnel.sh → sync URL to git
```

### Files
| File | Purpose |
|------|---------|
| `watchdog.sh` | Lightweight health check + auto-restart |
| `crontab` | 3 entries: watchdog every 10min, disk check every 30min, @reboot |

### Coverage
| Scenario | Before | After |
|----------|--------|-------|
| Phone reboot | Manual `bash go.sh` | Auto within 10 min via @reboot + cron |
| Termux killed | Manual restart | Auto within 10 min |
| Tunnel drop + go.sh down | Manual fix | Auto within 10 min |
| Backend crash during tile gap | Silent failure | Auto restarted next cycle |

### Setup (already done)
- `/usr/sbin/cron` running (PID verified)
- Crontab installed with 3 entries
- `watchdog.sh` tested — backend auto-started successfully
- Tunnel URL synced to `Osama/.tunnel-url` and git-pushed on each restart

---

## `/v1/chat/completions` — Universal OpenAI Endpoint

### Current Tunnel URL
```
https://extraordinary-october-databases-remote.trycloudflare.com
```

### Models available through tunnel
| Model ID | Type | Status |
|----------|------|--------|
| `claude-sonnet-4-6` | Sonnet 4.6 (default) | ✅ Tested |
| `claude-opus-4-6-thinking` | Opus 4.6 Thinking | ✅ Tested |
| `antigravity_claude_sonnet_46` | Antigravity direct | ✅ Available |
| `antigravity_claude_opus_46` | Antigravity direct | ✅ Available |
| Any other model | Falls through OpenRouter → Groq → Local | ✅ Auto

### Endpoint
```
POST {tunnel-url}/v1/chat/completions
```

### Models
| Model ID | Provider | Type |
|----------|----------|------|
| `claude-sonnet-4-6` | Antigravity | Tier 0 |
| `claude-opus-4-6-thinking` | Antigravity | Tier 0 (extended thinking) |
| Any other | Auto-fallback | OpenRouter → Groq → Local |

### Cherry Studio Setup (Windows)
1. Settings → Providers → Add **OpenAI**
2. Name: `Antigravity`
3. API URL: `{tunnel-url}/v1/chat/completions`
4. Model: `claude-sonnet-4-6`
5. API Key: anything (not checked)
6. Assign to 3 model slots:
   - Default: `claude-sonnet-4-6`
   - Quick: `claude-sonnet-4-6`
   - Translate: `claude-sonnet-4-6`

### OpenCode Desktop Setup (Windows)
1. Settings → Providers → Add **OpenAI-compatible**
2. Name: `Antigravity`
3. Base URL: `{tunnel-url}/v1/chat/completions`
4. Model: `claude-sonnet-4-6`
5. API Key: anything (not checked)
6. Also add OpenRouter as backup for when tunnel is down

### Notes
- Backend must be running on Android for this to work
- The backend auto-refreshes the Antigravity OAuth token
- If Antigravity fails, backend falls through to OpenRouter → Groq → Local

---

## Reference Docs
- `Osama/WINDOWS_SETUP.md` — Cherry Studio + OpenCode Desktop + go.ps1 config steps
- `Osama/AGENT_PROMPTS.md` — copy-paste system prompts for all 9 agents

## Audit Fixes (completed June 18)
All 16 identified issues fixed in commit `41b93ef`:
- **Critical:** Removed tunnel health_check_url (NAT hairpinning caused infinite restart loop)
- **Critical:** Removed git push from watchdog (crontab has no credentials)
- **High:** Wired rate limiting + health tracking to /v1/chat/completions
- **High:** Updated .env.example (Anthropic → Antigravity)
- **High:** Fixed setup-windows.ps1 (Out-Null bug, Anthropic refs)
- **High:** Deleted dead anthropic_provider.py
- **Medium:** Streaming path consistency, git stash cleanup, grep -oE portability
- **Low:** Performance recording reuse, Find-Git version sort, MODEL_NAME var

## Refactors (completed June 18)
All 4 refactors committed in `87086ab`:
1. **Router dedup** — extracted `_route()` shared function, `generate()` and `extract_structured()` are now thin wrappers (−120 lines)
2. **Chat uses resolve_chain** — `FALLBACK_CHAIN` now auto-syncs with router (14 providers)
3. **Config consolidation** — new `app/settings.py` centralizes all 21 env var reads from 11 files
4. **Streaming cleanup** — removed `generate_stream()` from AntigravityProvider (uses parent default)

## Android Agent Testing (curl commands)
Test any agent directly against localhost backend (no tunnel needed):
```bash
# Agent 1 — Gap Analysis
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-6","messages":[{"role":"system","content":"Act as Senior Lead Auditor. ISO clause-level precise. Identify findings only — no solutions."},{"role":"user","content":"Run gap analysis on ISO 27001 Annex A.5 (Information Security Policies). List all controls and their compliance status."}],"temperature":0.2,"max_tokens":4096}' | python3 -m json.tool

# Agent 2 — Implementation Doc
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-6","messages":[{"role":"system","content":"Act as Senior Lead Implementer. Complete audit-defensible docs. Client formulas non-negotiable."},{"role":"user","content":"Create ISO 27001 Information Security Policy document outline for MSD-MOI with clause references."}],"temperature":0.3,"max_tokens":4096}' | python3 -m json.tool

# Agent 5 — Arabic Output
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-sonnet-4-6","messages":[{"role":"system","content":"Act as Senior ISO Implementer and Arabic technical writer. MSA first-person practitioner voice. ISO refs in English."},{"role":"user","content":"Write an Arabic ISO 22301 Business Continuity Policy introduction for MSD-MOI."}],"temperature":0.3,"max_tokens":4096}' | python3 -m json.tool

# Test Opus thinking for complex reasoning
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-opus-4-6-thinking","messages":[{"role":"user","content":"Evaluate this risk scenario: A manufacturing plant has single generator for backup power. 8-hour fuel supply. No maintenance contract. Lead time for parts 72 hours. Score inherent and residual risk using ISO 31000 methodology."}],"temperature":0.3,"max_tokens":4096}' | python3 -m json.tool
```

## Next Steps
1. ~~Create watchdog.sh + crontab for auto-restart~~ ✅
2. ~~Test Antigravity API — Claude Sonnet 4.6 + Opus 4.6 Thinking~~ ✅
3. ~~Create antigravity_provider.py + `/v1/chat/completions` endpoint~~ ✅
4. ~~Create `backend/start.sh` (setsid, survives shell kills)~~ ✅
5. ~~Wire Antigravity accounts into OpenCode CLI plugin~~ ✅
6. ~~16 audit fixes + 4 refactors~~ ✅
7. **Configure Cherry Studio on Windows** — follow `Osama/WINDOWS_SETUP.md` + `AGENT_PROMPTS.md`
8. **Configure OpenCode Desktop on Windows** — follow `Osama/WINDOWS_SETUP.md`
9. **Start NTIS IMS audit production** — Agent 1 gap analyses, Agent 2 BCM docs, Agent 5 Arabic outputs
