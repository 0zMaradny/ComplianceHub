"""Model capability registry — single source of truth for all AI models.

Each model has:
  - tier: 'frontier_free' | 'strong_free' | 'basic_free' | 'paid' | 'local'
  - context_length: max tokens
  - strengths: list of task types it excels at
  - provider: which provider class handles it
  - model_id: the OpenRouter model identifier
  - openrouter_name: short name used in create_provider()
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCaps:
    model_id: str                          # e.g. "qwen/qwen3-coder:free"
    openrouter_name: str                   # short name for provider lookup
    provider: str                          # "openrouter" | "local" | "openai" | etc.
    tier: str                              # frontier_free | strong_free | basic_free | paid | local
    context_length: int                    # max context tokens
    strengths: tuple[str, ...] = ()        # task types this model excels at
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# FREE OPENROUTER MODELS — ranked by capability for ISO audit document tasks
# ═══════════════════════════════════════════════════════════════════════════

# Frontier free: 500B+ params, 1M context — use for complex multi-clause docs
FRONTIER_FREE = [
    ModelCaps(
        model_id="nvidia/nemotron-3-ultra-550b-a55b:free",
        openrouter_name="nemotron_ultra",
        provider="openrouter",
        tier="frontier_free",
        context_length=1_000_000,
        strengths=("Audit_Report", "Certificate_Text", "ISO_Checklist"),
        notes="55B active params, 1M ctx. Best free model for long-form structured output.",
    ),
    ModelCaps(
        model_id="qwen/qwen3-coder:free",
        openrouter_name="qwen3_coder",
        provider="openrouter",
        tier="frontier_free",
        context_length=1_048_000,
        strengths=("ISO_Checklist", "TNL", "extract_shared_context"),
        notes="480B MoE (35B active), 1M ctx. Best for structured/JSON output.",
    ),
]

# Strong free: 70-120B params, 128-262k context — use for standard docs
STRONG_FREE = [
    ModelCaps(
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        openrouter_name="nemotron_super",
        provider="openrouter",
        tier="strong_free",
        context_length=1_000_000,
        strengths=("Audit_Plan_Stage_1", "Audit_Plan_Stage_2", "Participation_List"),
        notes="120B (12B active), 1M ctx. Fast + high quality for standard docs.",
    ),
    ModelCaps(
        model_id="meta-llama/llama-3.3-70b-instruct:free",
        openrouter_name="llama_70b",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("Audit_Report", "Audit_Plan_Stage_2"),
        notes="70B proven workhorse. Reliable for standard audit docs.",
    ),
    ModelCaps(
        model_id="openai/gpt-oss-120b:free",
        openrouter_name="gpt_oss_120b",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("TNL", "extract_shared_context", "Participation_List"),
        notes="117B MoE from OpenAI. Good for structured extraction tasks.",
    ),
    ModelCaps(
        model_id="moonshotai/kimi-k2.6:free",
        openrouter_name="kimi_k26",
        provider="openrouter",
        tier="strong_free",
        context_length=262_144,
        strengths=("Audit_Report", "Certificate_Text"),
        notes="Multimodal, 262k ctx. Good for complex narrative generation.",
    ),
    ModelCaps(
        model_id="qwen/qwen3-next-80b-a3b-instruct:free",
        openrouter_name="qwen3_next",
        provider="openrouter",
        tier="strong_free",
        context_length=262_144,
        strengths=("ISO_Checklist", "Audit_Plan_Stage_1"),
        notes="80B (3B active), 262k ctx. Fast for structured checklist generation.",
    ),
    ModelCaps(
        model_id="z-ai/glm-4.5-air:free",
        openrouter_name="glm_45",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("Participation_List", "extract_shared_context"),
        notes="Lightweight, agent-centric. Good for simple structured tasks.",
    ),
    ModelCaps(
        model_id="nousresearch/hermes-3-llama-3.1-405b:free",
        openrouter_name="hermes_405b",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("Audit_Report", "Certificate"),
        notes="405B. Agentic capabilities. Good for complex reasoning docs.",
    ),
]

# Basic free: smaller models — use for simple/extraction tasks only
BASIC_FREE = [
    ModelCaps(
        model_id="openai/gpt-oss-20b:free",
        openrouter_name="gpt_oss_20b",
        provider="openrouter",
        tier="basic_free",
        context_length=131_072,
        strengths=("extract_shared_context",),
        notes="20B. Use only for simple extraction when rate limits hit.",
    ),
]

# Paid / special
FUSION = ModelCaps(
    model_id="openrouter/fusion",
    openrouter_name="fusion",
    provider="openrouter",
    tier="paid",
    context_length=131_072,
    strengths=(),
    notes="Multi-model deliberation. Variable cost. Use only when free tiers exhausted.",
)

AUTO = ModelCaps(
    model_id="openrouter/auto",
    openrouter_name="auto",
    provider="openrouter",
    tier="paid",
    context_length=2_000_000,
    strengths=(),
    notes="OpenRouter picks best model. Variable cost. Use as premium fallback.",
)

# Local: llama.cpp
LOCAL = ModelCaps(
    model_id="local",
    openrouter_name="local",
    provider="local",
    tier="local",
    context_length=4_096,
    strengths=(),
    notes="Offline fallback. Qwen 0.5B/1.5B. Only if server is running.",
)


# ═══════════════════════════════════════════════════════════════════════════
# REGISTRY — all models indexed by openrouter_name
# ═══════════════════════════════════════════════════════════════════════════

ALL_MODELS: dict[str, ModelCaps] = {}
for _m in FRONTIER_FREE + STRONG_FREE + BASIC_FREE + [FUSION, AUTO, LOCAL]:
    ALL_MODELS[_m.openrouter_name] = _m


def get_tier_models(tier: str) -> list[ModelCaps]:
    """Return all models in a given tier."""
    return [m for m in ALL_MODELS.values() if m.tier == tier]


def get_best_for_task(task_type: str, tier: str) -> ModelCaps | None:
    """Return the best model in a tier for a given task type.
    If no model claims the task, return the first model in the tier."""
    tier_models = get_tier_models(tier)
    for m in tier_models:
        if task_type in m.strengths:
            return m
    return tier_models[0] if tier_models else None


def get_task_chain(task_type: str) -> list[str]:
    """Build the optimal provider chain for a task type.

    Chain: frontier_free → strong_free → basic_free → paid → local

    Each tier contributes at most 1 model (the best for the task).
    This keeps chains short and fast while always trying the best free model first.
    """
    chain: list[str] = []
    seen: set[str] = set()

    for tier in ("frontier_free", "strong_free", "basic_free", "paid"):
        m = get_best_for_task(task_type, tier)
        if m and m.openrouter_name not in seen:
            chain.append(m.openrouter_name)
            seen.add(m.openrouter_name)

    if "local" not in seen:
        chain.append("local")

    return chain if chain else ["local"]


# ═══════════════════════════════════════════════════════════════════════════
# QUALITY THRESHOLDS — minimum scores for document acceptance
# ═══════════════════════════════════════════════════════════════════════════

FIELD_MIN_LENGTHS: dict[str, dict[str, int]] = {
    "Audit_Report": {
        "findings_summary": 200,
        "conclusion": 150,
        "scope": 50,
        "report_number": 5,
    },
    "Audit_Plan_Stage_1": {
        "audit_scope": 80,
        "audit_objectives": 10,
    },
    "Audit_Plan_Stage_2": {
        "audit_scope": 80,
        "audit_objectives": 10,
    },
    "ISO_Checklist": {
        "overall_assessment": 100,
    },
    "Certificate_Text": {
        "scope": 50,
        "certification_decision": 2,
    },
    "Certificate": {
        "scope": 50,
        "certification_decision": 2,
    },
    "TNL": {
        # entries[].description checked in quality gate
    },
}

FIELD_MIN_ITEMS: dict[str, dict[str, int]] = {
    "Audit_Report": {
        "positive_findings": 3,
        "opportunities_for_improvement": 2,
        "nonconformities": 1,
    },
    "ISO_Checklist": {
        "sections": 15,
    },
    "Audit_Plan_Stage_1": {
        "daily_schedule": 6,
        "audit_objectives": 4,
    },
    "Audit_Plan_Stage_2": {
        "daily_schedule": 8,
        "audit_objectives": 4,
    },
    "Participation_List": {
        "participants": 5,
    },
    "TNL": {
        "entries": 2,
    },
}
