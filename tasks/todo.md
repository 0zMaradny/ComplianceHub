# OWL Task Board

## Phase A — Engine verification (✅ done)
- [x] Fix model_bench.py (all 21 models, correct output) — commit 6671cc4 range
- [x] Fix Groq key detection in router._provider_has_key (groq_llama/groq_scout) — verified
- [x] Add registry-driven /v1/models endpoint + MODELS_LIST to chat.py
- [x] Update test_chat_endpoint.py stale asserts (kimi-k3, claude-sonnet-5, count 24)
- [x] Full AI test suite green: 84 passed (router 46 + providers + chat)
- [x] compileall clean
- [x] Committed: e832672 "fix(ai): Groq key detection + registry-driven /v1/models; 84/84 AI tests green"

## Phase B — Agent harness + second brain
- [x] HARNESS.md written (portable bootstrap, 33 Cherny rules fused in workflow + memory table)
- [x] tasks/todo.md (this file)
- [ ] tasks/lessons.md created (correction log)
- [ ] Commit Phase B

## Phase C — Bigger version (pending, next session)
- [ ] Registry-as-data (model_registry.json, not code)
- [ ] Startup health-check vs OpenRouter /models (delete dead IDs)
- [ ] Per-task model preference from model_performance.json history
- [ ] Streaming quality gate (placeholder validation on streamed text)
- [ ] Perf dashboard endpoint (/api/models/health)
- [ ] Sync AGENTS.md to the 21-model reality

## Review
- Phase A verified locally (84 tests) + pushed to origin/main.
- Groq key bug was silently killing Tier 3 for whoever set GROQ_API_KEY. Now fixed.
- Live bench without keys correctly 401'd every provider — proving the chain enumerates all tiers.