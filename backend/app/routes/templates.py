import json
import os
from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse
from datetime import datetime, timedelta

from app.utils import sanitize_filename
from app.config import OUTPUT_FOLDER
from app.services.document_generator import generate_audit_plan_stage

router = APIRouter(tags=["Templates", "Audit Plan"])

from app.services.template_manager import get_checklist_is_excel
from app.services.template_manager import TEMPLATE_MAP as DOC_TEMPLATES
from app.services.template_manager import CHECKLIST_TEMPLATES, TEMPLATES_DIR


@router.get("/api/templates")
def list_templates():
    doc_templates = []
    for doc_type, fname in DOC_TEMPLATES.items():
        path = os.path.join(TEMPLATES_DIR, fname)
        doc_templates.append({
            'doc_type': doc_type,
            'filename': fname,
            'path': path,
            'exists': os.path.exists(path),
            'type': 'document',
        })

    checklist_templates = []
    for std_key, fname in CHECKLIST_TEMPLATES.items():
        path = os.path.join(TEMPLATES_DIR, fname)
        is_excel = get_checklist_is_excel(std_key)
        checklist_templates.append({
            'standard_key': std_key,
            'filename': fname,
            'path': path,
            'exists': os.path.exists(path),
            'is_excel': is_excel,
            'type': 'checklist',
        })

    all_files = []
    if os.path.exists(TEMPLATES_DIR):
        for f in sorted(os.listdir(TEMPLATES_DIR)):
            fpath = os.path.join(TEMPLATES_DIR, f)
            if os.path.isfile(fpath):
                all_files.append(f)

    unused = [f for f in all_files if f not in list(DOC_TEMPLATES.values()) + list(CHECKLIST_TEMPLATES.values())]

    return {
        'document_templates': doc_templates,
        'checklist_templates': checklist_templates,
        'unused_files': unused,
        'template_dir': TEMPLATES_DIR,
        'count': {
            'document': len(doc_templates),
            'checklist': len(checklist_templates),
            'unused': len(unused),
        },
    }


@router.post("/api/templates/upload")
async def upload_template(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail='No filename provided')
    fname = sanitize_filename(file.filename)
    if not (fname.endswith('.docx') or fname.endswith('.xlsx') or fname.endswith('.doc')):
        raise HTTPException(status_code=400, detail='Only .docx, .xlsx, and .doc files are allowed')
    dest = os.path.join(TEMPLATES_DIR, fname)
    if os.path.exists(dest):
        raise HTTPException(status_code=409, detail=f'Template "{fname}" already exists')
    content = await file.read()
    with open(dest, 'wb') as f:
        f.write(content)
    return {'success': True, 'filename': fname, 'size': len(content)}


@router.delete("/api/templates/{filename:path}")
def delete_template(filename: str):
    fname = sanitize_filename(filename)
    path = os.path.join(TEMPLATES_DIR, fname)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f'Template "{fname}" not found')
    os.remove(path)
    return {'success': True, 'filename': fname}


@router.post("/api/audit_plan/generate", summary="Generate standalone Audit Plan",
             tags=["Audit Plan"])
def generate_audit_plan(
    client_name: str = Form(""),
    client_key: str = Form(""),
    standards: str = Form("[]"),
    audit_type: str = Form("stage2"),
    lead_auditor: str = Form(""),
    audit_team: str = Form(""),
    start_date: str = Form(""),
    end_date: str = Form(""),
    location: str = Form(""),
    audit_scope: str = Form(""),
    audit_language: str = Form("English"),
    report_due_days: int = Form(30),
    daily_schedule: str = Form("[]"),
    notes: str = Form(""),
):
    if not client_name or not start_date or not end_date:
        raise HTTPException(status_code=400, detail="client_name, start_date, end_date are required")

    stds = json.loads(standards) if standards else []
    team_names = [t.strip() for t in audit_team.split(",") if t.strip()] if audit_team else []
    schedule = json.loads(daily_schedule) if daily_schedule else []

    from app.config import ISO_STANDARDS
    std_labels = [ISO_STANDARDS.get(s, s) for s in stds]
    standard_label = " / ".join(std_labels) if std_labels else "ISO Standard"

    stage_map = {
        "stage1": "Stage 1 — Readiness Review",
        "stage2": "Stage 2 — Certification Audit",
        "surveillance": "Surveillance Audit",
        "recertification": "Recertification Audit",
        "transfer": "Transfer Audit",
    }
    stage_label = stage_map.get(audit_type, "Stage 2 — Certification Audit")

    team_data = []
    for i, name in enumerate(team_names):
        role = "Lead Auditor" if i == 0 else "Auditor"
        team_data.append({"name": name, "role": role, "days": ""})

    if not schedule:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            ed = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = (ed - sd).days + 1
            for d in range(num_days):
                day_date = sd + timedelta(days=d)
                schedule.append({
                    "day": d + 1,
                    "date": day_date.strftime("%d/%m/%Y"),
                    "time": "09:00 – 17:00",
                    "activity": "Audit activities per audit programme",
                    "auditee": "",
                    "auditor": team_names[0] if team_names else "",
                    "clause": "",
                })
        except Exception:
            schedule = [{"day": 1, "date": start_date, "time": "09:00 – 17:00",
                         "activity": "Audit activities", "auditee": "",
                         "auditor": team_names[0] if team_names else "", "clause": ""}]

    report_due = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=report_due_days)).strftime("%d/%m/%Y")

    plan_data = {
        "client_name": client_name,
        "standard": standard_label,
        "standard_key": stds[0] if stds else "iso_9001",
        "audit_date": start_date,
        "stage": stage_label,
        "audit_team": team_data,
        "audit_scope": audit_scope or f"The audit covers the management system at {client_name} against {standard_label} requirements.",
        "audit_objectives": [
            f"Evaluate the management system conformity with {standard_label} requirements",
            "Assess the effectiveness of implemented processes in achieving planned outcomes",
            "Verify conformity with applicable statutory and regulatory requirements",
            "Evaluate personnel competence and awareness of relevant policies and procedures",
            "Assess internal audit process and management review outputs",
            "Identify opportunities for improvement in the management system",
        ],
        "audit_criteria": [standard_label] + [
            "Management system documented policies, procedures, and work instructions",
            "Applicable statutory and regulatory requirements",
        ],
        "daily_schedule": schedule,
        "confidentiality": "All information obtained during this audit shall be treated as strictly confidential and used solely for the purpose of certification.",
        "language": audit_language,
        "report_date": report_due,
        "location": location,
        "notes": notes,
    }

    output_dir = os.path.join(OUTPUT_FOLDER, 'audit_plans')
    os.makedirs(output_dir, exist_ok=True)
    safe_name = sanitize_filename(f"{client_name}_{audit_type}")
    output_path = os.path.join(output_dir, f"TUV_Audit_Plan_{safe_name}.docx")

    try:
        generate_audit_plan_stage(plan_data, output_path, stage_label, client_key=client_key or None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit Plan generation failed: {str(e)}")

    return FileResponse(
        output_path,
        filename=f"TUV_Audit_Plan_{safe_name}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
