# TOOLS.md — Local Notes
_See also: Context.md (clients + platform) · AGENTS.md (roles) · SKILLS.md (SOPs) · SOUL.md (identity)_

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## ComplianceHub Repo

- **Location:** `~/ComplianceHub` (cloned from https://github.com/0zMaradny/ComplianceHub)
- **Branch:** `main` (auto-pushes via post-commit hook)
- **Never commit directly to main without testing first**

## GitHub

- **Username:** `0zMaradny` (zero, not O)
- **PAT:** stored in `~/.git-credentials`
- **gh CLI:** available and authenticated

## API Keys Reference

All API keys are stored in `backend/.env`. Each key powers specific tiers of the AI router or system features.

### Quick Reference

| Key | Provider | Tier | Powers | Cost | Status | Min Length |
|-----|----------|------|--------|------|--------|------------|
| `OPENROUTER_API_KEY` | OpenRouter | 1+2 (Free) | **8 free models:** frontier (Nemotron 550B, Qwen3 Coder 480B, Kimi K2.6, Owl Alpha) + strong (Nemotron 120B, Llama 70B, Qwen3 Next 80B, Hermes 405B). Up to 1M ctx | **Free** | ✅ Valid | Any non-empty |
| `GROQ_API_KEY` | Groq | 3 (Fastest) | Llama 3.3 70B Versatile (~800 t/s), 131K ctx | **Free** | ✅ Valid | Any non-empty |
| `HF_API_KEY` | HuggingFace | Fallback | Meta-Llama-3-8B-Instruct (overridable via `HF_MODEL` env) | **Free** | ✅ Valid | Any non-empty |
| `ANTHROPIC_API_KEY` | Anthropic | 0 (Premium) | Claude Sonnet 4 (200K ctx, best quality) | **Paid** | ⚠️ Truncated (61 chars, needs ≥100) — auto-skipped | ≥ 100 chars |
| GitHub PAT | GitHub | — | `git push` via post-commit hook (`~/.git-credentials`) | **Free** | ✅ Valid | — |

### Per-Key Detail

#### `OPENROUTER_API_KEY` — Primary Free Cloud Tier

| Field | Detail |
|-------|--------|
| **Prefix** | `sk-or-v1-` |
| **File(s)** | `app/services/ai/openrouter_provider.py:27` — reads from env |
| **Router** | `app/services/ai/router.py:176` — injected via `set_api_key()` |
| **Models** | 8 free: Nemotron Ultra 550B, Qwen3 Coder 480B, Kimi K2.6, Owl Alpha, Nemotron Super 120B, Llama 3.3 70B, Qwen3 Next 80B, Hermes 405B |
| **Parallel** | Batch size 2 per tier (configurable via `AI_BATCH_SIZE`) |
| **Peak hours** | Weekdays 12–18 UTC — low-priority tasks skip OpenRouter |
| **Rate limit** | 30 req/min per provider |
| **Degrade** | 3 consecutive failures → provider skipped |
| **Absent** | Tiers 1+2 skipped, falls through to Groq |
| **Get key** | https://openrouter.ai/keys |

#### `GROQ_API_KEY` — Fastest Free Backup

| Field | Detail |
|-------|--------|
| **Prefix** | `gsk_` |
| **File(s)** | `app/services/ai/groq_provider.py:12` — reads from env |
| **Router** | `app/services/ai/router.py:180` — injected via `set_api_key()` |
| **Models** | Llama 3.3 70B Versatile (~800 t/s inference) |
| **Context** | 131K tokens |
| **Rate limit** | 30 req/min |
| **Absent** | Tier 3 skipped, falls through to local/offline |
| **Get key** | https://console.groq.com/keys |

#### `HF_API_KEY` — Optional HuggingFace Fallback

| Field | Detail |
|-------|--------|
| **Prefix** | `hf_` |
| **File(s)** | `app/services/ai/hf_provider.py` |
| **Models** | Default: `meta-llama/Meta-Llama-3-8B-Instruct` (override via `HF_MODEL`) |
| **Cooldown** | 402/429/503 → exponential backoff: 60s → 120s → 300s → 600s |
| **Rate limit** | 10 req/min, 0.8s minimum inter-request gap |
| **Setup** | Must enable Inference Providers at https://huggingface.co/settings/inference-providers |
| **Absent** | Skipped — no fallback impact |
| **Get key** | https://huggingface.co/settings/tokens |

#### `ANTHROPIC_API_KEY` — Premium Tier (Currently Skipped)

| Field | Detail |
|-------|--------|
| **Prefix** | `sk-ant-api` |
| **File(s)** | `app/services/ai/anthropic_provider.py:15` — reads from env |
| **Router** | `app/services/ai/router.py:182` — injected via `set_api_key()` |
| **Models** | Claude Sonnet 4 (`claude-sonnet-4-20250514`) |
| **Context** | 200K tokens |
| **Length check** | `app/services/ai/router.py:233-235` — requires ≥ 100 chars or skipped |
| **Status** | Current key is 61 chars — fast-fails in 0.0s instead of ~8s timeout |
| **Rate limit** | 50 req/min |
| **Absent/short** | Tier 0 skipped, falls through to OpenRouter free tiers |
| **Get key** | https://console.anthropic.com/ |

#### GitHub PAT — Auto-Push

| Field | Detail |
|-------|--------|
| **Location** | `~/.git-credentials` |
| **Purpose** | `git push` via `.git/hooks/post-commit` — auto-pushes every commit on `main` |
| **Scope** | Repo access to `github.com/0zMaradny/ComplianceHub` |

### No-Key Tiers

| Tier | Provider | How to Enable |
|------|----------|---------------|
| **4 — Local AI** | `llama-server` (localhost:8080) | `bash run.sh --local-ai` or start manually: `/opt/llama-server/llama-server -m /opt/llama-server/models/qwen3-4b.gguf -c 32768 -t 4 -b 2048 --mlock --port 8080` |
| **Offline** | Static template generator | Leave all API keys empty — instant generation, no AI needed (3.2s/8 docs) |

### Where to Configure

| Environment | File / Location |
|-------------|-----------------|
| **Local dev** | `backend/.env` — 4 keys already populated |
| **Railway deploy** | Dashboard → Variables tab — auto-injected as env vars |
| **Reference** | `backend/.env.example` — documents all 20+ configurable vars |

### Related Env Vars (beyond keys)

| Var | Default | Purpose |
|-----|---------|---------|
| `AI_CACHE_TTL` | 3600 | Response cache TTL (seconds) |
| `AI_DEGRADE_THRESHOLD` | 3 | Consecutive failures before skipping a provider |
| `AI_BATCH_SIZE` | 2 | Parallel model calls per tier |
| `AI_PEAK_START` / `AI_PEAK_END` | 12 / 18 | OpenRouter peak hours (UTC) |
| `LOCAL_AI_BASE` | http://localhost:8080 | Local llama-server URL |
| `LOCAL_AI_TIMEOUT` | 120 | Local AI request timeout (seconds) |
| `HF_MODEL` | meta-llama/Meta-Llama-3-8B-Instruct | HuggingFace model override |
| `TUNNEL_SECRET` | — | Secret for tunnel URL updates |

## Local AI (llama.cpp)

- **Binary:** `/opt/llama-server/llama-server`
- **Models directory:** `~/ComplianceHub/backend/models/`
- **Available models (ordered best-first):**
  - `qwen3-4b.gguf` (~2.5 GB, Q4_K_M) — **primary** ~40s/doc, 32K ctx, best local quality
  - `qwen-3b.gguf` (~2.1 GB, Q4_K_M) — fallback ~60s/doc, 8K ctx
  - `qwen-0.5b.gguf` (~469 MB, Q4_K_M) — minimal ~20s/doc, 4K ctx, lowest quality
- **ARM64 flags:** `-t 4 -b 2048 --mlock --cache-type-k q8_0 --cache-type-v q8_0`
- **Port:** 8080

## TÜV Austria

- **Employer:** TÜV Austria GCC (Feb 2023–present)
- **Role:** Scheme Head — ISMS / ITSMS / BCMS
- **Branding:** TUV_BLUE #003D7A · TUV_RED #C00000
- **Logo:** `backend/static/tuv_logo.png`

## Client Doc Code Prefixes

| Client | Prefix |
|--------|--------|
| MSD-MOI | `MSD-MOI-GRC-` |
| UACC | `UACC-EnMS-` |
| SAGCO | SAGCO-IMS- |
| MOC | MOC-ABMS- |
| Al-Ahsa Municipality | AHSA-ISMS- |

## SAGCO Dashboard

- **URL:** https://sagcodrv-ux.github.io/sagco-im/
- **Data backend:** Google Sheets → Apps Script Web App → static site
- **API:** `https://script.google.com/macros/s/AKfycbweju9C4Xow2mJ95Y_namTbj8Zsll-faZv2vuL_vAwzcJ0xfmymXz88_vJanfCuXaM/exec?tab=TABNAME&action=read`
- **Available data tabs (60+):** risks, compliance, objectives, context, pestle, moc, energy, hira, sea, bribery_risk, ghg_inventory, training, ptw_register, emergency, fire_ext, capa, incidents, and many more
- **Domain vocabulary:** SHC, EnB, EnPI, SEU, SPC, GHG, HFO, LPG, HIRA, PTW, MOC, ECM, SEET
- **Risk formula:** L × S (5×5 matrix, confirmed via WI-RA-01)
- **Doc codes:** L4-430-RC-01, L4-IMS-410-WI-04, SAGCO-IMS-CKL-001, SAGCO-IMS-WI-RA-01
- **IMS Champion** = system owner for all SAGCO IMS documentation
## Excel Defaults

- **Engine:** openpyxl (never xlsxwriter, never VBA)
- **Calculations:** Live Excel formulas only — never hardcoded Python values
- **Hidden sheets:** `_Lists` or `_Data` for all dropdown sources
- **Print:** A4, rows_to_repeat on row 1, freeze panes
- **Recalc:** Run `scripts/recalc.py` after every formula build — zero errors mandatory

## Word / Arabic Defaults

- **Engine:** python-docx
- **Arabic:** WD_ALIGN_PARAGRAPH.RIGHT + explicit bidi run property
- **Voice:** ﻗﻤﻨﺎ ﺑـ / ﺗﻢ ﺗﻄﺒﻴﻖ — first-person practitioner, active voice
- **ISO refs + Risk IDs:** Always in English, even in Arabic documents

## Python Defaults

- **Style:** Modular scripts, `# --- CONFIG ---` block at top
- **Quality:** `python -m compileall . -q` + `python -m pyflakes app/` — zero errors
- **Deployment:** Locally deployable, no cloud dependency

## React / Frontend Defaults

- **Build:** Vite (`npm run build`)
- **Lint:** ESLint (`npm run lint`)
- **Dev server:** `npm run dev` (port 5173)

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
