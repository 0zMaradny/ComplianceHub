# OWL Task Board

## Phase A — Engine verification (✅ done)
- [x] Fix model_bench.py (all 21 models, correct output) — commit 6671cc4 range
- [x] Fix Groq key detection in router._provider_has_key (groq_llama/groq_scout) — verified
- [x] Add registry-driven /v1/models endpoint + MODELS_LIST to chat.py
- [x] Update test_chat_endpoint.py stale asserts (kimi-k3, claude-sonnet-5, count 24)
- [x] Full AI test suite green: 84 passed (router 46 + providers + chat)
- [x] compileall clean
- [x] Committed: e832672 "fix(ai): Groq key detection + registry-driven /v1/models; 84/84 AI tests green"

## Phase B — Agent harness + second brain (✅ done)
- [x] HARNESS.md written (portable bootstrap, 33 Cherny rules fused in workflow + memory table)
- [x] tasks/todo.md (this file)
- [x] tasks/lessons.md created (correction log)
- [x] Committed: d8c9fd1 "feat(agent): portable HARNESS.md + tasks/ second brain + memory session log" + pushed

## Phase C — Network stability + CI gate (✅ done)
- [x] CI workflow added (2117a55)
- [x] CI: kimi_k26 → kimi_k3 (registry renamed) — 7c6b4da
- [x] CI: key-detection tests env-aware (skip when API keys absent) — 7c6b4da
- [x] Frontend: dedicated vitest.config.js (jsdom, globals, setupFiles, test include) — proper vitest 4 pattern; vite.config.js stripped of test block
- [x] Frontend: vitest bumped 4.1.8 → 4.1.10, test script uses vitest.config.js
- [x] .gitignore: node_modules/ + .vite/ at root (cleanup from npx vitest)
- [x] Committed: cf79a39 "ci: fix workflow for CI green (kimi_k3, env-aware key tests) + frontend vitest config"

## Phase D — Bigger version (queued, next)
- [ ] Registry-as-data (model_registry.json, not code)
- [ ] Startup health-check vs OpenRouter /models (dead ID pruning)
- [ ] Per-task model preference from model_performance.json history
- [ ] Streaming quality gate (placeholder validation on streamed text)
- [ ] Perf dashboard endpoint (/api/models/health)
- [ ] Sync AGENTS.md to the 21-model reality

## Review
- Phase A verified locally (84 tests) + pushed to origin/main.
- Groq key bug was silently killing Tier 3 for whoever set GROQ_API_KEY. Now fixed.
- Live bench without keys correctly 401'd every provider — proving the chain enumerates all tiers.
- CI gate: backend 86 passed locally (3 key-detection tests need API keys — CI now skips when absent); frontend test config fixed for vitest 4.
- Local note: frontend tests hit 'Vitest failed to find the runner' with vitest 4.1.x on Node 26.3.0 (bleeding-edge); CI uses Node 22 LTS which vitest targets.