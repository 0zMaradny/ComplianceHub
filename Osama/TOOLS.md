# TOOLS.md — Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## ComplianceHub Repo

- **Location:** `~/ComplianceHub` (cloned from https://github.com/0zMaradny/ComplianceHub)
- **Branch:** `main` (auto-pushes via post-commit hook)
- **Never commit directly to main without testing first**

## GitHub

- **Username:** `0zMaradny` (zero, not O)
- **PAT:** stored in `~/.git-credentials`
- **gh CLI:** available and authenticated

## Local AI (llama.cpp)

- **Binary:** `/opt/llama-server/llama-server`
- **Models directory:** `~/ComplianceHub/backend/models/`
- **Available models:**
  - `qwen-0.5b.gguf` (~469 MB, Q4_K_M) — fast, lower quality
  - `qwen-1.5b.gguf` (~941 MB, Q4_K_M) — better quality
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
| SAGCO | TBD |
| Al-Ahsa Municipality | TBD |

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
