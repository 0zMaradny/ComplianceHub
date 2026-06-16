from fastapi import APIRouter, HTTPException, Form

from app.services.surveillance import (
    create_surveillance_cycle, get_surveillance_cycle,
    list_surveillance_cycles, update_surveillance_cycle,
    generate_surveillance_scope,
    create_surveillance_finding,
    list_surveillance_findings,
    get_surveillance_dashboard_stats,
    auto_schedule_surveillance, check_overdue_cycles,
)

router = APIRouter(tags=["Surveillance"])


@router.post("/api/surveillance/cycles", summary="Create surveillance cycle")
def create_cycle(
    project_id: str = Form(""),
    cycle_number: str = Form(""),
    scheduled_date: str = Form(""),
    notes: str = Form(""),
):
    if not project_id or not cycle_number or not scheduled_date:
        raise HTTPException(status_code=400, detail="project_id, cycle_number, and scheduled_date are required")
    num = int(cycle_number) if cycle_number.isdigit() else cycle_number
    if num not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="cycle_number must be 1, 2, or 3")
    cycle = create_surveillance_cycle(project_id, num, scheduled_date, notes)
    return {"success": True, "cycle": cycle.to_dict()}


@router.get("/api/surveillance/cycles", summary="List surveillance cycles")
def list_cycles(project_id: str = ""):
    cycles = list_surveillance_cycles(project_id=project_id or None)
    return {"cycles": [c.to_dict() for c in cycles]}


@router.get("/api/surveillance/cycles/{cycle_id}", summary="Get surveillance cycle")
def get_cycle(cycle_id: str):
    cycle = get_surveillance_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle.to_dict()


@router.put("/api/surveillance/cycles/{cycle_id}", summary="Update surveillance cycle")
def update_cycle(cycle_id: str, cycle_data: dict):
    cycle = update_surveillance_cycle(cycle_id, **cycle_data)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle.to_dict()


@router.post("/api/surveillance/cycles/{cycle_id}/scope", summary="Generate surveillance scope")
def generate_scope(cycle_id: str):
    cycle = get_surveillance_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    result = generate_surveillance_scope(cycle.project_id, cycle_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/api/surveillance/cycles/{cycle_id}/findings", summary="Add surveillance finding")
def add_finding(
    cycle_id: str,
    clause: str = Form(...),
    finding_type: str = Form(...),
    severity: str = Form(...),
    description: str = Form(...),
    previous_nc_id: str = Form(""),
):
    finding = create_surveillance_finding(cycle_id, clause, finding_type, severity, description, previous_nc_id or None)
    return finding.to_dict()


@router.get("/api/surveillance/cycles/{cycle_id}/findings", summary="List cycle findings")
def list_findings(cycle_id: str):
    findings = list_surveillance_findings(cycle_id=cycle_id)
    return {"findings": [f.to_dict() for f in findings]}


@router.post("/api/projects/{project_id}/auto-schedule", summary="Auto-schedule surveillance cycles")
def auto_schedule(project_id: str, cert_date: str = ""):
    if not cert_date:
        raise HTTPException(status_code=400, detail="cert_date is required")
    cycles = auto_schedule_surveillance(project_id, cert_date)
    return {"cycles": [c.to_dict() for c in cycles]}


@router.get("/api/surveillance/dashboard", summary="Surveillance dashboard stats")
def dashboard():
    stats = get_surveillance_dashboard_stats()
    return stats


@router.post("/api/surveillance/check-overdue", summary="Check overdue cycles")
def check_overdue():
    overdue = check_overdue_cycles()
    return {"newly_overdue": [c.to_dict() for c in overdue]}
