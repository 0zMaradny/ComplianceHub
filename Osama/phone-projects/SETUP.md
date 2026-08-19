# Phone Setup Guide — OWL v4.0

## Apps to Install

| App | Use Case | Platform |
|-----|----------|----------|
| **Qwen** | Primary — general, documents, vibe coding | Android |
| **Z.ai** | Agents, coding, reasoning | Android |
| **Gemini** | Deep Research, Gems, general | Android |
| **DeepSeek** | Confirmation of outputs, reasoning | Android |
| **Claude** | Client-sensitive data only | Android |
| **Xiaomi MiMo** | General, OWL tasks | Android |

---

## App-by-App Setup

### Qwen (Primary Phone App)
- Login with same account as Qwen Studio
- Same 4 Projects available on phone
- Use for: quick deliverable questions, Arabic docs, research
- **Budget:** ~4K–8K tokens per message

### Z.ai
- Login with same account
- Same OWL agent available
- Use for: reasoning tasks, CAPA, stress-test
- **Budget:** ~4K–8K tokens

### Gemini
- Login with company Google account
- Same 5 Gems available
- Use for: Deep Research, regulatory queries, quick audit questions
- Voice-to-research: dictate questions on-site
- **Budget:** Unlimited (company-paid)

### DeepSeek
- Free app
- Use for: confirming outputs from other platforms, reasoning
- Good for: second opinion on audit findings
- **Budget:** Daily limits

### Claude
- Use for: client-sensitive data (MSD-MOI, Al-Ahsa)
- Only app safe for HIGH sensitivity data on phone
- Use for: reviewing client documents, named-employee findings
- **Budget:** Daily limits

### MiMo
- Free app
- Use for: general queries, OWL-related tasks
- **Budget:** 4hr/day free

---

## Phone Workflow

### On-Site (Audit/Client Visit)
1. **Gemini** → Deep Research on the standard (voice-to-research)
2. **Claude** → Review client-sensitive documents
3. **Hermes (Telegram)** → Quick queries ("What's the SAGCO formula?")

### Commuting
1. **Gemini** → Deep Research on regulatory updates
2. **Qwen** → Draft documents in Projects
3. **Z.ai** → Reasoning tasks

### Quick Queries
1. **Hermes (Telegram)** → Fastest for OWL queries
2. **Gemini** → If research needed
3. **Qwen** → If deliverable context needed

### Client-Sensitive Work
1. **Claude ONLY** → Named employees, participation lists, PDPL data
2. Never use Qwen/Z.ai/Gemini/MiniMax for HIGH sensitivity

---

## Compressed Pastes for Phone

Phone context is limited (~4K–8K tokens). Paste only:

### For Client Work
```
Client: [name]
Standard: [ISO standard]
Formula: [from CONTEXT.md]
Task: [what you need]
```

### For Audit Work
```
Standard: [ISO standard]
Audit type: [Stage 1/2/Survival]
Client: [name]
Focus: [specific clause or area]
```

### For KSA Work
```
Framework: [NCA ECC/SAMA/PDPL/DGA/SDAIA]
Client: [name]
Question: [specific question]
```

### For Implementation
```
Client: [name]
Document type: [policy/procedure/risk register/etc.]
Standard: [ISO standard]
Language: [English/Arabic]
```

---

## Phone Context Budget

| Platform | Context | Compressed Load | Free for Work |
|----------|---------|-----------------|---------------|
| Qwen | 1M | ~2K | ~998K |
| Z.ai | 128K–1M | ~2K | ~126K–998K |
| Gemini | 1M+ | ~2K | ~998K+ |
| DeepSeek | 128K | ~2K | ~126K |
| Claude | 200K | ~2K | ~198K |
| MiMo | Varies | ~2K | Varies |
| Phone total | ~4K–8K | ~2K | ~2K–6K |

---

## caveman on Phone

Use caveman ultra from message 1 on all phone apps:
- Say "caveman ultra" or just start with compressed context
- Never modify: code blocks, formulas, clause refs, doc codes
- Saves ~50% tokens per message

---

## Privacy Matrix (Phone)

| Client | Qwen | Z.ai | Gemini | DeepSeek | Claude | MiMo |
|--------|------|------|--------|----------|--------|------|
| MSD-MOI (HIGH) | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Al-Ahsa (HIGH) | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| SAGCO (MEDIUM) | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ | ✅ scrub |
| UACC (MEDIUM) | ✅ scrub | ✅ scrub | ✅ scrub | ✅ scrub | ✅ | ✅ scrub |
| Audit (LOW) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OWL internal | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Scrub:** Remove names, phones, emails, NIDs, addresses before pasting.

---

## Daily Phone Workflow

### Morning (8 AM)
- Hermes Telegram: morning briefing (auto)

### On-Site
- Gemini: voice-to-research
- Claude: client-sensitive review
- Hermes: quick queries

### Commuting
- Gemini: Deep Research
- Qwen: draft in Projects
- Z.ai: reasoning tasks

### Evening (6 PM)
- Hermes Telegram: evening digest (auto)
