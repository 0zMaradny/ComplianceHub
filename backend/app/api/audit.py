"""Audit Workflow API Router.

Provides CRUD endpoints for audit projects, evidence, NCs, and CAPA.
All data persisted as JSON files (no database dependency).
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models import (
    AuditProject, Evidence, Nonconformity, CAPA,
    create_project, get_project, list_projects, update_project, delete_project,
    create_evidence, list_evidence, update_evidence,
    create_nc, list_ncs, update_nc,
    create_capa, list_capa, update_capa,
    get_project_stats, DATA_DIR,
)
from app.services.client_config import get_client

router = APIRouter(prefix="/api/audit", tags=["audit-workflow"])

EVIDENCE_DIR = os.path.join(DATA_DIR, "evidence_files")
os.makedirs(EVIDENCE_DIR, exist_ok=True)


# ── Project CRUD ──────────────────────────────────────────────────────────

@router.post("/projects")
def create_audit_project(
    client_key: str = Form(""),
    title: str = Form(""),
    standards: str = Form("[]"),
    lead_auditor: str = Form(""),
    scope: str = Form(""),
    audit_date: str = Form(""),
):
    """Create a new audit project."""
    if not client_key:
        raise HTTPException(status_code=400, detail="client_key is required")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    client = get_client(client_key)
    if not client:
        raise HTTPException(status_code=404, detail=f"Client not found: {client_key}")

    import json as _json
    project = AuditProject(
        client_key=client_key,
        title=title,
        standards=_json.loads(standards),
        lead_auditor=lead_auditor,
        scope=scope,
        audit_date=audit_date,
    )
    created = create_project(project)
    return {"success": True, "project": created.__dict__}


@router.get("/projects")
def get_projects(client_key: str = ""):
    """List audit projects, optionally filtered by client."""
    projects = list_projects(client_key if client_key else None)
    return {"projects": [p.__dict__ for p in projects]}


@router.get("/projects/{project_id}")
def get_project_detail(project_id: str):
    """Get full project detail with stats."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    stats = get_project_stats(project_id)
    evidence = list_evidence(project_id)
    ncs = list_ncs(project_id)
    capas = list_capa(project_id)

    return {
        "project": project.__dict__,
        "stats": stats,
        "evidence": [e.__dict__ for e in evidence],
        "nonconformities": [n.__dict__ for n in ncs],
        "capa": [c.__dict__ for c in capas],
    }


@router.put("/projects/{project_id}")
def update_audit_project(
    project_id: str,
    title: str = Form(""),
    status: str = Form(""),
    lead_auditor: str = Form(""),
    scope: str = Form(""),
    audit_date: str = Form(""),
):
    """Update project fields."""
    kwargs = {k: v for k, v in locals().items() if k not in ("project_id", "") and v}
    project = update_project(project_id, **kwargs)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project": project.__dict__}


@router.delete("/projects/{project_id}")
def delete_audit_project(project_id: str):
    """Delete a project and all associated data."""
    if delete_project(project_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Project not found")


# ── Gate Management ───────────────────────────────────────────────────────

@router.put("/projects/{project_id}/gates/{gate_name}")
def update_gate(project_id: str, gate_name: str, status: str = Form(...)):
    """Update a gate status (pending → in_progress → complete)."""
    valid_gates = ["G1_Scope", "G2_GapAnalysis", "G3_RiskRegister", "G4_Implementation", "G5_InternalAudit", "G6_Certification"]
    if gate_name not in valid_gates:
        raise HTTPException(status_code=400, detail=f"Invalid gate. Valid: {valid_gates}")

    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    gates = dict(project.gates)
    gates[gate_name] = status
    update_project(project_id, gates=gates)

    return {"success": True, "gates": gates}


# ── Evidence Management ────────────────────────────────────────────────────

@router.post("/projects/{project_id}/evidence")
def upload_evidence(
    project_id: str,
    clause: str = Form(""),
    standard: str = Form(""),
    uploaded_by: str = Form(""),
    file: UploadFile = File(...),
):
    """Upload evidence file for a project."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Save file
    safe_name = f"{project_id}_{clause.replace('.', '_')}_{file.filename}"
    file_path = os.path.join(EVIDENCE_DIR, safe_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    evidence = Evidence(
        project_id=project_id,
        clause=clause,
        standard=standard,
        file_name=file.filename,
        file_path=file_path,
        uploaded_by=uploaded_by,
    )
    created = create_evidence(evidence)
    return {"success": True, "evidence": created.__dict__}


@router.get("/projects/{project_id}/evidence")
def get_evidence(project_id: str):
    """List all evidence for a project."""
    evidence = list_evidence(project_id)
    return {"evidence": [e.__dict__ for e in evidence]}


@router.put("/evidence/{evidence_id}")
def review_evidence(
    evidence_id: str,
    status: str = Form(""),
    reviewer_notes: str = Form(""),
):
    """Review evidence (accept/reject with notes)."""
    kwargs = {k: v for k, v in locals().items() if k not in ("evidence_id", "") and v}
    ev = update_evidence(evidence_id, **kwargs)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {"success": True, "evidence": ev.__dict__}


# ── Nonconformity Management ──────────────────────────────────────────────

@router.post("/projects/{project_id}/ncs")
def create_nonconformity(
    project_id: str,
    clause: str = Form(""),
    severity: str = Form("Minor"),
    description: str = Form(""),
    evidence_ref: str = Form(""),
    due_date: str = Form(""),
):
    """Create a new nonconformity."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    nc = Nonconformity(
        project_id=project_id,
        clause=clause,
        severity=severity,
        description=description,
        evidence_ref=evidence_ref,
        due_date=due_date,
    )
    created = create_nc(nc)
    return {"success": True, "nc": created.__dict__}


