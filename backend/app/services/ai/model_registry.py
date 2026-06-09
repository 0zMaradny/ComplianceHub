"""Model capability registry — single source of truth for all AI models.

Each model has:
  - tier: 'frontier_free' | 'strong_free' | 'basic_free' | 'paid' | 'local'
  - context_length: max tokens
  - strengths: list of task types it excels at
  - provider: which provider class handles it
  - model_id: the OpenRouter model identifier

Only verified free models from OpenRouter are registered.
Paid fallbacks (auto, fusion) kept as last resort only.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCaps:
    model_id: str
    openrouter_name: str
    provider: str
    tier: str
    context_length: int
    strengths: tuple = ()
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# FREE OPENROUTER MODELS — verified as of June 2026
# Only models suitable for ISO audit document generation are included.
# ═══════════════════════════════════════════════════════════════════════════

# Frontier free: 50B+ active params, 1M context — complex multi-clause docs
FRONTIER_FREE = [
    ModelCaps(
        model_id="nvidia/nemotron-3-ultra-550b-a55b:free",
        openrouter_name="nemotron_ultra",
        provider="openrouter",
        tier="frontier_free",
        context_length=1_000_000,
        strengths=("Audit_Report", "ISO_Checklist", "Certificate_Text"),
        notes="55B active / 550B total. Best free model for long-form structured docs.",
    ),
    ModelCaps(
        model_id="qwen/qwen3-coder:free",
        openrouter_name="qwen3_coder",
        provider="openrouter",
        tier="frontier_free",
        context_length=1_048_000,
        strengths=("TNL", "extract_shared_context"),
        notes="35B active / 480B total. Best for structured/JSON extraction.",
    ),
]

# Strong free: 30-120B params, 128K-1M context — standard docs
STRONG_FREE = [
    ModelCaps(
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        openrouter_name="nemotron_super",
        provider="openrouter",
        tier="strong_free",
        context_length=1_000_000,
        strengths=("Audit_Plan_Stage_1", "Audit_Plan_Stage_2", "Participation_List"),
        notes="12B active / 120B total. Fast + high quality for standard docs.",
    ),
    ModelCaps(
        model_id="meta-llama/llama-3.3-70b-instruct:free",
        openrouter_name="llama_70b",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("Audit_Report",),
        notes="70B proven workhorse. Reliable for audit reports.",
    ),
    ModelCaps(
        model_id="moonshotai/kimi-k2.6:free",
        openrouter_name="kimi_k26",
        provider="openrouter",
        tier="strong_free",
        context_length=262_144,
        strengths=("Audit_Report", "Certificate_Text"),
        notes="Multimodal, 262k ctx. Good for narrative generation.",
    ),
    ModelCaps(
        model_id="openai/gpt-oss-120b:free",
        openrouter_name="gpt_oss_120b",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("TNL", "Participation_List"),
        notes="117B MoE from OpenAI. Good for structured extraction.",
    ),
    ModelCaps(
        model_id="google/gemma-4-31b-it:free",
        openrouter_name="gemma_31b",
        provider="openrouter",
        tier="strong_free",
        context_length=262_144,
        strengths=("ISO_Checklist", "Audit_Plan_Stage_1"),
        notes="31B Google Gemma 4. Strong reasoning, 262k ctx.",
    ),
]

# Paid fallbacks — only used when all free tiers fail or aren't available
FUSION = ModelCaps(
    model_id="openrouter/fusion",
    openrouter_name="fusion",
    provider="openrouter",
    tier="paid",
    context_length=131_072,
    strengths=(),
    notes="Multi-model deliberation. Paid. Use only when free tiers exhausted.",
)

AUTO = ModelCaps(
    model_id="openrouter/auto",
    openrouter_name="auto",
    provider="openrouter",
    tier="paid",
    context_length=2_000_000,
    strengths=(),
    notes="OpenRouter picks best model. Paid. Premium last resort.",
)

# Local: llama.cpp
LOCAL = ModelCaps(
    model_id="local",
    openrouter_name="local",
    provider="local",
    tier="local",
    context_length=4_096,
    strengths=(),
    notes="Offline fallback. Qwen 0.5B/1.5B.",
)


# ═══════════════════════════════════════════════════════════════════════════
# REGISTRY — all models indexed by openrouter_name
# ═══════════════════════════════════════════════════════════════════════════

ALL_MODELS: dict = {}
for _m in FRONTIER_FREE + STRONG_FREE + [FUSION, AUTO, LOCAL]:
    ALL_MODELS[_m.openrouter_name] = _m


def get_tier_models(tier: str) -> list:
    """Return all models in a given tier."""
    return [m for m in ALL_MODELS.values() if m.tier == tier]


def get_best_for_task(task_type: str, tier: str) -> "ModelCaps | None":
    """Return the best model in a tier for a given task type.
    If no model claims the task, return the first model in the tier."""
    tier_models = get_tier_models(tier)
    for m in tier_models:
        if task_type in m.strengths:
            return m
    return tier_models[0] if tier_models else None


def get_task_chain(task_type: str) -> list:
    """Build the optimal provider chain for a task type.

    Chain: frontier_free (best match) → strong_free (best match) → paid → local

    Each tier contributes at most 1 model — the best for the task.
    Paid tier contributes at most 1 (fusion, since we can't afford auto).
    Keeps chains to 3-4 models max for speed.
    """
    chain = []
    seen = set()

    for tier in ("frontier_free", "strong_free"):
        m = get_best_for_task(task_type, tier)
        if m and m.openrouter_name not in seen:
            chain.append(m.openrouter_name)
            seen.add(m.openrouter_name)

    # Paid: only fusion (skip auto — too expensive for automated use)
    if "fusion" not in seen:
        chain.append("fusion")

    if "local" not in seen:
        chain.append("local")

    return chain if chain else ["local"]


# ═══════════════════════════════════════════════════════════════════════════
# QUALITY THRESHOLDS
# ═══════════════════════════════════════════════════════════════════════════

FIELD_MIN_LENGTHS: dict = {
    "Audit_Report": {
        "findings_summary": 200,
        "conclusion": 150,
        "scope": 50,
        "report_number": 5,
    },
    "Audit_Plan_Stage_1": {"audit_scope": 80, "audit_objectives": 10},
    "Audit_Plan_Stage_2": {"audit_scope": 80, "audit_objectives": 10},
    "ISO_Checklist": {"overall_assessment": 100},
    "Certificate_Text": {"scope": 50, "certification_decision": 2},
    "Certificate": {"scope": 50, "certification_decision": 2},
    "TNL": {},
}

FIELD_MIN_ITEMS: dict = {
    "Audit_Report": {
        "positive_findings": 3,
        "opportunities_for_improvement": 2,
        "nonconformities": 1,
    },
    "ISO_Checklist": {"sections": 15},
    "Audit_Plan_Stage_1": {"daily_schedule": 6, "audit_objectives": 4},
    "Audit_Plan_Stage_2": {"daily_schedule": 8, "audit_objectives": 4},
    "Participation_List": {"participants": 5},
    "TNL": {"entries": 2},
}
