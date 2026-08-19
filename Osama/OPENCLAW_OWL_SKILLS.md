# OPENCLAW_OWL_SKILLS — OpenClaw & AutoClaw Integration Map
_Last updated: 2026-08-09_

## Overview
OpenClaw is the workspace management platform that hosts the OWL v4.2 system. AutoClaw is Z.ai's automation engine for scheduled OWL workflows. This file maps both systems to OWL's numbered skills.

## OpenClaw Skill Integration Map

| OWL Skill | OpenClaw Skill | Trigger |
|-----------|---------------|---------|
| Skill 08 (Python) | openclaw:code-exec | Code generation tasks |
| Skill 15 (Prompt Transform) | openclaw:prompt-architect | Every message (Layer 0) |
| Skill 21 (Language Gate) | openclaw:language-gate | Before Skill 22 |
| Skill 22 (Quality Gates) | openclaw:quality-check | After every deliverable |
| Skill 23 (Token Compression) | openclaw:token-opt | When pressure detected |
| Skill 38 (Code Review) | openclaw:code-review | Commit gate |

## AutoClaw Automation Map

| Automation | Schedule | OWL Skills | AutoClaw Trigger |
|------------|----------|------------|------------------|
| Morning Briefing | Daily 8 AM | 01b, 10, 28 | cron: `0 8 * * *` |
| Audit Calendar Sync | Daily 9 AM | 14, 25 | cron: `0 9 * * *` |
| Quality Gate Sweep | On save | 21, 22 | file: `on_deliverable_save` |
| Template Population | On audit start | 02, 14, 25 | event: `audit_session_start` |
| Evening Digest | Daily 6 PM | 01b, 32 | cron: `0 18 * * *` |
| Weekly Reconciliation | Friday 5 PM | 22, 34 | cron: `0 17 * * 5` |
| ComplianceHub Deploy Check | On git push | 38, 17 | event: `git_push` |

**Full AutoClaw setup:** `autoclaw-projects/SETUP.md`

## File Locations in OpenClaw Workspace
- SOUL.md → Workspace root
- AGENTS.md → Workspace root
- CONTEXT.md → Workspace root
- MEMORY.md → Workspace root
- SKILLS.md → Workspace root
- PLATFORMS.md → Workspace root
- skills/ → `skills/` directory
- clients/ → `clients/` directory
- templates/ → `templates/` directory
- memory/ → `memory/` directory

## OpenClaw Configuration
- Bootstrap file: `.openclaw/workspace-state.json`
- Agent config: `.openclaw/agents/`
- Credentials: `.openclaw/credentials/` (NEVER read or expose)
- Identity: `.openclaw/identity/` (NEVER read or expose)
