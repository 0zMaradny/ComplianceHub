# PLATFORMS.md — Platform Configurations & Privacy Rules
_Last updated: 2026-08-08_

## Platform Overview

| Platform | Model | Role | Context | Status |
|----------|-------|------|---------|--------|
| Qwen Studio | Qwen 3.8 Max | Primary deliverables | 1M | ✅ Active |
| VS Code + Cline | DeepSeek Flash V4 | Terminal coding | Full | ✅ Active |
| Z.ai Agent | GLM-5.2 | Reasoning + agents (full OWL) | 128K–1M | ✅ Active |
| Z.ai Chat | GLM-5.2 | Quick Q&A (light OWL) | 128K–1M | ✅ Active |
| AutoClaw | Z.ai engine | Automated workflows | Persistent | ✅ Active |
| Gemini Pro | Pro 3.1 / Flash 3.5 / Thinking 3.6 | Research + synthesis | 1M+ | ✅ Active (company-paid) |
| Hermes | OpenRouter (various) | Always-on + automations | Persistent | ⏳ Setup pending |
| Phone (6 apps) | Various | Mobile access | ~4K–8K | ⏳ Install pending |
| MiniMax | MiniMax | Free quick queries | Limited | ✅ Available |
| MiMo | MiMo-V2.5-Pro | OWL-internal tasks | Limited | ✅ Available |
| Qwen Coder | Qwen Coder | Free coding | Limited | ✅ Available |

## Privacy Rules

### Client Sensitivity Classification (Projects vs Audit Clients)
| Client | Category | Sensitivity | Reason |
|--------|----------|------------|--------|
| MSD-MOI | Project | HIGH | KSA government data, NDA required |
| Al-Ahsa | Project | HIGH | KSA government data, NDA required |
| SAGCO | Project | MEDIUM | Corporate, scrub OK on non-Claude providers |
| Audit clients | Audit Client | Varies | Classify per client: HIGH if gov, MEDIUM if industrial |
| UACC | Archived | MEDIUM | Finished · EnMS vocabulary locked |

### Platform Access Matrix
| Platform | HIGH Clients | MEDIUM Clients | LOW Clients |
|----------|-------------|----------------|-------------|
| Qwen | ❌ BLOCKED | ✅ PII scrub | ✅ |
| Gemini | ❌ BLOCKED | ✅ PII scrub | ✅ |
| Z.ai Agent | ❌ BLOCKED | ✅ PII scrub | ✅ |
| Z.ai Chat | ❌ BLOCKED | ✅ PII scrub | ✅ |
| AutoClaw | ❌ BLOCKED | ✅ PII scrub | ✅ |
| Cline (local) | ✅ Local only | ✅ | ✅ |
| Claude (phone) | ✅ | ✅ | ✅ |
| Hermes (self-hosted) | ✅ Self-hosted | ✅ | ✅ |
| MiniMax/MiMo | ❌ BLOCKED | ⚠️ Scrub carefully | ✅ |

### PII Scrub Rules
- Names → [EMPLOYEE-001]
- Phones → [PHONE-REDACTED]
- Emails → [EMAIL-REDACTED]
- NIDs → [NID-REDACTED]
- Addresses → [ADDRESS-REDACTED]
- Never scrub: ISO clauses, formulas, doc codes, technical terms

## Platform Strip Rules
- **Qwen:** Strip "Work through this step by step"
- **Z.ai Agent:** Use native reasoning. Strip PUSH. Full OWL load via knowledge files.
- **Z.ai Chat:** Use native reasoning. Strip PUSH. Light load — SOUL summary + client row only.
- **AutoClaw:** Native reasoning. Full OWL load. Scheduled triggers. Never manual invocation.
- **Gemini:** Strip "Work through this step by step"
- **MiniMax/MiMo:** Strip PUSH only
- **Phone:** Strip PUSH + drop reasoning line

## Rate Limits (Approximate)
| Platform | Limit | Strategy |
|----------|-------|----------|
| Qwen Studio | ~100 msg/day (free) | Projects for context isolation |
| Gemini Pro | Unlimited (company-paid) | Maximize for research |
| Z.ai Agent | ~60 turns (desktop), 40 (phone) | caveman at limit · full OWL load |
| Z.ai Chat | ~60 turns (desktop), 40 (phone) | Light load · quick Q&A |
| AutoClaw | Unlimited (cron-driven) | Scheduled automations · see autoclaw-projects/SETUP.md |
| Cline | Depends on API key | Free fallback models |
| Hermes | Depends on OpenRouter | 50 req/day free tier |
