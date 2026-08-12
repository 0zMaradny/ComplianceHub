# OWL_PENDING_EDITS.md — FROZEN 2026-07-22. Apply exactly. Small-edit discipline:
# change ONLY what each card names; never reformat untouched content. Match every
# <<<FIND>>> verbatim including whitespace. If a <<<FIND>>> is not found verbatim,
# SKIP that card, record "FIND NOT MATCHED — skipped", continue; never guess.
# Apply in order, file by file. LongCat folded in ? registry ends at 21 models.
# Skywork deliberately excluded (gated on rotated key + verified id).

================ PHASE A — RECON ONLY (no edits) ================
1. git rev-parse --show-toplevel   (must equal C:\Users\eos\ComplianceHub; else STOP)
2. git status --short
3. git log --oneline -5
4. git rev-list --left-right --count HEAD...origin/main
5. git ls-files SOUL.md Context.md CONTEXT.md SKILLS.md AGENTS.md MEMORY.md
6. Read model_registry.py + router.py + document_generator.py; report current tier
   lists, any hex strings, and the EXACT name+signature of the router text-gen function.
7. git push --dry-run
DECISION: PROCEED only if path correct AND no tracked modifications (untracked allowed)
AND origin not ahead. Else HARD STOP, edit nothing, report blockers + one fix each.
A 401/403 on dry-run is NOT a stop condition (only means final push needs PAT refresh).

================ PHASE B — APPLY ================

