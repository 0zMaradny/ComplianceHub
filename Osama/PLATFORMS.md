# PLATFORMS.md — Loading Profiles
_See also: CHERRY_STUDIO_ASSISTANTS.md (9-assistant mapping) · AGENTS.md (roles) · Context.md (clients + platform) · MEMORY.md (preferences)_

Osama's actual platform ecosystem as of June 2026. Different tools need different slices of the Osama/ files. Load the right profile for each platform.

## opencode (AnyClaud, AI coding partner)

**Model:** Claude
**Role:** Primary development + system work interface
**Load:** Fully — SOUL.md + USER.md + AGENTS.md + SKILLS.md + Context.md + MEMORY.md
**On demand:** TOOLS.md when platform/repo work
**Strip before loading:** Nothing — Claude handles ~22K full context easily

## OpenClaw Gateway (AnyClaud)

**Model:** Claude
**Role:** Session initialization — loads core identity + context
**Load:** SOUL.md + USER.md + Context.md (client entries, platform, standards)
**On demand:** AGENTS.md + SKILLS.md when task requires specific agent
**Note:** Gateway passes through to opencode for full sessions

## Claude (standalone, free tier)

**Model:** Claude Sonnet 4
**Role:** Ad-hoc research, writing, analysis outside repo
**Load:** Same as opencode — SOUL.md + USER.md + AGENTS.md + SKILLS.md + Context.md + MEMORY.md
**On demand:** TOOLS.md

## ComplianceHub Web UI

**Model:** Backend AI pipeline (5-tier: OpenRouter frontier → strong → Groq → local Qwen)
**Role:** Audit document generation (8 doc types, 14 standards)
**Load:** None directly — backend uses its own SYSTEM_PROMPT + per-doc-type prompts
**Osama/ files reference:** Context.md is the source for writing/updating prompts in ai_pipeline.py
**Note:** This is the deliverable tool, not an AI assistant interface

## Cherry Studio (Android + Windows)

**Model:** Configurable (user picks provider per assistant)
**Role:** Daily AI tasks — 9 assistants mapped from AGENTS.md
**Load per assistant:** [Relevant agent role from AGENTS.md] + [Context.md client entries] + [SKILLS.md relevant skill] + [MEMORY.md corrections + preferences]
**Token budget:** Depends on provider — ~8K for local, up to 200K for cloud
**Setup:** 9 assistants created per CHERRY_STUDIO_ASSISTANTS.md mapping

## Qwen Studio App (phone)

**Model:** Qwen (on-device)
**Role:** Quick tasks, offline queries
**Load:** Minimal — per-task snippet only: [client entry from Context.md] + [skill paragraph from SKILLS.md] + [task instruction]
**Token budget:** ~4K — full files will overflow

## DeepSeek App (phone)

**Model:** DeepSeek
**Role:** Quick tasks, offline queries, research
**Load:** Minimal — per-task snippet only, similar to Qwen Studio
**Token budget:** ~4K–8K

## Google Gemini Pro (pro account)

**Model:** Gemini Pro
**Role:** Research, analysis, one-off queries
**Load:** USER.md + Context.md (client sections only) + MEMORY.md (corrections + preference summaries)
**Strip before loading:** PUSH instruction (Gemini ignores it) · artifact sandbox rules · React-specific content · memory_user_edits references
**Token budget:** 128K — fine but wasteful to load full set

## Google AI Edge Gallery (Android, freshly installed)

**Model:** Edge-optimized models (on-device)
**Role:** On-device AI experiments, lightweight tasks
**Load:** Minimal — single paragraph task description + 1–2 client facts
**Token budget:** ~2K — edge models have very small context windows
**Note:** New platform — profile will evolve after experimentation

## NotebookLM (Pro account)

**Model:** Google NotebookLM
**Role:** Research synthesis, source analysis, document summarization
**Load as sources:** USER.md + Context.md (client sections, standards, platform) + MEMORY.md (wins + preferences) + relevant ISO PDFs
**Note:** NotebookLM doesn't follow instructions — it synthesizes sources. Use Context.md client entries as domain knowledge injection, not as system prompts.

## Logseq

**Model:** None (markdown-based knowledge management)
**Role:** Daily journaling, client notes, standards references, compounding knowledge
**Load:** None — files are stored as pages at /root/Documents/Logseq/pages/
**Sync:** Google Drive across Android + Windows
**Relationship:** Logseq pages are written by Osama and Cherry Studio — they reference Osama/ files but don't load them

## Local Qwen3-4B (llama-server, ComplianceHub backend fallback)

**Model:** Qwen3-4B GGUF (Q4_K_M, ~2.5 GB)
**Role:** Offline AI generation when cloud unavailable
**Load:** Task-specific snippets only — [client entry from Context.md] + [relevant skill paragraph from SKILLS.md] + [task instruction]
**Token budget:** 32K but generation is slow (~40s/doc) — keep prompts lean
**Note:** This is the backend Tier 4 fallback, not an interactive assistant

## Platform Compatibility Quick Reference

| Platform | Load Strategy | Token Budget | Claude Features That Break |
|----------|--------------|-------------|---------------------------|
| opencode (Claude) | Full | 200K | None — native |
| OpenClaw Gateway (Claude) | Core 3 files | ~8K | None |
| Claude standalone | Full | 200K | None |
| ComplianceHub UI | Backend pipeline | N/A | N/A — different system |
| Cherry Studio | Per-agent snippet | Varies | PUSH ignored on non-Claude |
| Qwen Studio | Per-task snippet | ~4K | PUSH · extended thinking · tool calls |
| DeepSeek | Per-task snippet | ~4K–8K | PUSH · tool calls |
| Gemini Pro | Stripped | 128K | PUSH · memory_user_edits · artifacts |
| AI Edge Gallery | Minimal | ~2K | Everything stripped |
| NotebookLM | Source only | N/A | Instructions ignored entirely |
| Logseq | None — stored pages | N/A | N/A |
| Local Qwen3-4B | Per-task snippet | 32K | PUSH · extended thinking · tools |
