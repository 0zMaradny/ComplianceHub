# Hermes Agent Setup Guide — OWL v4.0 (Consolidated)

## Platform Info
- **Type:** Self-hosted desktop application (Windows, via WSL2 or native)
- **Model:** OpenRouter (configurable)
- **Channels:** Telegram + WhatsApp
- **Memory:** Persistent (imports files once, remembers forever)
- **Automations:** 4 cron jobs (consolidated from 7)

---

## Step 1: Install

### Option A: Windows Installer (Recommended)
1. Download from **hermes-agent.org** → Windows installer
2. Run installer → follow wizard
3. Launch Hermes Agent from Start Menu

### Option B: WSL2
```powershell
wsl --install
# Inside WSL:
curl -fsSL https://hermes-agent.org/install.sh | bash
```

---

## Step 2: Configure LLM

In Hermes Agent settings:
- Provider: **OpenRouter**
- API Key: Your `OPENROUTER_API_KEY`
- Model: Start with `nvidia/nemotron-ultra-253b` (free)

### Model Options (Best → Budget)
| Model | Quality | Speed | Cost | When to Use |
|-------|---------|-------|------|-------------|
| deepseek/deepseek-chat-v3-0324 | Excellent | Fast | Cheap | Best quality, worth paying |
| qwen/qwen3-235b-a22b:free | Excellent | Slower | Free | Complex queries, free |
| nvidia/nemotron-ultra-253b | Good | Medium | Free | Default daily use |
| google/gemma-3-27b-it:free | Good | Fast | Free | Quick queries, fallback |

---

## Step 3: Load OWL Context (Full Load)

```powershell
# Core
hermes memory import SOUL.md
hermes memory import CONTEXT.md
hermes memory import AGENTS.md
hermes memory import MEMORY.md
hermes memory import SKILLS.md

# Client profiles
hermes memory import clients/MSD-MOI.md
hermes memory import clients/SAGCO.md
hermes memory import clients/AL-AHSA.md
hermes memory import clients/KSA-REGULATORY.md

# Skill domain files
hermes memory import skills/AUDIT.md
hermes memory import skills/IMPLEMENT.md
hermes memory import skills/DEV.md
hermes memory import skills/SYSTEM.md
hermes memory import skills/humanizer/SKILL.md
```

---

## Step 4: Connect Telegram

1. Message @BotFather on Telegram → `/newbot` → get token
2. In Hermes: Settings → Channels → Telegram → paste token
3. Enable Telegram channel
4. Test: send "What's the SAGCO risk formula?" to your bot

---

## Step 5: Connect WhatsApp (Optional)

1. In Hermes: Settings → Channels → WhatsApp
2. Scan QR code with your WhatsApp
3. Test: send a message to the connected number

---

## Step 6: Set Up 4 Automations (Consolidated)

In Hermes Agent → Automations → New:

### 1. Morning Briefing (8 AM daily)
```
Good morning. Check and report:
1. Pending client deliverables (from CONTEXT.md)
2. Upcoming audit dates (next 7 days)
3. Overdue CAPA items
4. Any urgent items from yesterday's memory file
5. Today's calendar (if accessible)
Format: 5 bullet points, direct, no filler.
```

### 2. Evening Digest + Sync (6 PM daily)
```
End of day report:
1. Git log — what was committed today
2. memory/YYYY-MM-DD.md — what was planned vs done
3. Decisions made that need logging
4. Files changed that need syncing
5. Pending items for tomorrow
If nothing committed, remind to save work.
Did you sync files to Google Drive? Did you update memory file?
```

### 3. Weekly Reconciliation (Friday 5 PM)
```
Weekly review:
1. Git log — this week's commits
2. Deliverables produced vs planned
3. Client status changes
4. Open items for next week
5. Any missed automations or overdue items
Summary in 10 bullet points max.
```

### 4. Monthly KSA Regulatory + Audit Calendar (1st of month, 9 AM)
```
Monthly check:
1. KSA regulatory updates:
   - NCA ECC — new controls or guidance?
   - SAMA CSF — circulars or updates?
   - PDPL — enforcement actions or clarifications?
   - DGA Qiyas — version changes?
   - SDAIA — new AI ethics guidance?
2. This month's audit calendar:
   - Upcoming audits from CONTEXT.md
   - Pre-audit research needed?
   - Documents not yet delivered?
   - Manday calculations done?
Flag anything affecting active clients.
```

---

## Step 7: Use Cases

### Quick Questions (Telegram)
- "What's the SAGCO risk formula?" → L×S
- "What NCA ECC controls map to ISO 27001 A.5.24?" → Cross-reference
- "What's the status of Al-Ahsa CAPA items?" → Check MEMORY.md
- "What does PDPL Art.20 require?" → 72hr breach notify
- "Draft a CAPA root cause for [NC]" → 5-Whys analysis

### Client Status
- "MSD-MOI status" → pending deliverables, audit dates
- "SAGCO blockers" → Stage 2 blockers list
- "Al-Ahsa open items" → CAPA items, documents

### Implementation Guidance
- "How do I build a BIA workbook?" → From skills/IMPLEMENT.md
- "What's the CAPA order?" → Root Cause → Containment → Corrective → Preventive → Effectiveness
- "What documents are in ISO 42001 AIMS?" → 24 mandatory docs

### KSA Compliance
- "PDPL data subject rights?" → Art.12
- "NCA ECC domains?" → 5 domains, 114 controls
- "DGA maturity model?" → 8 dimensions, 5 levels

### Arabic Support
- "Translate 'Risk Level' to Arabic" → مستوى المخاطر
- "How to say 'Corrective Action' in Arabic" → إجراء تصحيحي

### Draft Generation
- "Draft a brief audit finding for [NC]" → Basic draft (refine in Qwen/Gemini)
- "Draft a CAPA response for [issue]" → Structure + content

---

## Step 8: Telegram Bot Commands (Optional)

Set up with @BotFather:
```
/setcommands
ask - Quick OWL query
client - Client status
audit - Audit prep
formula - Risk formula
ksa - KSA compliance
```

---

## Privacy
- Self-hosted = all data stays local
- Safe for HIGH sensitivity clients (MSD-MOI, Al-Ahsa)
- No external routing needed