@router.get("/projects/{project_id}/ncs")
def get_ncs(project_id: str):
    """List all NCs for a project."""
    ncs = list_ncs(project_id)
    return {"nonconformities": [n.__dict__ for n in ncs]}


@router.put("/ncs/{nc_id}")
def update_nonconformity(
    nc_id: str,
    status: str = Form(""),
    root_cause: str = Form(""),
    containment_action: str = Form(""),
    corrective_action: str = Form(""),
    preventive_action: str = Form(""),
    effectiveness_verification: str = Form(""),
    closed_date: str = Form(""),
):
    """Update NC fields (status, root cause, actions, etc.)."""
    kwargs = {k: v for k, v in locals().items() if k not in ("nc_id", "") and v}
    nc = update_nc(nc_id, **kwargs)
    if not nc:
        raise HTTPException(status_code=404, detail="NC not found")
    return {"success": True, "nc": nc.__dict__}


# ── CAPA Management ───────────────────────────────────────────────────────

@router.post("/projects/{project_id}/capa")
def create_capa_entry(
    project_id: str,
    nc_id: str = Form(""),
    type: str = Form("corrective"),
    description: str = Form(""),
    root_cause: str = Form(""),
    action: str = Form(""),
    owner: str = Form(""),
    due_date: str = Form(""),
):
    """Create a CAPA entry."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    capa = CAPA(
        project_id=project_id,
        nc_id=nc_id,
        type=type,
        description=description,
        root_cause=root_cause,
        action=action,
        owner=owner,
        due_date=due_date,
    )
    created = create_capa(capa)
    return {"success": True, "capa": created.__dict__}


@router.get("/projects/{project_id}/capa")
def get_capa(project_id: str):
    """List all CAPA entries for a project."""
    capas = list_capa(project_id)
    return {"capa": [c.__dict__ for c in capas]}


@router.put("/capa/{capa_id}")
def update_capa_entry(
    capa_id: str,
    status: str = Form(""),
    description: str = Form(""),
    action: str = Form(""),
    verification_notes: str = Form(""),
):
    """Update CAPA fields."""
    kwargs = {k: v for k, v in locals().items() if k not in ("capa_id", "") and v}
    capa = update_capa(capa_id, **kwargs)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return {"success": True, "capa": capa.__dict__}


# ── Dashboard Stats ───────────────────────────────────────────────────────

@router.get("/dashboard")
def get_dashboard(client_key: str = ""):
    """Get dashboard statistics across all projects."""
    projects = list_projects(client_key if client_key else None)

    total_projects = len(projects)
    active_projects = len([p for p in projects if p.status == "active"])
    draft_projects = len([p for p in projects if p.status == "draft"])
    closed_projects = len([p for p in projects if p.status == "closed"])

    all_ncs = []
    all_evidence = []
    for p in projects:
        all_ncs.extend(list_ncs(p.id))
        all_evidence.extend(list_evidence(p.id))

    return {
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "draft": draft_projects,
            "closed": closed_projects,
        },
        "nonconformities": {
            "total": len(all_ncs),
            "open": len([n for n in all_ncs if n.status not in ("closed", "verified")]),
            "major": len([n for n in all_ncs if n.severity == "Major"]),
            "minor": len([n for n in all_ncs if n.severity == "Minor"]),
        },
        "evidence": {
            "total": len(all_evidence),
            "pending": len([e for e in all_evidence if e.status == "pending"]),
            "accepted": len([e for e in all_evidence if e.status == "accepted"]),
        },
        "recent_projects": [p.__dict__ for p in projects[:5]],
    }
