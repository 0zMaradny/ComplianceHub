from fastapi import APIRouter, HTTPException, Form
import json

from app.services.audit_workflow import (
    create_project, get_project, list_projects, update_project, delete_project,
    advance_gate, set_gate, get_project_progress,
    create_nc, list_ncs, update_nc,
    create_capa, list_capas, update_capa,
    create_evidence, list_evidence, update_evidence,
    GATES,
)

router = APIRouter(tags=["Audit Workflow"])


@router.post("/api/projects", summary="Create audit project",
             description="Create a new audit project for a client with specified standards and target date.")
def create_audit_project(
    client_key: str = Form(""),
    title: str = Form(""),
    standards: str = Form("[]"),
    target_date: str = Form(""),
    lead_auditor: str = Form(""),
    notes: str = Form(""),
):
    if not client_key or not title:
        raise HTTPException(status_code=400, detail="client_key and title are required")
    stds = json.loads(standards) if standards else []
    project = create_project(client_key, title, stds, target_date, lead_auditor, notes)
    return {"success": True, "project": project.to_dict()}


@router.get("/api/projects")
def list_audit_projects(client_key: str = "", status: str = ""):
    projects = list_projects(
        client_key=client_key or None,
        status=status or None,
    )
    return {"projects": [p.to_dict() for p in projects]}


@router.get("/api/projects/{project_id}")
def get_audit_project(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()


@router.get("/api/projects/{project_id}/progress")
def get_audit_progress(project_id: str):
    progress = get_project_progress(project_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Project not found")
    return progress


@router.put("/api/projects/{project_id}")
def update_audit_project(project_id: str, **kwargs):
    project = update_project(project_id, **kwargs)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()


@router.delete("/api/projects/{project_id}")
def delete_audit_project(project_id: str):
    if delete_project(project_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Project not found")


@router.post("/api/projects/{project_id}/advance")
def advance_audit_project(project_id: str):
    if advance_gate(project_id):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Cannot advance gate")


@router.post("/api/projects/{project_id}/gate/{gate_num}")
def set_audit_gate(project_id: str, gate_num: int):
    if set_gate(project_id, gate_num):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Invalid gate number")


@router.get("/api/gates")
def list_gates():
    return {"gates": [g.to_dict() for g in GATES]}


@router.post("/api/projects/{project_id}/ncs")
def create_nonconformity(project_id: str, nc_data: dict):
    nc = create_nc(project_id, nc_data)
    return {"success": True, "nc": nc.to_dict()}


@router.get("/api/projects/{project_id}/ncs")
def list_nonconformities(project_id: str):
    ncs = list_ncs(project_id)
    return {"ncs": [n.to_dict() for n in ncs]}


@router.put("/api/ncs/{nc_id}")
def update_nonconformity(nc_id: str, nc_data: dict):
    nc = update_nc(nc_id, nc_data)
    if not nc:
        raise HTTPException(status_code=404, detail="NC not found")
    return {"success": True, "nc": nc.to_dict()}


@router.post("/api/projects/{project_id}/capas")
def create_corrective_action(project_id: str, capa_data: dict):
    capa = create_capa(project_id, capa_data)
    return {"success": True, "capa": capa.to_dict()}


@router.get("/api/projects/{project_id}/capas")
def list_corrective_actions(project_id: str):
    capas = list_capas(project_id)
    return {"capas": [c.to_dict() for c in capas]}


@router.put("/api/capas/{capa_id}")
def update_corrective_action(capa_id: str, capa_data: dict):
    capa = update_capa(capa_id, capa_data)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return {"success": True, "capa": capa.to_dict()}


@router.post("/api/projects/{project_id}/evidence")
def create_evidence_item(project_id: str, evidence_data: dict):
    ev = create_evidence(project_id, evidence_data)
    return {"success": True, "evidence": ev.to_dict()}


@router.get("/api/projects/{project_id}/evidence")
def list_evidence_items(project_id: str):
    items = list_evidence(project_id)
    return {"evidence": [e.to_dict() for e in items]}


@router.put("/api/evidence/{evidence_id}")
def update_evidence_item(evidence_id: str, evidence_data: dict):
    ev = update_evidence(evidence_id, evidence_data)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"success": True, "evidence": ev.to_dict()}
