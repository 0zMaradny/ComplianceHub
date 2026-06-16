import os
import json
from fastapi import APIRouter, HTTPException, Form, UploadFile, File

from app.services.audit_program import (
    create_program, list_programs, update_program, delete_program,
    create_entry, list_entries, update_entry, delete_entry,
    build_checklist_for_program, list_checklist,
    list_checklist_by_day, update_checklist_item, bulk_update_checklist,
    add_evidence, list_evidence_register, update_evidence_entry, delete_evidence_entry,
    get_or_create_daily_summary, update_daily_summary, list_daily_summaries,
    get_program_overview, get_checklist_export,
)

router = APIRouter(tags=["Audit Execution"])


@router.post("/api/audit_programs", summary="Create audit program")
def create_audit_program(
    title: str = Form(""),
    client_name: str = Form(""),
    client_key: str = Form(""),
    standards: str = Form("[]"),
    audit_type: str = Form("stage2"),
    lead_auditor: str = Form(""),
    audit_team: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    location: str = Form(""),
    notes: str = Form(""),
):
    if not title or not client_name or not start_date or not end_date:
        raise HTTPException(status_code=400, detail="title, client_name, start_date, end_date are required")
    stds = json.loads(standards) if standards else []
    team = [t.strip() for t in audit_team.split(",") if t.strip()] if audit_team else []
    program = create_program(
        title=title, client_name=client_name, client_key=client_key,
        standards=stds, audit_type=audit_type, lead_auditor=lead_auditor,
        audit_team=team, start_date=start_date, end_date=end_date,
        location=location, notes=notes,
    )
    return {"success": True, "program": program.to_dict()}


@router.get("/api/audit_programs", summary="List audit programs")
def list_audit_programs(client_key: str = "", status: str = ""):
    programs = list_programs(client_key=client_key or None, status=status or None)
    return {"programs": [p.to_dict() for p in programs]}


@router.get("/api/audit_programs/{program_id}", summary="Get audit program overview")
def get_audit_program_overview(program_id: str):
    overview = get_program_overview(program_id)
    if not overview:
        raise HTTPException(status_code=404, detail="Program not found")
    return overview


@router.put("/api/audit_programs/{program_id}", summary="Update audit program")
def update_audit_program_endpoint(program_id: str, **kwargs):
    if "standards" in kwargs and isinstance(kwargs["standards"], str):
        kwargs["standards"] = json.loads(kwargs["standards"])
    if "audit_team" in kwargs and isinstance(kwargs["audit_team"], str):
        kwargs["audit_team"] = [t.strip() for t in kwargs["audit_team"].split(",") if t.strip()]
    program = update_program(program_id, **kwargs)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program.to_dict()


