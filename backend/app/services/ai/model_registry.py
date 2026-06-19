"""Model capability registry — single source of truth for all AI models.

Each model has:
  - tier: 'frontier_free' | 'strong_free' | 'groq' | 'local'
  - context_length: max tokens
  - strengths: list of task types it excels at
  - provider: which provider class handles it
  - model_id: the OpenRouter model identifier

Only verified free models from OpenRouter are registered.
Paid fallbacks (fusion, auto) kept as last resort only.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelCaps:
    model_id: str
    openrouter_name: str
    provider: str
    tier: str
    context_length: int
    strengths: tuple[str, ...] = ()
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
    ModelCaps(
        model_id="moonshotai/kimi-k2.6:free",
        openrouter_name="kimi_k26",
        provider="openrouter",
        tier="frontier_free",
        context_length=262_144,
        strengths=("Audit_Report", "Certificate_Text", "chat_query"),
        notes="Kimi K2.6 — ties GPT-5.5 on coding, 262k ctx. Excellent narrative generation.",
    ),
    ModelCaps(
        model_id="openrouter/owl-alpha",
        openrouter_name="owl_alpha",
        provider="openrouter",
        tier="frontier_free",
        context_length=1_048_756,
        strengths=("Audit_Report", "Certificate_Text", "chat_query", "extract_shared_context"),
        notes="Owl Alpha — 1M ctx, agentic tool use. Designed for agentic workloads.",
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
        strengths=("Audit_Report", "Audit_Plan_Stage_2"),
        notes="70B proven workhorse. Reliable for standard audit docs.",
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
        model_id="nousresearch/hermes-3-llama-3.1-405b:free",
        openrouter_name="hermes_405b",
        provider="openrouter",
        tier="strong_free",
        context_length=131_072,
        strengths=("Audit_Report", "Certificate", "Certificate_Text"),
        notes="405B. Agentic capabilities. Good for complex reasoning docs.",
    ),
]

# Groq: independent API endpoint, ~800 t/s
GROQ_FREE = [
    ModelCaps(
        model_id="llama-3.3-70b-versatile",
        openrouter_name="groq_llama",
        provider="groq",
        tier="groq",
        context_length=131_072,
        strengths=("Audit_Report", "ISO_Checklist", "chat_query"),
        notes="Groq Llama 3.3 70B — fastest free inference at ~800 t/s. Independent API fallback.",
    ),
]

# Local: llama.cpp — ordered best-first
LOCAL_FREE = [
    ModelCaps(
        model_id="qwen3-4b",
        openrouter_name="local_qwen3_4b",
        provider="local",
        tier="local",
        context_length=32768,
        strengths=("chat_query", "ISO_Checklist", "Audit_Report", "Audit_Plan_Stage_1", "Audit_Plan_Stage_2", "TNL"),
        notes="Qwen3-4B (Q4_K_M) via local llama-server. ~40s/doc, best local quality. Needs ~3 GB RAM.",
    ),
    ModelCaps(
        model_id="qwen-3b",
        openrouter_name="local_qwen_3b",
        provider="local",
        tier="local",
        context_length=8192,
        strengths=("chat_query", "ISO_Checklist", "Audit_Plan_Stage_1", "Audit_Plan_Stage_2"),
        notes="Qwen2.5-3B (Q4_K_M) via local llama-server. ~60s/doc, 6x params over qwen-0.5b. Needs ~2.5 GB RAM.",
    ),
    ModelCaps(
        model_id="qwen-0.5b",
        openrouter_name="local_qwen",
        provider="local",
        tier="local",
        context_length=4096,
        strengths=("chat_query",),
        notes="Qwen2.5-0.5B via local llama-server (localhost:8080). ~20s/doc, CPU-only ARM64 fallback, lowest quality.",
    ),
]

# Antigravity: free Claude via Google's internal API (confirmed working June 18 2026)
ANTIGRAVITY_FREE = [
    ModelCaps(
        model_id="claude-sonnet-4-6",
        openrouter_name="antigravity_claude_sonnet_46",
        provider="antigravity",
        tier="antigravity",
        context_length=200_000,
        strengths=(
            "Audit_Report", "ISO_Checklist", "Certificate_Text", "Certificate",
            "Audit_Plan_Stage_1", "Audit_Plan_Stage_2", "Participation_List", "TNL",
            "Management_Review_Minutes", "Corrective_Action_Report", "Gap_Analysis_Report",
            "Statement_of_Applicability", "Business_Impact_Analysis",
            "Records_of_Processing_Activities", "Risk_Treatment_Plan",
            "Incident_Investigation_Report", "Internal_Audit_Program",
            "Environmental_Aspect_Register", "Hazard_Identification_Register",
            "Energy_Review", "Compliance_Obligations_Register",
            "Service_Portfolio", "Service_Catalogue", "Supplier_Agreement_Register",
            "Business_Relationship_Register", "Capacity_Management_Plan",
            "Change_Management_Register", "Release_Deployment_Plan",
            "Incident_Management_Log", "Problem_Management_Register",
            "Service_Continuity_Plan", "Availability_Management_Report",
            "extract_shared_context", "chat_query",
        ),
        notes="Claude Sonnet 4.6 — free via Antigravity API. Used as Tier 0.",
    ),
    ModelCaps(
        model_id="claude-opus-4-6-thinking",
        openrouter_name="antigravity_claude_opus_46",
        provider="antigravity",
        tier="antigravity",
        context_length=200_000,
        strengths=(
            "Audit_Report", "ISO_Checklist", "Certificate_Text", "Certificate",
            "Audit_Plan_Stage_1", "Audit_Plan_Stage_2", "Gap_Analysis_Report",
            "Statement_of_Applicability", "Risk_Treatment_Plan",
            "extract_shared_context",
        ),
        notes="Claude Opus 4.6 — free via Antigravity API. Extended thinking, use for complex reasoning.",
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

LOCAL_NAMES = [m.openrouter_name for m in LOCAL_FREE]

# ═══════════════════════════════════════════════════════════════════════════
# REGISTRY — all models indexed by openrouter_name
# ═══════════════════════════════════════════════════════════════════════════

ALL_MODELS: dict[str, ModelCaps] = {}
for _m in ANTIGRAVITY_FREE + FRONTIER_FREE + STRONG_FREE + GROQ_FREE + LOCAL_FREE + [FUSION, AUTO]:
    ALL_MODELS[_m.openrouter_name] = _m

ANTIGRAVITY_NAMES = [m.openrouter_name for m in ANTIGRAVITY_FREE]
FRONTIER_NAMES = [m.openrouter_name for m in FRONTIER_FREE]
STRONG_NAMES = [m.openrouter_name for m in STRONG_FREE]
GROQ_NAMES = [m.openrouter_name for m in GROQ_FREE]
ALL_API_NAMES = ANTIGRAVITY_NAMES + FRONTIER_NAMES + STRONG_NAMES + GROQ_NAMES + LOCAL_NAMES


def get_tier_models(tier: str) -> list[ModelCaps]:
    return [m for m in ALL_MODELS.values() if m.tier == tier]


def get_best_for_task(task_type: str, tier: str) -> "ModelCaps | None":
    """Return the best model in a tier for a given task type.
    If no model claims the task, return the first model in the tier."""
    tier_models = get_tier_models(tier)
    for m in tier_models:
        if task_type in m.strengths:
            return m
    return tier_models[0] if tier_models else None


MIN_SCORE_THRESHOLDS: dict[str, int] = {
    "Audit_Report": 70,
    "Certificate_Text": 70,
    "Certificate": 70,
    "ISO_Checklist": 60,
    "Audit_Plan_Stage_1": 60,
    "Audit_Plan_Stage_2": 60,
    "Participation_List": 50,
    "TNL": 50,
    "Management_Review_Minutes": 65,
    "Corrective_Action_Report": 65,
    "Gap_Analysis_Report": 60,
    "Statement_of_Applicability": 60,
    "Business_Impact_Analysis": 60,
    "Records_of_Processing_Activities": 60,
    "Risk_Treatment_Plan": 65,
    "Incident_Investigation_Report": 65,
    "Internal_Audit_Program": 60,
    "Environmental_Aspect_Register": 55,
    "Hazard_Identification_Register": 55,
    "Energy_Review": 55,
    "Compliance_Obligations_Register": 55,
    "Service_Portfolio": 50,
    "Service_Catalogue": 50,
    "Supplier_Agreement_Register": 50,
    "Business_Relationship_Register": 50,
    "Capacity_Management_Plan": 50,
    "Change_Management_Register": 55,
    "Release_Deployment_Plan": 50,
    "Incident_Management_Log": 50,
    "Problem_Management_Register": 50,
    "Service_Continuity_Plan": 55,
    "Availability_Management_Report": 50,
    "extract_shared_context": 40,
    "chat_query": 0,
}

LOCAL_3_STRIKE_THRESHOLD = 30

TASK_PRIORITY: dict[str, str] = {
    "Audit_Report": "high",
    "Certificate_Text": "high",
    "Certificate": "high",
    "ISO_Checklist": "high",
    "Audit_Plan_Stage_1": "high",
    "Audit_Plan_Stage_2": "high",
    "Participation_List": "high",
    "TNL": "high",
    "Management_Review_Minutes": "high",
    "Corrective_Action_Report": "high",
    "Gap_Analysis_Report": "high",
    "Statement_of_Applicability": "high",
    "Business_Impact_Analysis": "high",
    "Records_of_Processing_Activities": "high",
    "Risk_Treatment_Plan": "high",
    "Incident_Investigation_Report": "high",
    "Internal_Audit_Program": "high",
    "Environmental_Aspect_Register": "high",
    "Hazard_Identification_Register": "high",
    "Energy_Review": "high",
    "Compliance_Obligations_Register": "high",
    "Service_Portfolio": "high",
    "Service_Catalogue": "high",
    "Supplier_Agreement_Register": "high",
    "Business_Relationship_Register": "high",
    "Capacity_Management_Plan": "high",
    "Change_Management_Register": "high",
    "Release_Deployment_Plan": "high",
    "Incident_Management_Log": "high",
    "Problem_Management_Register": "high",
    "Service_Continuity_Plan": "high",
    "Availability_Management_Report": "high",
    "extract_shared_context": "low",
    "chat_query": "low",
}

FIELD_MIN_LENGTHS: dict[str, dict[str, int]] = {
    "Audit_Report": {"findings_summary": 300, "conclusion": 150, "scope": 50, "report_number": 5},
    "ISO_Checklist": {"scope": 100, "methodology": 100, "overall_assessment": 100},
    "TNL": {"scope": 100},
    "Audit_Plan_Stage_1": {"scope_objectives": 100, "audit_scope": 80, "audit_objectives": 10},
    "Audit_Plan_Stage_2": {"scope_objectives": 100, "audit_scope": 80, "audit_objectives": 10},
    "Certificate_Text": {"scope": 50, "certification_decision": 2},
    "Certificate": {"scope": 50, "certification_decision": 2},
}

FIELD_MIN_ITEMS: dict[str, dict[str, int]] = {
    "Audit_Report": {"findings": 3, "recommendations": 2, "positive_findings": 3, "opportunities_for_improvement": 2, "nonconformities": 1},
    "ISO_Checklist": {"sections": 5, "control_items": 10},
    "TNL": {"sections": 4, "entries": 2},
    "Audit_Plan_Stage_1": {"daily_schedule": 2, "team_members": 2, "audit_objectives": 4},
    "Audit_Plan_Stage_2": {"daily_schedule": 2, "team_members": 2, "audit_objectives": 4},
    "Participation_List": {"participants": 3},
}
