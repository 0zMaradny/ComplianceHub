from fastapi import APIRouter

router = APIRouter(tags=["Export"])


@router.get("/api/export/csv", summary="Export dataset as CSV")
def export_csv(dataset: str = "nc_trends", months: int = 6, project_id: str = ""):
    from app.services.report_generator import generate_csv
    csv_text = generate_csv(dataset, months=months, project_id=project_id)
    filename_map = {
        "nc_trends": "nc_trends.csv",
        "project_health": "project_health.csv",
        "capa_metrics": "capa_metrics.csv",
        "ai_usage": "ai_usage.csv",
    }
    filename = filename_map.get(dataset, "export.csv")
    from starlette.responses import Response
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/api/export/report", summary="Generate PDF summary report")
def export_report(report_type: str = "compliance_summary", project_id: str = ""):
    from app.services.report_generator import generate_compliance_summary, generate_project_overview

    if report_type == "project_overview":
        pdf_bytes = generate_project_overview(project_id=project_id)
        filename = "project_overview.pdf"
    else:
        pdf_bytes = generate_compliance_summary()
        filename = "compliance_summary.pdf"

    from starlette.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
