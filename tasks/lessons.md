# OWL — Lessons (correction log)

One line per correction: pattern → fix. Read at session start. Newest first.

## 2026-08-16
- Tool-call failures (repeated): messages with prose + markdown backticks/tables/fences around a tool → parser corrupts/empties the command. FIX: a tool call is the entire message; no text beside it; short single-line args; no backticks/fences/tables; write logic to a .py then `python file.py`.
- `replace_in_file` kept failing with "diff parameter was empty" when prose + XML collided. FIX: use lean-ctx `ctx_patch(op=replace_unique)` or `write_to_file` for whole-file safety. Also: files may use CRLF or LF — match old_text exactly (verify with ctx_read raw).
- Groq tier was silently dead: `_provider_has_key` only checked legacy key `'groq'`, registry uses `groq_llama`/`groq_scout`. FIX: added the two registry keys to the same key check. Pattern: registry keys and hardcoded checks must stay in sync — grep for the literal after any registry change.
- `test_chat_endpoint.py` expected `/v1/models` + `MODELS_LIST` that didn't exist, and referenced retired models (claude-opus-4-6-thinking, kimi-k26, 12 models). FIX: made chat.py registry-driven (MODELS_LIST/MODEL_MAP auto-built, `/v1/models` GET added) and updated tests to registry reality (24 models incl auto). Pattern: after any registry change, update chat endpoint + its tests together; run test_chat_endpoint.
- model_bench.py had a broken dict-ternary and only benched openrouter models. FIX: rewrote cleanly to run all 21. Pattern: keep scripts runnable by hand; `python -m scripts.model_bench` should work.
- Sessions must record outcomes to tasks/todo.md + lessons here at close — done this session.

## Pending lessons bucket
- After every correction: add one line here.