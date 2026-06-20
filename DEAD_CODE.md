# Dead Code Registry

## Removed

| File | What | Why | Date |
|------|------|-----|------|
| `backend/app/services/ai/__init__.py` | `gemma_31b` provider factory entry | Google Gemma model — not in model_registry, never used in fallback chain | 2026-06-19 |
| `backend/app/services/ai/rate_limiter.py` | `gemma_31b: 20` rate limit entry | Dangling reference after factory removal | 2026-06-19 |
| `backend/requirements.txt` | `markitdown` | Replaced by native OCR (tesseract + Pillow) for PDF/image parsing | 2026-06-19 |
| `backend/requirements.txt` | `google-genai==2.7.0` | Never imported by any ComplianceHub code; only causes confusion with API key errors | 2026-06-19 |
| `backend/pyproject.toml` | `google-genai>=2.7` optional dependency | Same as above — re-installs package on `pip install -e .[ai]` | 2026-06-19 |
| `backend/templates/index.html` | Jinja2 509-line template | Superseded by React SPA served through `FRONTEND_STATIC_DIR` | 2026-06-19 |
| `backend/app/services/file_parser.py` | `parse_with_markitdown()` function | Dead fallback — OCR handles all PDF/image parsing | 2026-06-19 |
| `backend/.env` | `HF_API_KEY` | Declared but never read by any Python source | 2026-06-19 |

## Renamed

| Old | New | Why |
|-----|-----|-----|
| `test_anthropic_no_key` | `test_antigravity_no_key` | AnthropicProvider replaced by AntigravityProvider |
| `test_anthropic_reads_env` | `test_antigravity_reads_env` | Same |
| `test_anthropic_init_with_name` | `test_antigravity_init_with_name` | Same |
| `test_anthropic_key_set` | `test_antigravity_key_set` | Same |
| `test_anthropic_key_empty` | `test_antigravity_key_empty` | Same |
| `test_claude_model_id` | updated `claude` → `antigravity_claude_sonnet_46` | Model naming standardized |

## Kept (intentional, not dead)

| Entry | File | Why kept |
|-------|------|----------|
| `fusion`, `auto` models | `model_registry.py` | Paid safety-net fallbacks — last resort if all free tiers fail |
| `google-auth` | system pip | Required by Antigravity OAuth2 token exchange |