----- Context.md (or CONTEXT.md, whichever exists) -----
C1 [BRAND] FIND: | Doc Gen|python-docx with TÜV branding (TUV_BLUE #003D7A · TUV_RED #C00000)|
REPLACE: | Doc Gen|python-docx; branding read from uploaded templates in backend/templates/04_03_26_consense_audit_documentation/ — no hardcoded hex, no blue (the stored #003D7A was wrong). Verify document_generator.py holds no hardcoded #003D7A; if present, delete and defer to the template.|

C2 [MODEL] FIND the 5 Tier lines (Tier 0 "Claude (Anthropic) — premium..." through Tier 4 "...localhost:8080)"):
REPLACE with:
Tier 0: claude-sonnet-5 (Anthropic, paid; fast-fail skip if key truncated or id 404s)
Tier 1: OpenRouter frontier — nemotron_ultra, qwen3_coder, kimi_k3, owl_alpha, glm_52, minimax_m3, qwen38_max_preview (parallel batch=2)
Tier 2: OpenRouter strong — nemotron_super, llama_70b, qwen3_next, hermes_405b, deepseek_v4_flash, llama_4_scout, glm_5_turbo, longcat_2 (parallel batch=2)
Tier 3: Groq — groq_scout preferred, groq_llama fallback (verify live model via /models)
Tier 4: Local AI — qwen3-4b / qwen-3b / qwen-0.5b (Q4_K_M GGUF, localhost:8080)
Model strings live in model_registry.py (single source of truth). VERIFY qwen38_max_preview, kimi_k3, meituan/longcat-2.0 ids live. Generation providers only — chat-platform models not listed. Gemini excluded from this chain (Mistake #5); routing blocks never carried a Gemini entry, so no Gemini line to delete.
Deprecation watch: kimi_k26 retired 2026-05-25; claude-sonnet-4 retired 2026-06-15 (never reference); DeepSeek V4 naming changes 2026-07-24 (re-verify deepseek_v4_flash then).
Free coding layer (NOT in this router): Laguna S 2.1 (Poolside) free on OpenCode — 1M, open-source, code-specialist — lives in OpenCode/coding-tool layer (Cline/Roo/Aider once an id known), not model_registry/5-tier, because it is a code model and the free path is OpenCode's pool not an OpenRouter id. Add to router later ONLY if a verified poolside/laguna id appears on OpenRouter (then STRONG_FREE). Until opencode fixed, free coding role = Cline/Roo/Aider over OpenRouter-free or local Ollama. Gemini Flash pricing (3.6 Flash -17% output, 3.5 Flash Lite -80%) is chat-selection in GEMINI_GEMS_GUIDE.md — never in this router (Mistake #5).
(The Fallback line after the Tier block is NOT in this FIND; it stays.)

C3 [MODEL] FIND: | app/services/ai/model_registry.py|14 models: PREMIUM + FRONTIER_FREE + STRONG_FREE + GROQ_FREE + LOCAL_FREE|
REPLACE: | app/services/ai/model_registry.py|21 models across 5 tiers (recount after edit): PREMIUM + FRONTIER_FREE + STRONG_FREE + GROQ_FREE + LOCAL_FREE. Updated 2026-07-22; single source of truth, router.py imports from here. Generation providers only — chat-platform models not registered here.|

C4 [CLIENT] FIND: Rule: Identify gaps ONLY. Never offer solutions.
REPLACE with that line + appended after it (blank line then):
Active Engagements — Canonical Registry (Track A)
| #|Client|Prefix|Formula|Language|Standards|Type|Status|
| ---|---|---|---|---|---|---|---|
| 5|Diriyah|DIRIYAH-RES-|L×S|English|ISO 22320 · 22316|Maturity & Alignment (guidance stds)|RPT-1 + RPT-2 shipped|
| 6|KFSHRC|KFSHRC-ISMS-|L×I|English|ISO 27001|Pre-Assessment|Audit 17–18 Jul 2026; report in Track A project|

C5 [CLIENT] FIND: Doc Code Example:`AHSA-ISMS-RISK-001`
REPLACE with that line + appended after it (blank line then):
Client Detail — Diriyah
Full Name: Diriyah Gate Development Authority
Track: A — Maturity & Alignment Assessment (guidance standards; not certifiable MS per ISO 17021)
Standards: ISO 22320:2018 · ISO 22316:2017
Risk Formula: L×S
Language: English
Doc Code Prefix: DIRIYAH-RES-
Regulatory Overlay: Vision 2030 giga-project · DGDA · Saudi Civil Defense · NCA ECC (IT scope) · GEA · SRCA · MOMRAH · NCM
Status: RPT-1 (22316) + RPT-2 (22320) shipped July 2026

Client Detail — KFSHRC
Full Name: King Faisal Specialist Hospital & Research Centre
Track: A — Pre-Assessment
Standard: ISO/IEC 27001:2022
Risk Formula: L×I
Language: English
Doc Code Prefix: KFSHRC-ISMS-
Phase: Pre-Assessment (audit 17–18 July 2026)
Privacy: MAXIMUM — healthcare. Named/PII content to Claude via OpenRouter only; scrub patient names, MRNs, employee personal details before any non-Tier-0 call.

C7 [PLATFORM] FIND: | Chat|AI chat interface|
REPLACE with that row + appended after it: | Unified chat|Open WebUI (Docker, localhost:3000) is the single chat front-end; it reaches ComplianceHub as an OpenAI-compat provider at host.docker.internal:8000/v1 and as a Tool (standards/generate/status). ComplianceHub React UI remains for structured workflows.|

----- SKILLS.md -----
S1 [COUNT] FIND: Skill count: 34 active (01, 01b, 02–12, 14–17, 19–35) · 2 tombstoned (13, 18 — see below)
REPLACE: Skill count: 36 active (01, 01b, 02–12, 14–17, 19–37) · 2 tombstoned (13, 18 — see below)
S2 [BRAND] FIND: TÜV branding: TUV_BLUE #003D7A, TUV_RED #C00000
REPLACE: TÜV branding: read theme colors from the uploaded templates (backend/templates/04_03_26_consense_audit_documentation/). Never hardcode a brand hex. The real template has no blue — the stored #003D7A was wrong and is removed. Confirm document_generator.py has no hardcoded #003D7A; if it does, delete it and defer to the template.
S3 [MODEL] FIND the 5 Skill-14 Tier lines (Tier 0 "Claude Sonnet 4..." through Tier 4 "...Qwen2.5-3B ~60s/doc)"):
REPLACE with:
Tier 0: claude-sonnet-5 (Anthropic, paid; fast-fail skip if key truncated or id 404s)
Tier 1: OpenRouter frontier (Nemotron Ultra, Qwen3 Coder 480B, Kimi K3, Owl Alpha, GLM-5.2, MiniMax M3, Qwen3.8-Max-Preview — parallel batch=2)
Tier 2: OpenRouter strong (Nemotron Super, Llama 70B, Qwen3 Next 80B, Hermes 405B, DeepSeek V4 Flash, Llama 4 Scout, GLM-5-Turbo, LongCat 2.0 — parallel batch=2)
Tier 3: Groq (Llama 4 Scout preferred, Llama 3.3 70B fallback)
Tier 4: Local AI (Qwen3-4B ~40s/doc or Qwen-3B ~60s/doc or Qwen-0.5B)
VERIFY qwen3.8-max-preview, kimi-k3, meituan/longcat-2.0 ids live. DeepSeek V4 rename 2026-07-24. Generation providers only — chat-platform models not listed; Gemini excluded (Mistake #5).
S4 [BRAND] FIND: Palette: #44546A (dark slate) primary · #C00000 (TÜV red) accent · #4472C4 (blue) · #FFC000 (gold)
REPLACE: Palette: read from the uploaded training template; never hardcode a hex. The previous hardcoded palette contained a blue (#4472C4) that violates the no-blue rule — removed, do not use it. Confirm the real deck colors from the template before generating any slide.
S5 [COUNT] FIND: | 36|Workflow Phasing|"Build ",  "Create ",  "Draft "|
REPLACE with that row + appended: | 37|Milestone Judge|"Review milestone ",  "Judge output ",  "Pass or fail ",  "Verify against plan "|
S6 [COUNT] FIND: Small-Edit Discipline: When user asks for a targeted change, change ONLY that. Do not "improve" untouched parts.
REPLACE with that line + appended after it (blank line then the full Skill 37 body verbatim):

Skill 37 — Milestone Judge (Plan-vs-Output Review)
Trigger: "Review this milestone " /  "Judge this output " /  "Milestone check " /  "Pass or fail " /  "Did the model do it right " /  "Review against the plan " /  "Check the deliverable " /  "Is this done right " /  "Verify against PRD " /  "Cheaper model finished " /  "Review the diff " /  "Milestone review "
Auto-trigger: ANY message where a completed deliverable (diff, file, output, or pasted work) is presented for judgement against a plan, PRD, task description, or success criteria — and the ask is "is this right?" not "build this." Distinct from Skill 22 (format/completeness gates) and Skill 02 (ISO clause audit). Compares planned vs produced, regardless of whether ISO-related, code, document, or other.
Agent: Agent 1 (Judge) — pass/fail verdict, gap identification, fix list. Agent 8 (Prompt Architect) only if Step 4 produces a new standing rule for MEMORY.md/SOUL.md.
When to use: after a cheaper model finishes a milestone from a PRD; after any delegated task needing verification before acceptance; at Skill 16 gate transitions for a second-eye pass/fail; after batch runs needing spot-checks.
When NOT to use: ISO clause-by-clause audit ? Skill 02/07; pre-delivery format/completeness gate ? Skill 22; building the deliverable ? route to builder agent 2/3/4/5/7; strategic stress-test ? Skill 33.
Steps:
1. CONFIRM INPUTS — THE PLAN (PRD section/task spec/success criteria; if not pasted ask once "Which plan/PRD/task is this judged against?") and THE WORK (the diff/file/output/pasted deliverable).
2. VERDICT FIRST — one line, no preamble: `VERDICT: PASS` or `VERDICT: FAIL — [one-line reason]`.
3. GAPS — everything missed/fudged/silently changed vs the plan; point at exact lines/sections/cells; hunt substance (wrong logic, skipped requirements, silent scope cuts, formula errors, client isolation breaches, missing Skill 21/22 gates, wrong doc codes/formulas); ignore style unless plan specified it; if none state "No gaps found" — never manufacture issues.
4. FIX LIST — each gap ? numbered fix a cheaper model executes one at a time (what to change · where · done-check); skip if PASS with no gaps.
5. STANDARDS — if a gap pattern recurred (check MEMORY.md Mistakes): write the preventing rule + name the file (SOUL/AGENTS/SKILLS/MEMORY/Context); if new, flag for Skill 01b; skip if no pattern.
Output structure:
VERDICT: [PASS / FAIL — reason]
GAPS:
1. [exact location] — [what's wrong vs plan]
FIX LIST:
1. [what] · [where] · [done-check]
STANDARDS:
- [rule] ? [file]
Hard rules: never rewrite the work (judge only; fix list is for a cheaper model); never soften a FAIL; never run Skill 22 as a substitute for plan comparison (sequence OK: 37 then 22 if PASS+client-facing, never merge); never mix Track A/B in verdict; formula integrity mandatory in Step 3 for any client deliverable (MOI V=S×(1-U/4) · UACC/SAGCO L×S · Al-Ahsa L×I — any deviation = automatic FAIL); client isolation mandatory in Step 3 (any cross-contamination of prefixes/colours/vocabulary/formulas = automatic FAIL); run Skill 21 on the fix-list text itself.
Linked Skills: Skill 22 · Skill 01b · Skill 16 · Skill 15

----- SOUL.md -----
U1 [BRAND] FIND: TÜV branding: TUV_BLUE #003D7A · TUV_RED #C00000
REPLACE: TÜV branding: sourced from the uploaded templates only (backend/templates/04_03_26_consense_audit_documentation/) — never hardcode a hex, never use blue. The stored #003D7A is wrong and removed.
U2 [BRAND] FIND: Never explain compliance with instructions — "Show don't tell." If output is concise, don't say so. If a gate passed, don't narrate it. Just deliver clean output.
REPLACE with that line + appended: Never hardcode a TÜV brand hex or put blue in TÜV branding. Branding is read from the uploaded templates (backend/templates/04_03_26_consense_audit_documentation/); the stored #003D7A blue was wrong. Applies to OWL files, generated prompts, ComplianceHub UI, and any chat-platform theme.
U3 [COUNT] FIND: | Active Skills|35|July 2026|  REPLACE: | Active Skills|36|July 2026|
U4 [COUNT] FIND: | Active Clients|4 (MOI, UACC, SAGCO, Al-Ahsa)|July 2026|  REPLACE: | Active Clients|6 (Track B: MOI, UACC, SAGCO, Al-Ahsa · Track A: Diriyah, KFSHRC)|July 2026|
U5 [COUNT] FIND: | NEVER Laws|12|July 2026|  REPLACE: | NEVER Laws|13|July 2026|

----- AGENTS.md -----
A1 [BRAND] FIND: | TÜV|#003D7A|#C00000|  REPLACE: | TÜV|READ FROM TEMPLATE — no blue, #003D7A was wrong|READ FROM TEMPLATE|
A2 [COUNT] FIND: Linked Skills: Skill 02 · Skill 07 · Skill 12 · Skill 22 · Skill 26 · Skill 28  REPLACE: Linked Skills: Skill 02 · Skill 07 · Skill 12 · Skill 22 · Skill 26 · Skill 28 · Skill 37
A3 [COUNT] FIND: | Manage my inbox · summarize meeting · write me a · draft a caption/email/script|Agent 6 (Concierge) — personal ops, never client-facing|Skill 35 (Personal Ops)|  REPLACE with that row + appended: | Milestone review · judge output · pass or fail · review against plan · verify deliverable vs PRD|Agent 1 (Judge)|Skill 37|

----- MEMORY.md -----
M1 [GEMINI] FIND: | 5|Gemini API in any output|api.anthropic.com/v1/messages only (via OpenRouter in KSA)|
REPLACE: | 5|Gemini in the doc-gen router / model_registry, or Gemini API in any output|Gemini (any version, incl. 3.6) is EXCLUDED from the ComplianceHub doc-gen router and from model_registry.py — it is a chat / Deep-Research platform only (Gemini Web / Gems), company-paid, never an artifact-generation provider. Generated artifacts use api.anthropic.com/v1/messages via OpenRouter in KSA.|
M2 [BRAND] FIND: | 48|Using Gemini Android for long sessions|Gemini Android fails after ~45 mins. Use Web for long tasks, Android for quick queries.|
REPLACE: that row + appended: | 49|Hardcoding TUV_BLUE #003D7A or any blue in TÜV branding|The real uploaded TÜV template has no blue. Branding = read theme colors from backend/templates/04_03_26_consense_audit_documentation/; never hardcode a hex in OWL files, generated prompts, ComplianceHub UI, or chat themes. Scrub #003D7A and #4472C4 from document_generator.py and from any Word-formatting prompt handed to another platform.|
M3 [LOG] DELETE these three rows entirely (leave row 27):
| 24|Create Google Drive OWL System/ folder structure|High|
| 25|Strip + convert OWL files for Gemini ? upload to Drive|High|
| 26|Create 10 Gemini Gems at gemini.google.com|High|
M4 [LOG] FIND: Client Segmentation: Track A (Audit) vs Track B (Implementation) clarified. MOC archived.
REPLACE with that line + appended after it:
July 2026 — Client Ship + Platform + Model-Tier Refresh Session
Shipped Diriyah ISO 22316 (RPT-1) + ISO 22320 (RPT-2); KFSHRC ISO 27001 pre-assessment drafted by user in Track A project. Both logged as Track A engagements (isolation fix). Delivered ComplianceHub 10-gate validator, router rewrite, document_generator validate_and_heal, iso_clause_database.json. Created + confirmed 10 Gemini Gems synced to Drive (Open Items 24/25/26 closed). Desktop coding agents: Mistral Vibe, Qoder, Goose, ZCode, Z.ai; Qwen Code via Android browser = only mobile coding path. Standardized on 2-surface minimum (Open WebUI chat + Goose code). Just Ship protocol; backlog audit; SAGCO F4/Stage2/F2 reclassified client-owned. Model-tier refresh: claude-sonnet-5; kimi_k3; added qwen38_max_preview, glm_52, minimax_m3 (frontier), deepseek_v4_flash, llama_4_scout, glm_5_turbo, longcat_2 (strong) (14?21). Gemini removed from doc-gen router + registry (Mistake #5). Skill 37 added; active-skill count reconciled to 36. TÜV blue hex scrubbed (NEVER #13, mistake #49). Open WebUI = unified chat front-end; ComplianceHub exposes OpenAI-compat /v1 + a Tool. Laguna S 2.1 ? OpenCode/coding layer only; Gemini 3.6 Flash/3.5 Flash Lite ? chat-selection in GEMINI_GEMS_GUIDE.md; meituan/longcat-2.0 ? STRONG_FREE (Meituan = Chinese origin, same privacy tier as DeepSeek — anonymized Track A + general/coding only, never PII/KSA gov/healthcare, never Tier 0). Deprecation watch: DeepSeek V4 naming 2026-07-24.

----- model_registry.py [CODE] (read-first; set the 5 lists to exactly this; keep imports/ALL_MODELS/helpers; no Gemini; list names unchanged so router.py needs no edit) -----
Add top comment: # Updated 2026-07-22: claude-sonnet-5; kimi_k3; added qwen38_max_preview, glm_52, minimax_m3 (frontier); deepseek_v4_flash, llama_4_scout, glm_5_turbo, longcat_2 (strong). Total 14?21. VERIFY qwen38_max_preview + kimi_k3 + meituan/longcat-2.0 ids live. Generation providers only (Mistake #5).
PREMIUM = [
    {"key": "premium_claude", "provider": "anthropic", "model": "claude-sonnet-5", "context": 1_000_000},
]
FRONTIER_FREE = [
    {"key": "nemotron_ultra", "provider": "openrouter", "model": "nvidia/nemotron-ultra-251b", "context": 256_000},
    {"key": "qwen3_coder", "provider": "openrouter", "model": "qwen/qwen3-coder-480b-a35b-instruct", "context": 262_000},
    {"key": "kimi_k3", "provider": "openrouter", "model": "moonshotai/kimi-k3", "context": 1_000_000},
    {"key": "owl_alpha", "provider": "openrouter", "model": "owl-alpha", "context": 128_000},
    {"key": "glm_52", "provider": "openrouter", "model": "z-ai/glm-5.2", "context": 1_000_000},
    {"key": "minimax_m3", "provider": "openrouter", "model": "minimax/minimax-m3", "context": 1_000_000},
    {"key": "qwen38_max_preview", "provider": "openrouter", "model": "qwen/qwen3.8-max-preview", "context": 1_000_000},
]
STRONG_FREE = [
    {"key": "nemotron_super", "provider": "openrouter", "model": "nvidia/nemotron-3-super-120b", "context": 256_000},
    {"key": "llama_70b", "provider": "openrouter", "model": "meta-llama/llama-3.3-70b-instruct", "context": 128_000},
    {"key": "qwen3_next", "provider": "openrouter", "model": "qwen/qwen3-next-80b-a3b-instruct", "context": 128_000},
    {"key": "hermes_405b", "provider": "openrouter", "model": "nousresearch/hermes-3-llama-3.1-405b", "context": 128_000},
    {"key": "deepseek_v4_flash", "provider": "openrouter", "model": "deepseek/deepseek-v4-flash", "context": 1_000_000},
    {"key": "llama_4_scout", "provider": "openrouter", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "context": 128_000},
    {"key": "glm_5_turbo", "provider": "openrouter", "model": "z-ai/glm-5-turbo", "context": 1_000_000},
    {"key": "longcat_2", "provider": "openrouter", "model": "meituan/longcat-2.0", "context": 262_000},
]
GROQ_FREE = [
    {"key": "groq_scout", "provider": "groq", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "context": 128_000},
    {"key": "groq_llama", "provider": "groq", "model": "llama-3.3-70b-versatile", "context": 128_000},
]
LOCAL_FREE = [
    {"key": "qwen3_4b", "provider": "local", "model": "qwen3-4b", "context": 32_768},
    {"key": "qwen_3b", "provider": "local", "model": "qwen-3b", "context": 8_192},
    {"key": "qwen_05b", "provider": "local", "model": "qwen-0.5b", "context": 4_096},
]
(longcat_2 context: read OpenRouter page; if 1M listed use 1_000_000 else keep 262_000. If moonshotai/kimi-k3 not resolvable, fall kimi_k3 model string to moonshotai/kimi-k2.7-code, keep key.)

----- document_generator.py [CODE] (audit only) -----
Grep #003D7A / 003D7A / 4472C4 / TUV_BLUE. If hits: remove hex literals, defer to template theme (read template; do NOT invent a replacement hex); report exact lines. If none: record "generator already defers to templates", change nothing.

----- backend/app/api/openai_compat.py [CODE] (create) + 2 lines in main.py -----
Read router.py; use the EXACT text-gen function from recon (do not guess name; do not modify router.py; if sync, drop the await). Create the file:
# OpenAI-compatible chat endpoint so Open WebUI talks through the 5-tier router.
import time, uuid
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai.router import generate_text   # ADAPT name to recon finding
ROUTER_TIMEOUT = 120
MODEL_NAME = "compliancehub"
router = APIRouter(prefix="/v1", tags=["openai-compat"])
class ChatMessage(BaseModel):
    role: str; content: str
class ChatRequest(BaseModel):
    model: str = MODEL_NAME; messages: list[ChatMessage]; stream: bool = False
    temperature: float = 0.3; max_tokens: int = 4096
@router.post("/chat/completions")
async def chat_completions(req: ChatRequest):
    prompt = "\n".join(f"{'User' if m.role=='user' else 'Assistant'}: {m.content}" for m in req.messages)
    try: text = await generate_text(prompt=prompt, task_type="chat", timeout=ROUTER_TIMEOUT)
    except Exception as e: text = f"ComplianceHub router error: {e}"
    return {"id": f"chatcmpl-{uuid.uuid4().hex[:12]}", "object": "chat.completion",
            "created": int(time.time()), "model": MODEL_NAME,
            "choices": [{"index":0,"message":{"role":"assistant","content":text},"finish_reason":"stop"}],
            "usage": {"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}}
@router.get("/models")
async def list_models():
    return {"object":"list","data":[{"id":MODEL_NAME,"object":"model","created":int(time.time()),"owned_by":"compliancehub"}]}
In main.py add exactly: from app.api.openai_compat import router as openai_router  AND  app.include_router(openai_router). No Gemini provider. No brand hex.

----- OPTIONAL GEMINI_GEMS_GUIDE.md (only if exists) -----
Guard: skip if "Gemini Flash pricing 2026-07-22" present. Append:
Gemini Flash pricing 2026-07-22 (chat/flash selection only — never doc-gen router, Mistake #5):
- 3.6 Flash: 17% cheaper output than 3.5 Flash; prefer for fast+cheap chat / Gem default where 1M Pro overkill.
- 3.5 Flash Lite: 80% cheaper than 3.5 Flash; prefer for high-volume low-stakes chat.
- Reserve 3.1 Pro / 3.5 Pro for long-context drafting, Deep Research, quality-critical Arabic MSA.
These are CHAT/Deep-RESEARCH providers (company-paid); never enter model_registry.py or 5-tier chain.

----- OPTIONAL opencode.json (only if exists AND configured) -----
Guard: skip if laguna entry exists or opencode not operational (record "skipped — opencode not operational"). Else add Laguna S 2.1 as selectable model using OpenCode's current id (VERIFY from OpenCode model list; likely poolside/laguna-s-2.1), context 1_000_000, no API key.

================ PHASE C — VERIFY (report raw output) ================
cd C:\Users\eos\ComplianceHub
Select-String -Path SOUL.md,Context.md,SKILLS.md,AGENTS.md -Pattern "#003D7A","#4472C4","TUV_BLUE"
Select-String -Path Context.md,SKILLS.md -Pattern "kimi_k26","Kimi K2.6","14 models: PREMIUM"
Select-String -Path SOUL.md -Pattern "NEVER Laws\|13","Active Skills\|36","Active Clients\|6"
Select-String -Path SKILLS.md -Pattern "36 active","\| 37\|Milestone Judge"
Select-String -Path MEMORY.md -Pattern "\| 49\|"
Select-String -Path Context.md,SKILLS.md -Pattern "Claude Sonnet 4"
cd backend ; python -m compileall . -q ; python -m pyflakes app/
python -c "from app.services.ai.model_registry import ALL_MODELS, FRONTIER_FREE, STRONG_FREE; print('total', len(ALL_MODELS)); print('frontier', [m['key'] for m in FRONTIER_FREE]); print('strong', [m['key'] for m in STRONG_FREE])"
cd .. ; Select-String -Path backend\app\services\document_generator.py -Pattern "#003D7A","003D7A","4472C4"
Expected: 1st group EMPTY; kimi/14-models EMPTY; count/law/mistake ONE each; registry total 21 with kimi_k3/qwen38_max_preview/glm_52/minimax_m3 in frontier + deepseek_v4_flash/llama_4_scout/glm_5_turbo/longcat_2 in strong + NO kimi_k26; compileall/pyflakes zero; doc_gen grep empty (or report lines). KNOWN EXPECTED (not failures): "Claude Sonnet 4" may hit the LEGACY artifact line `YES Model: claude-sonnet-4-6` in Context.md + the strip-rule line in SKILLS.md — leave them. Any OTHER hit IS a miss. A 404ing id later is non-fatal.

================ PHASE D — COMMIT (fires post-commit auto-push) ================
Stage only changed TRACKED files (per recon step 5). OWL markdown: include if tracked, else leave on disk + record "OWL files untracked — sync via Drive/Gems" (expected). Always include backend code changed/created. No extra spec file.
Commit message: session: 2026-07-22 model-tier refresh (21) + branding fix + Skill 37 + Track A registry + Open WebUI /v1
Report push result. If commit landed but push failed: "commit local, push failed — refresh PAT then git push"; do not retry blindly.
FINAL REPORT: recon outputs · per-card applied/skipped · full VERIFY output · doc_gen grep result · openai_compat router function name wired · commit hash · push result. No rule-narration — outputs only.
