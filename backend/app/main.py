import os
import json
import zipfile
import uuid
import shutil
import threading
import time
from collections import defaultdict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    UPLOAD_FOLDER, OUTPUT_FOLDER, ISO_STANDARDS,
    OUTPUT_DOCUMENTS, DOC_LABELS, STANDARD_CATEGORIES
)
from app.utils import sanitize_filename, validate_job_id
from app.services.client_config import get_client, list_clients, get_doc_code, validate_client_data
from app.services.file_parser import extract_audit_notes, extract_manday_data
from app.services.ai_pipeline import generate_document as ai_generate, extract_shared_context
from app.services.document_generator import generate_document_file
from app.services.pdf_converter import convert_to_pdf
from app.services.offline_generator import generate_all as offline_generate_all
from app.api.audit import router as audit_router

app = FastAPI(title="ComplianceHub API", version="2.0.0")

# ── CORS: configurable via env var ───────────────────────────────────────
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
if CORS_ORIGINS == "*":
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit_router)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ── Thread-safe progress store ───────────────────────────────────────────
progress_store: dict = {}
_progress_lock = threading.Lock()
MAX_JOB_AGE = 3600

# ── Rate limiting (simple in-memory) ─────────────────────────────────────
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = threading.Lock()
RATE_LIMIT_WINDOW = 60       # seconds
RATE_LIMIT_MAX_REQUESTS = 30  # per window per client
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _check_rate_limit(client_id: str) -> bool:
    """Return True if request is allowed, False if rate-limited."""
    now = time.time()
    with _rate_limit_lock:
        timestamps = _rate_limit_store[client_id]
        # Prune old entries
        _rate_limit_store[client_id] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_limit_store[client_id]) >= RATE_LIMIT_MAX_REQUESTS:
            return False
        _rate_limit_store[client_id].append(now)
        return True


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all API endpoints."""
    if request.url.path.startswith("/api/"):
        client_id = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_id):
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Try again later."},
            )
    return await call_next(request)


def _update_progress(job_id: str, **kwargs):
    """Thread-safe progress store update."""
    with _progress_lock:
        if job_id in progress_store:
            progress_store[job_id].update(kwargs)


def _get_progress(job_id: str) -> dict | None:
    """Thread-safe progress store read."""
    with _progress_lock:
        return progress_store.get(job_id)


def cleanup_old_jobs():
    now = time.time()
    with _progress_lock:
        for jid in list(progress_store.keys()):
            entry = progress_store.get(jid)
            if entry and (now - entry.get('created_at', 0)) > MAX_JOB_AGE:
                del progress_store[jid]
                for d in [os.path.join(UPLOAD_FOLDER, jid), os.path.join(OUTPUT_FOLDER, jid)]:
                    shutil.rmtree(d, ignore_errors=True)


def _make_doc_result(output_dir, template_path, standard_key, doc_type, doc_data, client_key=None):
    """Generate a DOCX file from data, return doc_info dict or None."""
    path = generate_document_file(doc_type, doc_data, output_dir, template_path, standard_key, client_key=client_key)
    if not path:
        return None
    filename = os.path.basename(path)
    doc_info = {'path': path, 'filename': filename}
    pdf_path = convert_to_pdf(path)
    if pdf_path:
        doc_info['pdf_path'] = pdf_path
    for k in ('certification_decision', 'conditions', 'findings_summary',
              'conclusion', 'methodology', 'sections', 'summary',
              'client_name', 'audit_date', 'standard', 'scope', 'lead_auditor',
              'report_number', 'certificate_number', 'nonconformities',
              'positive_findings', 'opportunities_for_improvement'):
        if k in doc_data:
            doc_info[k] = doc_data[k]
    return doc_info


def generate_background(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key=None):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(output_dir, exist_ok=True)

    template_path = os.path.join(job_dir, 'checklist_template.docx')
    if not os.path.exists(template_path):
        template_path = None

    standard_key = selected_standards[0] if selected_standards else None
    notes_text = notes_data['text']
    manday_text = manday_data['text']

    _update_progress(job_id, status='extracting_context', progress=10, current_doc='Analyzing documents...')

    shared_context = None
    if api_key and api_key.strip().lower() not in ('', 'local'):
        shared_context = extract_shared_context(api_key, notes_text, manday_text)
        if 'error' in shared_context:
            shared_context = None

    results = {}
    total = len(OUTPUT_DOCUMENTS)
    client_name = 'Client'

    for idx, doc_type in enumerate(OUTPUT_DOCUMENTS):
        label = DOC_LABELS.get(doc_type, doc_type)
        _update_progress(job_id, status='generating', current_doc=label)
        # Set doc_progress entry
        with _progress_lock:
            if job_id in progress_store:
                progress_store[job_id]['doc_progress'][doc_type] = 'generating'
        base_progress = 20 + int((idx / total) * 70)
        _update_progress(job_id, progress=base_progress)

        # 1) Try AI pipeline (router → local/cloud provider)
        doc_data = None
        ai_error = None
        if True:
            try:
                ai_result = ai_generate(
                    api_key, notes_text, manday_text,
                    standards_full, doc_type, shared_context,
                    client_key=client_key
                )
                if 'error' not in ai_result:
                    doc_data = ai_result
                else:
                    ai_error = ai_result['error']
            except Exception as e:
                ai_error = str(e)

        # 2) If AI failed, fall back to offline generator
        if doc_data is None:
            offline_results = offline_generate_all(
                notes_text, manday_text,
                standards_full, selected_standards
            )
            doc_data = offline_results.get(doc_type, {})
            if 'error' in doc_data:
                ai_error = ai_error or doc_data['error']
                doc_data = None

        # 3) Generate the DOCX from whatever data we have
        if doc_data:
            # Inject client_key into doc_data so generators can use it
            if client_key:
                doc_data['client_key'] = client_key
            doc_info = _make_doc_result(output_dir, template_path, standard_key, doc_type, doc_data, client_key=client_key)
            if doc_info:
                if not client_name or client_name == 'Client':
                    client_name = doc_data.get('client_name', 'Client')
                doc_info['_data'] = doc_data
                results[doc_type] = doc_info
                with _progress_lock:
                    if job_id in progress_store:
                        progress_store[job_id]['doc_progress'][doc_type] = 'done'
                _update_progress(job_id, progress=20 + int(((idx + 1) / total) * 70))
                continue

        results[doc_type] = {'error': ai_error or 'Document generation failed'}
        with _progress_lock:
            if job_id in progress_store:
                progress_store[job_id]['doc_progress'][doc_type] = 'error'
        _update_progress(job_id, progress=20 + int(((idx + 1) / total) * 70))

    _update_progress(job_id, progress=95, current_doc='Creating package...')

    safe_name = sanitize_filename(client_name)
    zip_name = f'TUV_Audit_Package_{safe_name}.zip'
    zip_path = os.path.join(OUTPUT_FOLDER, f'{job_id}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for doc_type, result in results.items():
            if 'path' in result and os.path.exists(result['path']):
                zf.write(result['path'], result.get('filename', os.path.basename(result['path'])))
            if 'pdf_path' in result and os.path.exists(result['pdf_path']):
                pdf_filename = result.get('filename', os.path.basename(result['path'])).rsplit('.', 1)[0] + '.pdf'
                zf.write(result['pdf_path'], pdf_filename)

    shutil.rmtree(job_dir, ignore_errors=True)

    _update_progress(job_id, status='done', progress=100, current_doc=None,
                     results=results, download_url=f'/api/download/{job_id}',
                     zip_name=zip_name)


@app.get("/api/standards", summary="List all ISO standards", description="Returns all supported ISO standards, categories, and document types.")
def get_standards():
    return {
        'standards': ISO_STANDARDS,
        'categories': STANDARD_CATEGORIES,
        'documents': OUTPUT_DOCUMENTS,
        'doc_labels': DOC_LABELS,
    }


@app.post("/api/upload")
async def upload_files(
    audit_notes: UploadFile = File(...),
    manday: UploadFile = File(...),
    checklist_template: UploadFile | None = File(None),
    api_key: str = Form(''),
    standards: str = Form('[]'),
    client_key: str = Form(''),
):
    selected_standards = json.loads(standards)
    if not selected_standards:
        raise HTTPException(status_code=400, detail='At least one ISO standard must be selected')

    if not audit_notes.filename or not manday.filename:
        raise HTTPException(status_code=400, detail='Both files must be selected')

    job_id = uuid.uuid4().hex
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    notes_ext = os.path.splitext(audit_notes.filename)[1].lower()
    notes_path = os.path.join(job_dir, f'audit_notes{notes_ext}')
    manday_path = os.path.join(job_dir, 'manday.docx')

    # Read and validate file sizes
    content = await audit_notes.read()
    if len(content) > MAX_FILE_SIZE:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=413, detail=f'Audit notes file exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
    with open(notes_path, 'wb') as f:
        f.write(content)

    content = await manday.read()
    if len(content) > MAX_FILE_SIZE:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=413, detail=f'Manday file exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
    with open(manday_path, 'wb') as f:
        f.write(content)

    if checklist_template and checklist_template.filename:
        content = await checklist_template.read()
        if len(content) > MAX_FILE_SIZE:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=413, detail=f'Template file exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
        template_path = os.path.join(job_dir, 'checklist_template.docx')
        with open(template_path, 'wb') as f:
            f.write(content)

    try:
        notes_data = extract_audit_notes(notes_path)
        manday_data = extract_manday_data(manday_path)
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f'Failed to parse documents: {str(e)}')

    with _progress_lock:
        progress_store[job_id] = {
            'status': 'uploaded',
            'progress': 5,
            'current_doc': None,
            'created_at': time.time(),
            'doc_progress': {},
            'results': None,
            'error': None,
            'download_url': None,
            'zip_name': 'TUV_Audit_Package.zip',
            'client_key': client_key or None,
        }

    if api_key:
        standards_full = [ISO_STANDARDS.get(s, s) for s in selected_standards]
        t = threading.Thread(
            target=generate_background,
            args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key or None),
            daemon=True,
        )
        t.start()
        return {
            'success': True,
            'job_id': job_id,
            'async': True,
            'status_url': f'/api/status/{job_id}',
        }

    return {
        'success': True,
        'job_id': job_id,
        'api_key_required': True,
        'message': 'Files uploaded. Configure API key and click Generate.',
    }


@app.post("/api/generate")
async def generate_docs(
    job_id: str = Form(...),
    api_key: str = Form(''),
    standards: str = Form('[]'),
    client_key: str = Form(''),
):
    selected_standards = json.loads(standards)

    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    notes_path = None
    for ext in ('.docx', '.txt'):
        candidate = os.path.join(job_dir, f'audit_notes{ext}')
        if os.path.exists(candidate):
            notes_path = candidate
            break
    manday_path = os.path.join(job_dir, 'manday.docx')

    if not notes_path or not os.path.exists(manday_path):
        raise HTTPException(status_code=400, detail='Uploaded files not found. Please upload again.')

    notes_data = extract_audit_notes(notes_path)
    manday_data = extract_manday_data(manday_path)
    standards_full = [ISO_STANDARDS.get(s, s) for s in selected_standards]

    with _progress_lock:
        progress_store[job_id] = {
            'status': 'uploaded',
            'progress': 5,
            'current_doc': None,
            'created_at': time.time(),
            'doc_progress': {},
            'results': None,
            'error': None,
            'download_url': None,
            'zip_name': 'TUV_Audit_Package.zip',
            'client_key': client_key or None,
        }

    t = threading.Thread(
        target=generate_background,
        args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key or None),
        daemon=True,
    )
    t.start()

    return {
        'success': True,
        'job_id': job_id,
        'async': True,
        'status_url': f'/api/status/{job_id}',
    }


@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    entry = _get_progress(job_id)
    if not entry:
        raise HTTPException(status_code=404, detail='Job not found')

    result_data = entry.get('results')
    cleaned_results = None
    if result_data:
        cleaned_results = {}
        for doc_type, result in result_data.items():
            cleaned = {}
            for k, v in result.items():
                if k not in ('path', 'pdf_path', '_data'):
                    cleaned[k] = v
            data = result.get('_data', {})
            if doc_type == 'Audit_Report':
                cleaned['findings_summary_preview'] = (data.get('findings_summary') or '')[:200]
                cleaned['methodology'] = data.get('methodology')
                cleaned['certification_decision'] = data.get('certification_decision')
            elif doc_type in ('Certificate', 'Certificate_Text'):
                cleaned['certification_decision'] = data.get('certification_decision')
                cleaned['conditions'] = data.get('conditions', [])
            elif doc_type == 'ISO_Checklist':
                cleaned['total_sections'] = len(data.get('sections', []))
            cleaned_results[doc_type] = cleaned

    return {
        'status': entry['status'],
        'progress': entry['progress'],
        'current_doc': entry['current_doc'],
        'doc_progress': entry.get('doc_progress', {}),
        'results': cleaned_results,
        'download_url': entry.get('download_url'),
        'error': entry.get('error'),
    }


@app.get("/api/download/{job_id}")
def download(job_id: str):
    if not validate_job_id(job_id):
        raise HTTPException(status_code=400, detail='Invalid job ID')
    entry = _get_progress(job_id)
    zip_path = os.path.join(OUTPUT_FOLDER, f'{job_id}.zip')
    if os.path.exists(zip_path):
        zip_name = entry.get('zip_name', 'TUV_Audit_Package.zip') if entry else 'TUV_Audit_Package.zip'
        return FileResponse(zip_path, filename=zip_name, media_type='application/zip')
    raise HTTPException(status_code=404, detail='Package not found')


@app.get("/api/download_doc/{job_id}/{doc_type}")
def download_doc(job_id: str, doc_type: str):
    if not validate_job_id(job_id):
        raise HTTPException(status_code=400, detail='Invalid job ID')
    if doc_type not in OUTPUT_DOCUMENTS:
        raise HTTPException(status_code=400, detail='Invalid document type')

    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail='Job output not found')

    for fname in sorted(os.listdir(output_dir)):
        if fname.startswith(doc_type) and fname.endswith('.docx'):
            return FileResponse(
                os.path.join(output_dir, fname),
                filename=fname,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            )
    for fname in sorted(os.listdir(output_dir)):
        if fname.startswith(doc_type):
            return FileResponse(
                os.path.join(output_dir, fname),
                filename=fname,
            )
    raise HTTPException(status_code=404, detail='Document not found')


# --- Excel generation endpoint ---

@app.post("/api/generate_excel")
def generate_excel_endpoint(
    client_key: str = Form(''),
    doc_type: str = Form('risk_register'),
):
    """Generate an Excel document (risk_register, bia, enms, dashboard)."""
    from app.services.excel_generator import generate_excel

    if not client_key:
        raise HTTPException(status_code=400, detail='client_key is required')

    client = get_client(client_key)
    if not client:
        raise HTTPException(status_code=404, detail=f'Client not found: {client_key}')

    output_dir = os.path.join(OUTPUT_FOLDER, 'excel')
    try:
        path = generate_excel(client_key, doc_type, output_dir)
        filename = os.path.basename(path)
        return FileResponse(
            path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Excel generation failed: {str(e)}')


# --- Client management endpoints ---

@app.get("/api/clients")
def get_clients():
    """Return all active clients with their configuration."""
    return {'clients': list_clients()}


@app.get("/api/clients/{client_key}")
def get_client_detail(client_key: str):
    """Return full configuration for a specific client."""
    client = get_client(client_key)
    if not client:
        raise HTTPException(status_code=404, detail=f'Client not found: {client_key}')
    return {
        'key': client.key,
        'name': client.name,
        'name_ar': client.name_ar,
        'doc_code_prefix': client.doc_code_prefix,
        'language': client.language,
        'standards': client.standards,
        'formulas': {
            'latent_risk': client.formulas.latent_risk,
            'residual_risk': client.formulas.residual_risk,
            'rating_method': client.formulas.rating_method,
            'treatment_lookup': client.formulas.treatment_lookup,
        },
        'visual': {
            'primary_header': client.visual.primary_header,
            'accent': client.visual.accent,
            'secondary': client.visual.secondary,
            'rtl': client.visual.rtl,
        },
        'description': client.description,
    }


@app.post("/api/clients/{client_key}/validate")
def validate_client_doc(client_key: str, data: dict):
    """Validate document data against client configuration."""
    errors = validate_client_data(client_key, data)
    return {'valid': len(errors) == 0, 'errors': errors}


@app.get("/api/clients/{client_key}/doc_code")
def generate_doc_code(client_key: str, doc_type: str = "DOC", sequence: int = 1):
    """Generate a document code for a client."""
    client = get_client(client_key)
    if not client:
        raise HTTPException(status_code=404, detail=f'Client not found: {client_key}')
    return {
        'doc_code': get_doc_code(client_key, doc_type, sequence),
        'prefix': client.doc_code_prefix,
    }


# --- Compliance-specific endpoints ---

compliance_frameworks = {
    'iso_37301': {
        'name': 'ISO 37301:2021 Compliance Management',
        'pillars': [
            {'id': 'governance', 'label': 'Governance & Leadership'},
            {'id': 'risk_assessment', 'label': 'Compliance Risk Assessment'},
            {'id': 'policies', 'label': 'Policies & Procedures'},
            {'id': 'training', 'label': 'Training & Awareness'},
            {'id': 'monitoring', 'label': 'Monitoring & Reporting'},
            {'id': 'investigation', 'label': 'Investigation & Remediation'},
        ],
    },
    'iso_31000': {
        'name': 'ISO 31000:2018 Risk Management',
        'pillars': [
            {'id': 'framework', 'label': 'Risk Framework Design'},
            {'id': 'identification', 'label': 'Risk Identification'},
            {'id': 'analysis', 'label': 'Risk Analysis'},
            {'id': 'evaluation', 'label': 'Risk Evaluation'},
            {'id': 'treatment', 'label': 'Risk Treatment'},
            {'id': 'review', 'label': 'Monitoring & Review'},
        ],
    },
}


@app.get("/api/compliance/frameworks")
def get_frameworks():
    return {'frameworks': compliance_frameworks}


@app.get("/api/compliance/checklist/{framework_id}")
def get_checklist(framework_id: str):
    framework = compliance_frameworks.get(framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail='Framework not found')

    return {
        'framework': framework,
        'checklist_items': [
            {
                'pillar': p['id'],
                'pillar_label': p['label'],
                'items': [
                    f'Document {p["label"]} policy',
                    f'Assign responsibility for {p["label"]}',
                    f'Establish procedures for {p["label"]}',
                ],
            }
            for p in framework['pillars']
        ],
    }


# ── Audit Workflow Endpoints ──

from app.services.audit_workflow import (
    create_project, get_project, list_projects, update_project, delete_project,
    advance_gate, set_gate, get_gate_info, get_project_progress,
    create_nc, get_nc, list_ncs, update_nc,
    create_capa, get_capa, list_capas, update_capa,
    add_evidence, get_dashboard_stats, GATES,
)


@app.post("/api/projects")
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


@app.get("/api/projects")
def list_audit_projects(client_key: str = "", status: str = ""):
    projects = list_projects(
        client_key=client_key or None,
        status=status or None,
    )
    return {"projects": [p.to_dict() for p in projects]}


@app.get("/api/projects/{project_id}")
def get_audit_project(project_id: str):
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()


@app.get("/api/projects/{project_id}/progress")
def get_audit_progress(project_id: str):
    progress = get_project_progress(project_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Project not found")
    return progress


@app.put("/api/projects/{project_id}")
def update_audit_project(project_id: str, **kwargs):
    project = update_project(project_id, **kwargs)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.to_dict()


@app.delete("/api/projects/{project_id}")
def delete_audit_project(project_id: str):
    if delete_project(project_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Project not found")


@app.post("/api/projects/{project_id}/advance")
def advance_project_gate(project_id: str):
    project = advance_gate(project_id)
    if not project:
        raise HTTPException(status_code=400, detail="Cannot advance gate")
    return {"success": True, "project": project.to_dict()}


@app.post("/api/projects/{project_id}/gate/{gate_num}")
def set_project_gate(project_id: str, gate_num: int):
    project = set_gate(project_id, gate_num)
    if not project:
        raise HTTPException(status_code=400, detail="Invalid gate or project")
    return {"success": True, "project": project.to_dict()}


@app.get("/api/gates")
def get_all_gates():
    return {"gates": GATES}


# ── NC Endpoints ──

@app.post("/api/projects/{project_id}/ncs")
def create_nc_endpoint(
    project_id: str,
    clause: str = Form(""),
    severity: str = Form("Minor"),
    description: str = Form(""),
    evidence: str = Form(""),
    auditee: str = Form(""),
    due_date: str = Form(""),
):
    nc = create_nc(project_id, clause, severity, description, evidence, auditee, due_date)
    if not nc:
        raise HTTPException(status_code=404, detail="Project not found")
    return nc.to_dict()


@app.get("/api/projects/{project_id}/ncs")
def list_ncs_endpoint(project_id: str, status: str = ""):
    ncs = list_ncs(project_id=project_id, status=status or None)
    return {"ncs": [n.to_dict() for n in ncs]}


@app.put("/api/ncs/{nc_id}")
def update_nc_endpoint(nc_id: str, **kwargs):
    nc = update_nc(nc_id, **kwargs)
    if not nc:
        raise HTTPException(status_code=404, detail="NC not found")
    return nc.to_dict()


# ── CAPA Endpoints ──

@app.post("/api/projects/{project_id}/capas")
def create_capa_endpoint(
    project_id: str,
    nc_id: str = Form(""),
    root_cause: str = Form(""),
    containment: str = Form(""),
    corrective_action: str = Form(""),
    preventive_action: str = Form(""),
    owner: str = Form(""),
    due_date: str = Form(""),
):
    capa = create_capa(project_id, nc_id, root_cause, containment,
                       corrective_action, preventive_action, owner, due_date)
    if not capa:
        raise HTTPException(status_code=404, detail="Project not found")
    return capa.to_dict()


@app.get("/api/projects/{project_id}/capas")
def list_capas_endpoint(project_id: str, status: str = ""):
    capas = list_capas(project_id=project_id, status=status or None)
    return {"capas": [c.to_dict() for c in capas]}


@app.put("/api/capas/{capa_id}")
def update_capa_endpoint(capa_id: str, **kwargs):
    capa = update_capa(capa_id, **kwargs)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    return capa.to_dict()


# ── Dashboard ──

@app.get("/api/dashboard")
def get_dashboard(client_key: str = ""):
    stats = get_dashboard_stats(client_key=client_key or None)
    return stats


@app.on_event("startup")
async def startup():
    cleanup_old_jobs()