@router.delete("/api/audit_programs/{program_id}", summary="Delete audit program")
def delete_audit_program(program_id: str):
    if delete_program(program_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Program not found")


@router.post("/api/audit_programs/{program_id}/entries", summary="Add program entry")
def create_program_entry(
    program_id: str,
    day: int = Form(0),
    date: str = Form(""),
    start_time: str = Form(""),
    end_time: str = Form(""),
    department: str = Form(""),
    auditor: str = Form(""),
    clause_refs: str = Form("[]"),
    standard: str = Form(""),
    description: str = Form(""),
    room: str = Form(""),
):
    if not day or not start_time or not end_time or not department:
        raise HTTPException(status_code=400, detail="day, start_time, end_time, department are required")
    refs = json.loads(clause_refs) if clause_refs else []
    entry = create_entry(
        program_id=program_id, day=day, date=date,
        start_time=start_time, end_time=end_time,
        department=department, auditor=auditor,
        clause_refs=refs, standard=standard,
        description=description, room=room,
    )
    return entry.to_dict()


@router.get("/api/audit_programs/{program_id}/entries", summary="List program entries")
def list_program_entries(program_id: str, day: int = 0):
    day_val = day if day > 0 else None
    entries = list_entries(program_id, day=day_val)
    return {"entries": [e.to_dict() for e in entries]}


@router.put("/api/entries/{entry_id}", summary="Update program entry")
def update_program_entry_endpoint(entry_id: str, **kwargs):
    if "clause_refs" in kwargs and isinstance(kwargs["clause_refs"], str):
        kwargs["clause_refs"] = json.loads(kwargs["clause_refs"])
    entry = update_entry(entry_id, **kwargs)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.to_dict()


@router.delete("/api/entries/{entry_id}", summary="Delete program entry")
def delete_program_entry(entry_id: str):
    delete_entry(entry_id)
    return {"success": True}


@router.post("/api/audit_programs/{program_id}/checklist/build", summary="Build checklist from standards")
def build_program_checklist(program_id: str):
    items = build_checklist_for_program(program_id)
    return {"success": True, "total": len(items), "items": [i.to_dict() for i in items]}


@router.get("/api/audit_programs/{program_id}/checklist", summary="Get clause checklist")
def get_program_checklist(
    program_id: str,
    standard: str = "",
    status: str = "",
    day: int = 0,
):
    if day > 0:
        items = list_checklist_by_day(program_id, day)
    else:
        items = list_checklist(
            program_id,
            standard=standard or None,
            status=status or None,
        )
    return {"checklist": [i.to_dict() for i in items], "total": len(items)}


@router.get("/api/audit_programs/{program_id}/checklist/export", summary="Export checklist grouped by standard")
def export_program_checklist(program_id: str):
    grouped = get_checklist_export(program_id)
    return {"standards": grouped}


@router.put("/api/checklist/{item_id}", summary="Update checklist item")
def update_checklist_item_endpoint(item_id: str, **kwargs):
    item = update_checklist_item(item_id, **kwargs)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return item.to_dict()


@router.post("/api/audit_programs/{program_id}/checklist/bulk", summary="Bulk update checklist")
def bulk_update_checklist_endpoint(program_id: str, updates: dict = None):
    if not updates:
        raise HTTPException(status_code=400, detail="updates dict required")
    results = bulk_update_checklist(program_id, updates)
    return {"updated": len(results), "items": [i.to_dict() for i in results]}


@router.post("/api/audit_programs/{program_id}/evidence", summary="Add evidence")
async def add_evidence_endpoint(
    program_id: str,
    clause_ref: str = Form(""),
    standard: str = Form(""),
    evidence_type: str = Form("document"),
    description: str = Form(""),
    collected_by: str = Form(""),
    file: UploadFile = File(None),
):
    file_path = ""
    if file and file.filename:
        evidence_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'audit_program_evidence')
        os.makedirs(evidence_dir, exist_ok=True)
        safe_name = f"{program_id}_{int(__import__('time').time())}_{file.filename}"
        dest = os.path.join(evidence_dir, safe_name)
        content = await file.read()
        with open(dest, "wb") as f:
            f.write(content)
        file_path = dest
    ev = add_evidence(
        program_id=program_id, clause_ref=clause_ref,
        standard=standard, evidence_type=evidence_type,
        description=description, collected_by=collected_by,
        file_path=file_path,
    )
    return ev.to_dict()


@router.get("/api/audit_programs/{program_id}/evidence", summary="List evidence")
def list_evidence_endpoint(program_id: str, clause_ref: str = "", standard: str = ""):
    items = list_evidence_register(
        program_id,
        clause_ref=clause_ref or None,
        standard=standard or None,
    )
    return {"evidence": [e.to_dict() for e in items], "total": len(items)}


@router.put("/api/evidence/{evidence_id}", summary="Update evidence entry")
def update_evidence_endpoint(evidence_id: str, **kwargs):
    ev = update_evidence_entry(evidence_id, **kwargs)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return ev.to_dict()


@router.delete("/api/evidence/{evidence_id}", summary="Delete evidence entry")
def delete_evidence_endpoint(evidence_id: str):
    delete_evidence_entry(evidence_id)
    return {"success": True}


@router.get("/api/audit_programs/{program_id}/daily/{day}", summary="Get daily summary")
def get_daily_summary(program_id: str, day: int, date: str = ""):
    ds = get_or_create_daily_summary(program_id, day, date)
    return ds.to_dict()


@router.put("/api/daily_summaries/{summary_id}", summary="Update daily summary")
def update_daily_summary_endpoint(summary_id: str, **kwargs):
    ds = update_daily_summary(summary_id, **kwargs)
    if not ds:
        raise HTTPException(status_code=404, detail="Summary not found")
    return ds.to_dict()


@router.get("/api/audit_programs/{program_id}/daily", summary="List daily summaries")
def list_daily_summaries_endpoint(program_id: str):
    items = list_daily_summaries(program_id)
    return {"summaries": [s.to_dict() for s in items]}
