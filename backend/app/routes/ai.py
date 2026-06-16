from fastapi import APIRouter, HTTPException

from app.services.ai.router import get_model_performance, get_model_recommendation, _provider_health
from app.services.ai.model_registry import ALL_MODELS
from app.services.export_validator import ExportValidator

router = APIRouter(tags=["AI"])


@router.get("/api/ai/models/status", summary="AI model status dashboard")
def get_ai_models_status():
    perf = get_model_performance()
    models = []
    for name, caps in ALL_MODELS.items():
        p = perf.get(name, {})
        healthy = _provider_health.get(name, 0) < 3
        first_strength = caps.strengths[0] if caps.strengths else caps.tier
        models.append({
            "name": name,
            "tier": first_strength,
            "tier_category": caps.tier,
            "context_length": caps.context_length,
            "provider": caps.provider,
            "available": True,
            "healthy": healthy,
            "consecutive_fails": _provider_health.get(name, 0),
            "total_uses": p.get("total_uses", 0),
            "avg_quality_score": p.get("avg_quality_score", 0.0),
            "avg_response_time_ms": p.get("avg_response_time_ms", 0),
            "failure_rate_pct": p.get("failure_rate_pct", 0.0),
        })
    tier_order = {"frontier_free": 0, "strong_free": 1, "groq": 2, "local": 3, "paid": 4}
    models.sort(key=lambda m: (tier_order.get(m["tier_category"], 5), m["name"]))

    recommendations = {}
    task_types = ["Audit_Report", "Audit_Plan_Stage_1", "Audit_Plan_Stage_2",
                  "Participation_List", "ISO_Checklist", "Certificate_Text", "TNL"]
    for tt in task_types:
        rec = get_model_recommendation(tt)
        recommendations[tt] = rec.get("recommended", "local")

    return {"models": models, "recommended_for": recommendations}


@router.post("/api/ai/validate", summary="Validate AI output quality")
def validate_ai_output(data: dict):
    task_type = data.get("task_type", "")
    ai_output = data.get("ai_output", {})
    model_used = data.get("model_used", "")
    if not task_type or not ai_output:
        raise HTTPException(status_code=400, detail="task_type and ai_output required")
    validator = ExportValidator(task_type)
    report = validator.get_quality_report(ai_output, model_used)
    return report


@router.get("/api/ai/quality-history", summary="Quality scores over time")
def get_quality_history():
    perf = get_model_performance()
    history = {}
    for name, p in perf.items():
        tasks = p.get("tasks", {})
        history[name] = {
            "total_uses": p.get("total_uses", 0),
            "avg_quality": p.get("avg_quality_score", 0),
            "task_quality": {t: d.get("avg_quality", 0) for t, d in tasks.items()},
        }
    return {"models": history, "period": "all_time"}
