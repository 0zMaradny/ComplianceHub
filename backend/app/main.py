import os
import json
import zipfile
import uuid
import shutil
import threading
import time
import asyncio
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

from app.config import (
    UPLOAD_FOLDER, OUTPUT_FOLDER, ISO_STANDARDS,
    OUTPUT_DOCUMENTS, DOC_LABELS, STANDARD_CATEGORIES,
    AUDIT_PACKAGE_DOCS, STANDALONE_DOCS
)
from app.utils import sanitize_filename, validate_job_id
from app.services.client_config import get_client, list_clients, get_doc_code, validate_client_data
from app.services.file_parser import extract_audit_notes, extract_manday_data, extract_manday_tables
from app.services.ai_pipeline import generate_document as ai_generate, extract_shared_context
from app.services.ai.router import (
    get_model_performance, get_model_recommendation,
    _provider_health as _prov_health,
)
from app.services.ai.model_registry import ALL_MODELS
from app.services.export_validator import ExportValidator
from app.services.document_generator import generate_document_file, generate_audit_plan_stage
from app.services.pdf_generator import generate_pdf_file
from app.services.offline_generator import generate_all as offline_generate_all
from app.services.clause_data import get_clause_data, get_annex_a_data
from app.services import db
from datetime import datetime, timedelta
from app.services.ai_chat import build_chat_context, chat_with_ai, chat_stream
from app.services.doc_refiner import refine_field, bulk_refine, get_field_versions, get_refinable_fields, REFINABLE_FIELDS as RF

app = FastAPI(
    title="ComplianceHub API",
    version="2.0.0",
    description="TÜV Austria ComplianceHub — ISO audit document generation, project management, and multi-standard IMS platform",
    openapi_tags=[
        {"name": "System", "description": "Health check and system status"},
        {"name": "Standards", "description": "ISO standard definitions and clause data"},
        {"name": "Document Generation", "description": "Upload, generate, and download audit documents"},
        {"name": "Excel Export", "description": "Generate Excel workbooks (risk register, BIA, EnMS, KPI)"},
        {"name": "Clients", "description": "Client configuration and validation"},
        {"name": "Compliance", "description": "Compliance frameworks and checklists"},
        {"name": "Audit Workflow", "description": "6-gate audit project lifecycle management"},
        {"name": "Surveillance", "description": "Surveillance and recertification audit cycle management"},
        {"name": "IMS Multi-Standard", "description": "Cross-standard clause mapping and gap analysis"},
        {"name": "Templates", "description": "Document template management"},
        {"name": "Analytics", "description": "Dashboard statistics and reporting"},
    ],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

# ── CORS: configurable via env var ───────────────────────────────────────
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
if CORS_ORIGINS == "*":
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ── Health check ──────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    check_overdue_cycles()
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": time.time(),
    }


# ── Thread-safe progress store ───────────────────────────────────────────
progress_store: dict = {}
_progress_lock = threading.Lock()
MAX_JOB_AGE = 3600

# ── Rate limiting (simple in-memory) ─────────────────────────────────────
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = threading.Lock()
RATE_LIMIT_WINDOW = 60       # seconds
RATE_LIMIT_MAX_REQUESTS = 300  # per window per client (generous for testing)
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
    """Generate DOCX + PDF files from data, return doc_info dict or None."""
    _t1 = time.perf_counter()
    path = generate_document_file(doc_type, doc_data, output_dir, template_path, standard_key, client_key=client_key)
    if not path:
        return None
    _docx_t = time.perf_counter() - _t1
    filename = os.path.basename(path)
    doc_info = {'path': path, 'filename': filename}
    try:
        _t2 = time.perf_counter()
        pdf_path = generate_pdf_file(doc_type, doc_data, output_dir)
        _pdf_t = time.perf_counter() - _t2
        if pdf_path and os.path.exists(pdf_path):
            doc_info['pdf_path'] = pdf_path
            doc_info['pdf_filename'] = os.path.basename(pdf_path)
        logger.info('PROFILE filegen %s: DOCX %.2fs + PDF %.2fs = %.2fs', doc_type, _docx_t, _pdf_t, _docx_t + _pdf_t)
    except Exception as e:
        logger.warning("PDF generation failed for %s: %s", doc_type, e)
    for k in ('certification_decision', 'conditions', 'findings_summary',
              'conclusion', 'methodology', 'sections', 'summary',
              'client_name', 'audit_date', 'standard', 'scope', 'lead_auditor',
              'report_number', 'certificate_number', 'nonconformities',
              'positive_findings', 'opportunities_for_improvement',
              'controls', 'action_items', 'agenda_items', 'decisions',
              'root_cause', 'overall_assessment', 'status',
              'review_date', 'next_review_date', 'car_number', 'nc_reference',
              'severity', 'recommended_action', 'priority',
              'critical_activities', 'overall_findings',
              'processing_activities', 'data_controller', 'data_protection_officer',
              'risks', 'risk_assessment_reference',
              'incident_date', 'incident_description', 'location', 'incident_type',
              'investigation_team', 'immediate_actions', 'corrective_actions',
              'lessons_learned', 'recommendations', 'reviewed_by',
              'program_year', 'audit_manager', 'audits',
              'aspects', 'impact_type', 'significance', 'control_measures', 'legal_requirement',
              'hazards', 'associated_risk', 'existing_controls', 'additional_controls', 'hierarchy_of_control',
              'energy_sources', 'review_period', 'significant_uses', 'enpi', 'baseline', 'current_performance',
              'obligations', 'obligation_type', 'compliance_status', 'evidence',
              'services', 'portfolio_manager', 'sla_uptime', 'sla_response_time', 'sla_resolution_time',
              'catalogue_owner', 'catalogue_version',
              'register_owner', 'agreements', 'supplier_name',
              'relationship_manager', 'customers',
              'capacity_manager', 'review_period', 'components',
              'change_manager', 'changes',
              'release_manager', 'releases',
              'incident_manager', 'incidents',
              'problem_manager', 'problems',
              'plan_owner', 'last_review_date', 'next_review_date',
              'report_owner', 'reporting_period',
              'overall_availability'):
        if k in doc_data:
            doc_info[k] = doc_data[k]
    return doc_info


def generate_background(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key=None, manday_config=None):
    _t0 = time.perf_counter()
    logger.info('JOB %s START: generate_background with api_key=%s, standards=%s, client_key=%s, manday_config=%s',
                job_id, bool(api_key), selected_standards, client_key, bool(manday_config))
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
        _ts = time.perf_counter()
        shared_context = extract_shared_context(api_key, notes_text, manday_text)
        logger.info('JOB %s extract_shared_context took %.2fs', job_id, time.perf_counter() - _ts)
        if 'error' in shared_context:
            logger.warning('JOB %s extract_shared_context error: %s', job_id, shared_context['error'])
            shared_context = None

    manday_info = manday_config if manday_config else None

    # Pre-compute offline results once (reused across doc types)
    offline_cache = None
    _offline_timer = None

    results = {}
    total = len(OUTPUT_DOCUMENTS)
    client_name = 'Client'
    completed = 0
    _nonlocal_lock = threading.Lock()

    def process_doc(doc_type):
        nonlocal offline_cache, client_name, _offline_timer

        _t_start = time.perf_counter()
        with _progress_lock:
            if job_id in progress_store:
                progress_store[job_id]['doc_progress'][doc_type] = 'generating'

        doc_data = None
        ai_error = None
        _ai_attempted = False

        # 1) Try AI pipeline (router → local/cloud provider)
        if api_key and api_key.strip().lower() not in ('', 'local'):
            _ai_attempted = True
            try:
                ai_result = ai_generate(
                    api_key, notes_text, manday_text,
                    standards_full, doc_type, shared_context,
                    client_key=client_key, manday_info=manday_info
                )
                if 'error' not in ai_result:
                    doc_data = ai_result
                else:
                    ai_error = ai_result['error']
            except Exception as e:
                ai_error = str(e)

        # 2) If AI failed or no key, fall back to offline generator
        if doc_data is None:
            with _nonlocal_lock:
                if _offline_timer is None:
                    _offline_timer = time.perf_counter()
                if offline_cache is None:
                    _ts = time.perf_counter()
                    offline_cache = offline_generate_all(
                        notes_text, manday_text,
                        standards_full, selected_standards
                    )
                    logger.info('JOB %s offline_generate_all took %.2fs', job_id, time.perf_counter() - _ts)
            doc_data = offline_cache.get(doc_type, {})
            if 'error' in doc_data:
                ai_error = ai_error or doc_data['error']
                doc_data = None

        # 3) Generate the DOCX + PDF from whatever data we have
        if doc_data:
            if client_key:
                doc_data['client_key'] = client_key
            doc_info = _make_doc_result(output_dir, template_path, standard_key, doc_type, doc_data, client_key=client_key)
            if doc_info:
                with _nonlocal_lock:
                    if client_name == 'Client':
                        client_name = doc_data.get('client_name', 'Client')
                doc_info['_data'] = doc_data
                with _progress_lock:
                    if job_id in progress_store:
                        progress_store[job_id]['doc_progress'][doc_type] = 'done'
                dt = time.perf_counter() - _t_start
                logger.info('JOB %s doc %s completed in %.2fs (source=%s)', job_id, doc_type, dt, 'ai' if _ai_attempted and ai_error is None else 'offline')
                return doc_type, doc_info

        with _progress_lock:
            if job_id in progress_store:
                progress_store[job_id]['doc_progress'][doc_type] = 'error'
        logger.warning('JOB %s doc %s FAILED after %.2fs', job_id, doc_type, time.perf_counter() - _t_start)
        return doc_type, {'error': ai_error or 'Document generation failed'}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_doc, dt): dt for dt in OUTPUT_DOCUMENTS}
        for future in as_completed(futures):
            dt, result = future.result()
            results[dt] = result
            completed += 1
            _update_progress(job_id, current_doc=DOC_LABELS.get(dt, dt),
                             progress=20 + int((completed / total) * 70))

    _update_progress(job_id, progress=95, current_doc='Creating package...')

    _ts = time.perf_counter()
    safe_name = sanitize_filename(client_name)
    zip_name = f'TUV_Audit_Package_{safe_name}.zip'
    zip_path = os.path.join(OUTPUT_FOLDER, f'{job_id}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for doc_type, result in results.items():
            if 'path' in result and os.path.exists(result['path']):
                zf.write(result['path'], result.get('filename', os.path.basename(result['path'])))
            if 'pdf_path' in result and os.path.exists(result['pdf_path']):
                pdf_filename = result.get('pdf_filename') or (result.get('filename', os.path.basename(result['path'])).rsplit('.', 1)[0] + '.pdf')
                zf.write(result['pdf_path'], pdf_filename)
    logger.info('JOB %s zip took %.2fs', job_id, time.perf_counter() - _ts)

    shutil.rmtree(job_dir, ignore_errors=True)

    _update_progress(job_id, status='done', progress=100, current_doc=None,
                     results=results, download_url=f'/api/download/{job_id}',
                     zip_name=zip_name)

    _total = time.perf_counter() - _t0
    logger.info('JOB %s TOTAL: %.2fs for %d docs (%.2f avg)', job_id, _total, total, _total / total)


@app.get("/api/standards", summary="List all ISO standards", description="Returns all supported ISO standards, categories, and document types.")
def get_standards():
    return {
        'standards': ISO_STANDARDS,
        'categories': STANDARD_CATEGORIES,
        'documents': OUTPUT_DOCUMENTS,
        'doc_labels': DOC_LABELS,
        'audit_package_docs': AUDIT_PACKAGE_DOCS,
        'standalone_docs': STANDALONE_DOCS,
    }


@app.post("/api/upload")
async def upload_files(
    audit_notes: UploadFile = File(...),
    manday: UploadFile = File(...),
    checklist_template: UploadFile | None = File(None),
    api_key: str = Form(''),
    standards: str = Form('[]'),
    client_key: str = Form(''),
    manday_config: str = Form('null'),
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
    # Basic MIME validation: docx must be ZIP (PK), txt should be text
    if notes_ext == '.docx' and content[:2] != b'PK':
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail='Invalid audit notes file: not a valid DOCX')
    if notes_ext == '.txt':
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail='Invalid audit notes file: not a valid text file')
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

    mc = json.loads(manday_config) if manday_config not in ('null', 'None', '') else None

    manday_extracted = {}
    try:
        manday_extracted = extract_manday_tables(manday_path)
    except Exception as e:
        logger.warning("Manday table extraction failed: %s", e)

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

    db.set_job(
        job_id=job_id,
        status='uploaded',
        progress=5,
        current_doc=None,
        created_at=time.time(),
        doc_progress='{}',
        results=None,
        error=None,
        download_url=None,
        zip_name='TUV_Audit_Package.zip',
        standards=json.dumps(selected_standards),
    )

    if api_key:
        standards_full = [ISO_STANDARDS.get(s, s) for s in selected_standards]
        t = threading.Thread(
            target=generate_background,
            args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key or None, mc),
            daemon=True,
        )
        t.start()
        return {
            'success': True,
            'job_id': job_id,
            'async': True,
            'status_url': f'/api/status/{job_id}',
            'manday_extracted': manday_extracted,
        }

    return {
        'success': True,
        'job_id': job_id,
        'api_key_required': True,
        'message': 'Files uploaded. Configure API key and click Generate.',
        'manday_extracted': manday_extracted,
    }


@app.post("/api/generate")
async def generate_docs(
    job_id: str = Form(...),
    api_key: str = Form(''),
    standards: str = Form('[]'),
    client_key: str = Form(''),
    manday_config: str = Form('null'),
):
    mc = json.loads(manday_config) if manday_config not in ('null', 'None', '') else None
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

    try:
        notes_data = extract_audit_notes(notes_path)
        manday_data = extract_manday_data(manday_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to parse documents: {str(e)}')
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
        args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key or None, mc),
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
            elif doc_type == 'Management_Review_Minutes':
                cleaned['action_items'] = len(data.get('action_items', []))
                cleaned['agenda_items'] = len(data.get('agenda_items', []))
                cleaned['next_review_date'] = data.get('next_review_date', '')
            elif doc_type == 'Corrective_Action_Report':
                cleaned['car_number'] = data.get('car_number', '')
                cleaned['nc_reference'] = data.get('nc_reference', '')
                cleaned['status'] = data.get('status', '')
                cleaned['severity'] = data.get('severity', '')
            elif doc_type == 'Gap_Analysis_Report':
                cleaned['total_sections'] = len(data.get('sections', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Statement_of_Applicability':
                cleaned['total_controls'] = len(data.get('controls', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Business_Impact_Analysis':
                cleaned['total_activities'] = len(data.get('critical_activities', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Records_of_Processing_Activities':
                cleaned['total_activities'] = len(data.get('processing_activities', []))
                cleaned['data_controller'] = data.get('data_controller', '')
                cleaned['data_protection_officer'] = data.get('data_protection_officer', '')
            elif doc_type == 'Risk_Treatment_Plan':
                cleaned['total_risks'] = len(data.get('risks', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Incident_Investigation_Report':
                cleaned['incident_type'] = data.get('incident_type', '')
                cleaned['severity'] = data.get('severity', '')
                cleaned['incident_date'] = data.get('incident_date', '')
                cleaned['status'] = data.get('status', '')
                cleaned['location'] = data.get('location', '')
            elif doc_type == 'Internal_Audit_Program':
                cleaned['program_year'] = data.get('program_year', '')
                cleaned['total_audits'] = len(data.get('audits', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Environmental_Aspect_Register':
                cleaned['total_aspects'] = len(data.get('aspects', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Hazard_Identification_Register':
                cleaned['total_hazards'] = len(data.get('hazards', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Energy_Review':
                cleaned['total_sources'] = len(data.get('energy_sources', []))
                cleaned['total_seus'] = len(data.get('significant_uses', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Compliance_Obligations_Register':
                cleaned['total_obligations'] = len(data.get('obligations', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Service_Portfolio':
                cleaned['total_services'] = len(data.get('services', []))
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Service_Catalogue':
                cleaned['total_services'] = len(data.get('services', []))
                cleaned['catalogue_owner'] = data.get('catalogue_owner', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Supplier_Agreement_Register':
                cleaned['total_agreements'] = len(data.get('agreements', []))
                cleaned['register_owner'] = data.get('register_owner', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Business_Relationship_Register':
                cleaned['total_customers'] = len(data.get('customers', []))
                cleaned['relationship_manager'] = data.get('relationship_manager', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Capacity_Management_Plan':
                cleaned['total_components'] = len(data.get('components', []))
                cleaned['capacity_manager'] = data.get('capacity_manager', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Change_Management_Register':
                cleaned['total_changes'] = len(data.get('changes', []))
                cleaned['change_manager'] = data.get('change_manager', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Release_Deployment_Plan':
                cleaned['total_releases'] = len(data.get('releases', []))
                cleaned['release_manager'] = data.get('release_manager', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Incident_Management_Log':
                cleaned['total_incidents'] = len(data.get('incidents', []))
                cleaned['incident_manager'] = data.get('incident_manager', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Problem_Management_Register':
                cleaned['total_problems'] = len(data.get('problems', []))
                cleaned['problem_manager'] = data.get('problem_manager', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Service_Continuity_Plan':
                cleaned['total_services'] = len(data.get('services', []))
                cleaned['plan_owner'] = data.get('plan_owner', '')
                cleaned['summary'] = data.get('summary', {})
            elif doc_type == 'Availability_Management_Report':
                cleaned['total_services'] = len(data.get('services', []))
                cleaned['report_owner'] = data.get('report_owner', '')
                cleaned['summary'] = data.get('summary', {})
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


@app.get("/api/download_doc/{job_id}/{doc_type}/pdf")
def download_doc_pdf(job_id: str, doc_type: str):
    if not validate_job_id(job_id):
        raise HTTPException(status_code=400, detail='Invalid job ID')
    if doc_type not in OUTPUT_DOCUMENTS:
        raise HTTPException(status_code=400, detail='Invalid document type')

    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail='Job output not found')

    for fname in sorted(os.listdir(output_dir)):
        if fname.startswith(doc_type) and fname.endswith('.pdf'):
            return FileResponse(
                os.path.join(output_dir, fname),
                filename=fname,
                media_type='application/pdf',
            )
    raise HTTPException(status_code=404, detail='PDF not found')


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
    advance_gate, set_gate, get_project_progress,
    create_nc, list_ncs, update_nc,
    create_capa, list_capas, update_capa,
    create_evidence, list_evidence, update_evidence,
    get_dashboard_stats, GATES,
)
from app.services.ims import (
    get_ims_mapping, get_integrated_clause_list,
    get_shared_docs, get_unique_requirements,
    generate_ims_gap_analysis,
    IMS_MAPPINGS,
)
from app.services.audit_program import (
    create_program, list_programs, update_program, delete_program,
    create_entry, list_entries, update_entry, delete_entry,
    build_checklist_for_program, list_checklist,
    list_checklist_by_day, update_checklist_item, bulk_update_checklist,
    add_evidence, list_evidence_register, update_evidence_entry, delete_evidence_entry,
    get_or_create_daily_summary, update_daily_summary, list_daily_summaries,
    get_program_overview, get_checklist_export,
)
from app.services.surveillance import (
    create_surveillance_cycle, get_surveillance_cycle,
    list_surveillance_cycles, update_surveillance_cycle,
    generate_surveillance_scope,
    create_surveillance_finding,
    list_surveillance_findings,
    get_surveillance_dashboard_stats,
    auto_schedule_surveillance, check_overdue_cycles,
)


@app.post("/api/projects", summary="Create audit project", description="Create a new audit project for a client with specified standards and target date. The project starts at Gate 1 (Scope & Context).")
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


# ── Evidence Endpoints ──

@app.post("/api/projects/{project_id}/evidence")
async def upload_evidence(
    project_id: str,
    clause: str = Form(""),
    standard: str = Form(""),
    uploaded_by: str = Form(""),
    file: UploadFile = File(...),
):
    """Upload evidence file for a project."""
    if project_id not in [p.id for p in list_projects()]:
        raise HTTPException(status_code=404, detail="Project not found")
    safe_name = sanitize_filename(f"{project_id}_{clause.replace('.', '_')}_{file.filename}")
    evidence_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'evidence_files')
    os.makedirs(evidence_dir, exist_ok=True)
    file_path = os.path.join(evidence_dir, safe_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    ev = create_evidence(project_id, clause, standard, file.filename, file_path, uploaded_by)
    if not ev:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "evidence": ev.to_dict()}


@app.get("/api/projects/{project_id}/evidence")
def get_evidence(project_id: str):
    """List all evidence for a project."""
    evidence = list_evidence(project_id)
    return {"evidence": [e.to_dict() for e in evidence]}


@app.put("/api/evidence/{evidence_id}")
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
    return {"success": True, "evidence": ev.to_dict()}


# ── Surveillance Endpoints ──

@app.post("/api/surveillance/cycles", summary="Create surveillance cycle", tags=["Surveillance"])
def create_surveillance_cycle_endpoint(
    project_id: str = Form(""),
    cycle_number: int = Form(0),
    scheduled_date: str = Form(""),
    notes: str = Form(""),
):
    if not project_id or not cycle_number or not scheduled_date:
        raise HTTPException(status_code=400, detail="project_id, cycle_number, scheduled_date are required")
    if cycle_number not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="cycle_number must be 1, 2, or 3")
    cycle = create_surveillance_cycle(project_id, cycle_number, scheduled_date, notes)
    return {"success": True, "cycle": cycle.to_dict()}


@app.get("/api/surveillance/cycles", summary="List surveillance cycles", tags=["Surveillance"])
def list_surveillance_cycles_endpoint(project_id: str = "", status: str = ""):
    cycles = list_surveillance_cycles(
        project_id=project_id or None,
        status=status or None,
    )
    return {"cycles": [c.to_dict() for c in cycles]}


@app.get("/api/surveillance/cycles/{cycle_id}", summary="Get surveillance cycle", tags=["Surveillance"])
def get_surveillance_cycle_endpoint(cycle_id: str):
    cycle = get_surveillance_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle.to_dict()


@app.put("/api/surveillance/cycles/{cycle_id}", summary="Update surveillance cycle", tags=["Surveillance"])
def update_surveillance_cycle_endpoint(cycle_id: str, data: dict):
    cycle = update_surveillance_cycle(cycle_id, **data)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return cycle.to_dict()


@app.post("/api/surveillance/cycles/{cycle_id}/scope", summary="Generate surveillance scope", tags=["Surveillance"])
def generate_surveillance_scope_endpoint(cycle_id: str):
    cycle = get_surveillance_cycle(cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    scope = generate_surveillance_scope(cycle.project_id, cycle_id)
    if "error" in scope:
        raise HTTPException(status_code=404, detail=scope["error"])
    return scope


@app.post("/api/surveillance/cycles/{cycle_id}/findings", summary="Add surveillance finding", tags=["Surveillance"])
def create_surveillance_finding_endpoint(
    cycle_id: str,
    clause: str = Form(""),
    finding_type: str = Form("new_nc"),
    severity: str = Form("Minor"),
    description: str = Form(""),
    previous_nc_id: str = Form(""),
):
    finding = create_surveillance_finding(
        cycle_id=cycle_id, clause=clause,
        finding_type=finding_type, severity=severity,
        description=description, previous_nc_id=previous_nc_id,
    )
    if not finding:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return finding.to_dict()


@app.get("/api/surveillance/cycles/{cycle_id}/findings", summary="List cycle findings", tags=["Surveillance"])
def list_surveillance_findings_endpoint(cycle_id: str, project_id: str = ""):
    findings = list_surveillance_findings(
        cycle_id=cycle_id,
        project_id=project_id or None,
    )
    return {"findings": [f.to_dict() for f in findings]}


@app.post("/api/projects/{project_id}/auto-schedule", summary="Auto-schedule surveillance cycles", tags=["Surveillance"])
def auto_schedule_surveillance_endpoint(project_id: str, cert_date: str = ""):
    if not cert_date:
        raise HTTPException(status_code=400, detail="cert_date is required (YYYY-MM-DD)")
    cycles = auto_schedule_surveillance(project_id, cert_date)
    return {"success": True, "cycles": [c.to_dict() for c in cycles]}


@app.get("/api/surveillance/dashboard", summary="Surveillance dashboard stats", tags=["Surveillance"])
def surveillance_dashboard():
    return get_surveillance_dashboard_stats()


@app.post("/api/surveillance/check-overdue", summary="Check overdue cycles", tags=["Surveillance"])
def check_overdue_endpoint():
    overdue = check_overdue_cycles()
    return {"success": True, "newly_overdue": len(overdue), "cycles": [c.to_dict() for c in overdue]}


# ── IMS Multi-Standard Endpoints ──

@app.get("/api/ims/mapping")
def get_ims_mapping_endpoint(standards: str = ""):
    """Get IMS cross-standard clause mapping.
    Example: /api/ims/mapping?standards=iso_45001,iso_14001
    """
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required (comma-separated)")
    std_list = [s.strip() for s in standards.split(",")]
    mapping = get_ims_mapping(std_list)
    if not mapping:
        return {"available_mappings": [list(k) for k in IMS_MAPPINGS.keys()], "message": "No mapping for this combination"}
    return mapping


@app.get("/api/ims/clauses")
def get_ims_clauses_endpoint(standards: str = ""):
    """Get deduplicated clause list for an IMS."""
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    clauses = get_integrated_clause_list(std_list)
    return {"standards": std_list, "clauses": clauses, "total": len(clauses)}


@app.get("/api/ims/shared-docs")
def get_ims_shared_docs_endpoint(standards: str = ""):
    """Get documents that can be shared across standards."""
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    docs = get_shared_docs(std_list)
    return {"standards": std_list, "shared_documents": docs, "total": len(docs)}


@app.get("/api/ims/unique-requirements")
def get_ims_unique_endpoint(standards: str = ""):
    """Get requirements unique to each standard."""
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    unique = get_unique_requirements(std_list)
    return {"standards": std_list, "unique_requirements": unique}


@app.post("/api/ims/gap-analysis")
def ims_gap_analysis_endpoint(standards: str = Form(""), compliance_data: str = Form("{}")):
    """Generate IMS gap analysis. compliance_data is JSON: {clause: {status, evidence}}"""
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    data = json.loads(compliance_data) if compliance_data else {}
    result = generate_ims_gap_analysis(std_list, data)
    return result


# ── Analytics Endpoints ──

@app.get("/api/analytics/nc-trends", tags=["Analytics"])
def get_nc_trends(months: int = 6, project_id: str = ""):
    """Return monthly NC trend data for the past N months."""
    from app.services.audit_workflow import _NCS

    # Build month labels
    now = datetime.now()
    month_labels = []
    for i in range(months - 1, -1, -1):
        d = now - timedelta(days=i * 30)
        month_labels.append(d.strftime("%Y-%m"))

    # Initialize buckets
    major_nc = [0] * months
    minor_nc = [0] * months
    ofi = [0] * months
    closed = [0] * months
    recurring_rate_pct = [0] * months

    ncs = list(_NCS.values())
    if project_id:
        ncs = [n for n in ncs if n.project_id == project_id]

    for nc in ncs:
        # Parse created_at month
        created_month = None
        if nc.created_at:
            try:
                created = datetime.fromisoformat(nc.created_at)
                created_month = created.strftime("%Y-%m")
            except (ValueError, TypeError):
                pass

        if created_month and created_month in month_labels:
            idx = month_labels.index(created_month)
            if nc.severity == "Major":
                major_nc[idx] += 1
            elif nc.severity == "Minor":
                minor_nc[idx] += 1
            else:
                ofi[idx] += 1

        # Closed items
        if nc.status == "closed" and nc.closed_at:
            try:
                closed_dt = datetime.fromisoformat(nc.closed_at)
                closed_month = closed_dt.strftime("%Y-%m")
                if closed_month in month_labels:
                    closed_idx = month_labels.index(closed_month)
                    closed[closed_idx] += 1
            except (ValueError, TypeError):
                pass

    # Recurring rate: approximate from description similarity within same month window
    # For each month with NCS, compute what fraction share clauses with prior month
    for i in range(1, months):
        if major_nc[i] + minor_nc[i] == 0:
            recurring_rate_pct[i] = 0
            continue
        # Count NCs in this month and previous month that share a clause prefix
        current_clauses = set()
        prev_clauses = set()
        for nc in ncs:
            if not nc.created_at:
                continue
            try:
                created = datetime.fromisoformat(nc.created_at)
                m = created.strftime("%Y-%m")
            except (ValueError, TypeError):
                continue
            clause_prefix = nc.clause.split(".")[0] if nc.clause else ""
            if m == month_labels[i]:
                current_clauses.add(clause_prefix)
            elif m == month_labels[i - 1]:
                prev_clauses.add(clause_prefix)
        overlap = current_clauses & prev_clauses
        total_current = major_nc[i] + minor_nc[i]
        if total_current > 0:
            recurring_rate_pct[i] = round(len(overlap) / max(len(current_clauses), 1) * 100)
        else:
            recurring_rate_pct[i] = 0

    return {
        "months": month_labels,
        "major_nc": major_nc,
        "minor_nc": minor_nc,
        "ofi": ofi,
        "closed": closed,
        "recurring_rate_pct": recurring_rate_pct,
    }


@app.get("/api/analytics/project-health", tags=["Analytics"])
def get_project_health():
    """Return per-project health scores."""
    from app.services.audit_workflow import _PROJECTS, _NCS, _CAPAS

    projects = list(_PROJECTS.values())
    now = datetime.now()
    result = []

    for project in projects:
        ncs = [n for n in _NCS.values() if n.project_id == project.id]
        capas = [c for c in _CAPAS.values() if c.project_id == project.id]

        open_major = len([n for n in ncs if n.status == "open" and n.severity == "Major"])
        open_minor = len([n for n in ncs if n.status == "open" and n.severity == "Minor"])
        pending_capa = len([c for c in capas if c.status in ("draft", "in_progress")])

        # Health score formula
        score = 100
        score -= open_major * 15
        score -= open_minor * 5
        score -= pending_capa * 3

        # Days in current gate
        days_in_gate = 0
        if project.updated_at:
            try:
                last_update = datetime.fromisoformat(project.updated_at)
                days_in_gate = (now - last_update).days
            except (ValueError, TypeError):
                pass

        if days_in_gate > 60:
            score -= 15  # -10 for >30d + additional -5 for >60d
        elif days_in_gate > 30:
            score -= 10

        score = max(0, min(100, score))

        # Health label
        if score >= 85:
            label = "Excellent"
        elif score >= 60:
            label = "Good"
        elif score >= 40:
            label = "At Risk"
        else:
            label = "Critical"

        result.append({
            "id": project.id,
            "title": project.title,
            "client": project.client_key,
            "health_score": score,
            "health_label": label,
            "open_ncs": open_major + open_minor,
            "pending_capas": pending_capa,
            "current_gate": project.current_gate,
            "days_in_gate": days_in_gate,
            "last_activity": project.updated_at[:10] if project.updated_at else "",
        })

    return {"projects": result}


@app.get("/api/analytics/ai-usage", tags=["Analytics"])
def get_ai_usage():
    """Return AI provider usage statistics from job logs and provider health tracking."""
    from app.services.ai.router import _response_cache
    from app.services.ai.model_registry import ALL_MODELS

    conn = db._get_conn()

    # Count total generations from jobs table
    done_jobs = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='done'").fetchone()[0]

    # Count per-job document types generated
    res_rows = conn.execute(
        "SELECT results FROM jobs WHERE results IS NOT NULL AND status='done'"
    ).fetchall()

    by_task: dict[str, int] = {}
    total_generations = 0
    for r in res_rows:
        raw = r['results']
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
        if isinstance(raw, dict):
            for doc_type in raw.keys():
                by_task[doc_type] = by_task.get(doc_type, 0) + 1
                total_generations += 1

    conn.close()

    # Provider usage: model_registry has known providers, health tracker has fail counts
    known_providers = set()
    for m in ALL_MODELS.values():
        known_providers.add(m.name)

    # Build by_provider from task distribution (since router doesn't persist per-provider stats,
    # we estimate from healthy providers and total generations)
    from app.services.ai.router import _provider_health as _prov_health
    by_provider = {}
    healthy = {p: True for p in known_providers if _prov_health.get(p, 0) < 3}
    if healthy and total_generations > 0:
        per_provider = total_generations // max(len(healthy), 1)
        for p in healthy:
            by_provider[p] = per_provider
        # Remainder to first provider
        remainder = total_generations - per_provider * len(healthy)
        if remainder > 0 and by_provider:
            first = list(by_provider.keys())[0]
            by_provider[first] += remainder

    # Success rate from health tracker: providers with 0 consecutive fails = healthy
    success_rate = {}
    for p in known_providers:
        fails = _prov_health.get(p, 0)
        if fails == 0:
            success_rate[p] = 95
        elif fails < 3:
            success_rate[p] = max(50, 95 - fails * 15)
        else:
            success_rate[p] = 0

    # Cache hit rate: approximate from cache size
    cache_entries = len(_response_cache)
    cache_hit_rate = round(min(cache_entries * 2.5, 50.0), 1) if cache_entries > 0 else 0.0

    return {
        "total_generations": total_generations if total_generations > 0 else done_jobs,
        "by_provider": by_provider,
        "by_task": by_task,
        "success_rate_by_provider": success_rate,
        "avg_quality_score": None,  # Not tracked persistently yet
        "cache_hit_rate": cache_hit_rate,
        "period": "last_30d",
        "note": "Per-provider breakdown approximates from job results. Provider success from in-memory health tracker (resets on restart).",
    }


@app.get("/api/analytics/capa-metrics", tags=["Analytics"])
def get_capa_metrics():
    """Return CAPA metrics computed from audit workflow data."""
    from app.services.audit_workflow import _CAPAS, _NCS

    capas = list(_CAPAS.values())
    total = len(capas)
    now = datetime.now()

    by_status = {}
    closure_days = []
    overdue = 0
    days_by_severity: dict[str, list[float]] = {}

    for capa in capas:
        # By status
        s = capa.status or "draft"
        by_status[s] = by_status.get(s, 0) + 1

        # Closure days for verified items
        if s == "verified" and capa.created_at and capa.updated_at:
            try:
                created = datetime.fromisoformat(capa.created_at)
                updated = datetime.fromisoformat(capa.updated_at)
                delta = (updated - created).days
                closure_days.append(delta)
            except (ValueError, TypeError):
                pass

        # Overdue: has due_date in the past and not closed/verified
        if capa.due_date and s not in ("verified",):
            try:
                due = datetime.fromisoformat(capa.due_date)
                if due < now:
                    overdue += 1
            except (ValueError, TypeError):
                pass

        # Days by severity (infer from linked NC or CAPA content)
        severity = "Minor"  # default
        # Attempt to link to NC for severity
        for nc_item in _NCS.values():
            if nc_item.id == capa.nc_id:
                severity = nc_item.severity
                break

        if capa.created_at:
            try:
                created = datetime.fromisoformat(capa.created_at)
                if capa.updated_at and s == "verified":
                    updated = datetime.fromisoformat(capa.updated_at)
                    d = (updated - created).days
                elif capa.due_date:
                    due = datetime.fromisoformat(capa.due_date)
                    d = (now - created).days
                else:
                    d = (now - created).days
                if severity not in days_by_severity:
                    days_by_severity[severity] = []
                days_by_severity[severity].append(float(d))
            except (ValueError, TypeError):
                pass

    avg_closure = round(sum(closure_days) / len(closure_days), 1) if closure_days else 0.0
    verified_count = by_status.get("verified", 0)
    closure_rate = round(verified_count / total * 100, 1) if total > 0 else 0.0

    avg_days_by_severity = {}
    for sev, days_list in days_by_severity.items():
        avg_days_by_severity[sev] = round(sum(days_list) / len(days_list), 1)

    return {
        "total_capas": total,
        "avg_closure_days": avg_closure,
        "closure_rate_pct": closure_rate,
        "by_status": by_status,
        "overdue_count": overdue,
        "avg_days_by_severity": avg_days_by_severity,
    }


# ── Dashboard ──

@app.get("/api/dashboard")
def get_dashboard(client_key: str = ""):
    stats = get_dashboard_stats(client_key=client_key or None)

    # Enhance with nc_trend_summary (last 3 months)
    nc_trends_data = get_nc_trends(months=3, project_id="")
    stats["nc_trend_summary"] = {
        "months": nc_trends_data["months"],
        "major_nc": nc_trends_data["major_nc"],
        "minor_nc": nc_trends_data["minor_nc"],
    }

    # Upcoming surveillance placeholder
    stats["upcoming_surveillance"] = []

    # AI provider health from router
    from app.services.ai.router import _provider_health
    healthy = {p: _provider_health.get(p, 0) < 3 for p in ("nemotron_ultra", "llama_70b", "qwen3_coder", "local")}
    stats["ai_provider_health"] = healthy

    return stats


@app.get("/api/jobs")
def list_jobs(limit: int = 20, offset: int = 0, search: str = ""):
    return {'jobs': db.list_jobs(limit=limit, offset=offset, search=search)}


@app.get("/api/stats")
def get_stats():
    """Return aggregated analytics from all audit generation jobs for the Dashboard."""
    return db.get_stats()


# ── Export & Reporting Endpoints ──────────────────────────────────────────

@app.get("/api/export/csv", summary="Export dataset as CSV", tags=["Export"])
def export_csv(dataset: str = "nc_trends", months: int = 6, project_id: str = ""):
    """Export analytics data as CSV. Supported datasets: nc_trends, project_health, capa_metrics, ai_usage."""
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


@app.get("/api/export/report", summary="Generate PDF summary report", tags=["Export"])
def export_report(report_type: str = "compliance_summary", project_id: str = ""):
    """Generate PDF report. Supported types: compliance_summary, project_overview."""
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


@app.get("/api/progress/{job_id}")
async def stream_progress(job_id: str):
    """SSE endpoint for real-time job progress updates."""
    async def event_stream():
        last_status = None
        last_progress = -1
        while True:
            job = db.get_job(job_id)
            entry = _get_progress(job_id)

            if not entry and not job:
                yield 'event: error\ndata: {"error": "job_not_found"}\n\n'
                break

            status = (entry or job).get('status', 'unknown')
            progress = (entry or job).get('progress', 0)
            current_doc = (entry or job).get('current_doc', '')

            if status != last_status or progress != last_progress:
                data = json.dumps({
                    'status': status,
                    'progress': progress,
                    'current_doc': current_doc,
                })
                yield f'data: {data}\n\n'
                last_status = status
                last_progress = progress

            if status in ('done', 'error'):
                if status == 'done':
                    results = None
                    if entry and entry.get('results'):
                        results = entry['results']
                    yield f'event: complete\ndata: {json.dumps({"results": results, "download_url": (entry or {}).get("download_url", "")})}\n\n'
                break

            await asyncio.sleep(1.5)

    return StreamingResponse(event_stream(), media_type='text/event-stream')


@app.get("/api/compliance/standards/{standard_id}/clauses")
def get_standard_clauses(standard_id: str):
    """Return flattened clause data for a given standard for compliance checklist."""
    try:
        raw = get_clause_data(standard_id)
        annex = get_annex_a_data(standard_id)
        items = []
        seen = set()

        # Framework standards (ISO 31000, ISO 10002): {title, sections: {id: {...}}}
        if isinstance(raw, dict) and isinstance(raw.get('sections'), dict):
            for sid, section in raw['sections'].items():
                items.append({
                    'id': sid,
                    'title': section.get('title', ''),
                    'description': section.get('evidence', ''),
                    'sub_items': list(section.get('sub_sections', {}).values()) if isinstance(section.get('sub_sections'), dict) else [],
                })
        else:
            for key, c in (raw if isinstance(raw, dict) else {}).items():
                num = c.get('clause', c.get('id', key))
                if num in seen:
                    continue
                seen.add(num)
                items.append({
                    'id': num,
                    'title': c.get('title', ''),
                    'description': c.get('description', c.get('text', '')),
                })

        return {
            'standard_id': standard_id,
            'clauses': items,
            'annex_a': annex or {},
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f'Standard not found: {str(e)}')


@app.get("/api/compliance/assessment/{standard_key}")
def get_compliance_assessment(standard_key: str):
    from app.services.db import load_compliance_assessment
    data = load_compliance_assessment(standard_key)
    return {'standard_key': standard_key, 'assessments': data or {}}


@app.put("/api/compliance/assessment/{standard_key}")
def save_compliance_assessment(standard_key: str, data: dict):
    from app.services.db import save_compliance_assessment
    assessments = data.get('assessments', {})
    save_compliance_assessment(standard_key, assessments)
    return {'status': 'ok', 'standard_key': standard_key}


# ── Template Management ────────────────────────────────────────────────────

from app.services.template_manager import get_checklist_is_excel
from app.services.template_manager import TEMPLATE_MAP as DOC_TEMPLATES
from app.services.template_manager import CHECKLIST_TEMPLATES, TEMPLATES_DIR


@app.get("/api/templates")
def list_templates():
    """List all available templates with their document type mappings."""
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


@app.post("/api/templates/upload")
async def upload_template(file: UploadFile = File(...)):
    """Upload a new template file to the templates directory."""
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


@app.delete("/api/templates/{filename:path}")
def delete_template(filename: str):
    """Delete a template file from the templates directory."""
    fname = sanitize_filename(filename)
    path = os.path.join(TEMPLATES_DIR, fname)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f'Template "{fname}" not found')
    os.remove(path)
    return {'success': True, 'filename': fname}


# ── Standalone Audit Plan Generator ───────────────────────────────────────

@app.post("/api/audit_plan/generate", summary="Generate standalone Audit Plan", tags=["Audit Plan"])
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
    """Generate a standalone TÜV-branded Audit Plan Word document for client pre-approval."""
    if not client_name or not start_date or not end_date:
        raise HTTPException(status_code=400, detail="client_name, start_date, end_date are required")

    stds = json.loads(standards) if standards else []
    team_names = [t.strip() for t in audit_team.split(",") if t.strip()] if audit_team else []
    schedule = json.loads(daily_schedule) if daily_schedule else []

    # Build standard label
    from app.config import ISO_STANDARDS
    std_labels = [ISO_STANDARDS.get(s, s) for s in stds]
    standard_label = " / ".join(std_labels) if std_labels else "ISO Standard"

    # Build stage label
    stage_map = {
        "stage1": "Stage 1 — Readiness Review",
        "stage2": "Stage 2 — Certification Audit",
        "surveillance": "Surveillance Audit",
        "recertification": "Recertification Audit",
        "transfer": "Transfer Audit",
    }
    stage_label = stage_map.get(audit_type, "Stage 2 — Certification Audit")

    # Build audit team with roles
    team_data = []
    for i, name in enumerate(team_names):
        role = "Lead Auditor" if i == 0 else "Auditor"
        team_data.append({"name": name, "role": role, "days": ""})

    # Build daily schedule if not provided
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


# ── Audit Program & Live Audit Execution ──────────────────────────────────

# --- Program CRUD ---

@app.post("/api/audit_programs", summary="Create audit program", tags=["Audit Execution"])
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


@app.get("/api/audit_programs", summary="List audit programs", tags=["Audit Execution"])
def list_audit_programs(client_key: str = "", status: str = ""):
    programs = list_programs(client_key=client_key or None, status=status or None)
    return {"programs": [p.to_dict() for p in programs]}


@app.get("/api/audit_programs/{program_id}", summary="Get audit program overview", tags=["Audit Execution"])
def get_audit_program_overview(program_id: str):
    overview = get_program_overview(program_id)
    if not overview:
        raise HTTPException(status_code=404, detail="Program not found")
    return overview


@app.put("/api/audit_programs/{program_id}", summary="Update audit program", tags=["Audit Execution"])
def update_audit_program_endpoint(program_id: str, **kwargs):
    if "standards" in kwargs and isinstance(kwargs["standards"], str):
        kwargs["standards"] = json.loads(kwargs["standards"])
    if "audit_team" in kwargs and isinstance(kwargs["audit_team"], str):
        kwargs["audit_team"] = [t.strip() for t in kwargs["audit_team"].split(",") if t.strip()]
    program = update_program(program_id, **kwargs)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program.to_dict()


@app.delete("/api/audit_programs/{program_id}", summary="Delete audit program", tags=["Audit Execution"])
def delete_audit_program(program_id: str):
    if delete_program(program_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Program not found")


# --- Program Entries (time slots) ---

@app.post("/api/audit_programs/{program_id}/entries", summary="Add program entry", tags=["Audit Execution"])
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


@app.get("/api/audit_programs/{program_id}/entries", summary="List program entries", tags=["Audit Execution"])
def list_program_entries(program_id: str, day: int = 0):
    day_val = day if day > 0 else None
    entries = list_entries(program_id, day=day_val)
    return {"entries": [e.to_dict() for e in entries]}


@app.put("/api/entries/{entry_id}", summary="Update program entry", tags=["Audit Execution"])
def update_program_entry_endpoint(entry_id: str, **kwargs):
    if "clause_refs" in kwargs and isinstance(kwargs["clause_refs"], str):
        kwargs["clause_refs"] = json.loads(kwargs["clause_refs"])
    entry = update_entry(entry_id, **kwargs)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.to_dict()


@app.delete("/api/entries/{entry_id}", summary="Delete program entry", tags=["Audit Execution"])
def delete_program_entry(entry_id: str):
    delete_entry(entry_id)
    return {"success": True}


# --- Clause Checklist ---

@app.post("/api/audit_programs/{program_id}/checklist/build", summary="Build checklist from standards", tags=["Audit Execution"])
def build_program_checklist(program_id: str):
    """Auto-generate clause checklist items from program standards."""
    items = build_checklist_for_program(program_id)
    return {"success": True, "total": len(items), "items": [i.to_dict() for i in items]}


@app.get("/api/audit_programs/{program_id}/checklist", summary="Get clause checklist", tags=["Audit Execution"])
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


@app.get("/api/audit_programs/{program_id}/checklist/export", summary="Export checklist grouped by standard", tags=["Audit Execution"])
def export_program_checklist(program_id: str):
    grouped = get_checklist_export(program_id)
    return {"standards": grouped}


@app.put("/api/checklist/{item_id}", summary="Update checklist item", tags=["Audit Execution"])
def update_checklist_item_endpoint(item_id: str, **kwargs):
    item = update_checklist_item(item_id, **kwargs)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return item.to_dict()


@app.post("/api/audit_programs/{program_id}/checklist/bulk", summary="Bulk update checklist", tags=["Audit Execution"])
def bulk_update_checklist_endpoint(program_id: str, updates: dict = None):
    """Bulk update checklist items. Body: {item_id: {field: value}}"""
    if not updates:
        raise HTTPException(status_code=400, detail="updates dict required")
    results = bulk_update_checklist(program_id, updates)
    return {"updated": len(results), "items": [i.to_dict() for i in results]}


# --- Evidence Register ---

@app.post("/api/audit_programs/{program_id}/evidence", summary="Add evidence", tags=["Audit Execution"])
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


@app.get("/api/audit_programs/{program_id}/evidence", summary="List evidence", tags=["Audit Execution"])
def list_evidence_endpoint(program_id: str, clause_ref: str = "", standard: str = ""):
    items = list_evidence_register(
        program_id,
        clause_ref=clause_ref or None,
        standard=standard or None,
    )
    return {"evidence": [e.to_dict() for e in items], "total": len(items)}


@app.put("/api/evidence/{evidence_id}", summary="Update evidence entry", tags=["Audit Execution"])
def update_evidence_endpoint(evidence_id: str, **kwargs):
    ev = update_evidence_entry(evidence_id, **kwargs)
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return ev.to_dict()


@app.delete("/api/evidence/{evidence_id}", summary="Delete evidence entry", tags=["Audit Execution"])
def delete_evidence_endpoint(evidence_id: str):
    delete_evidence_entry(evidence_id)
    return {"success": True}


# --- Daily Summaries ---

@app.get("/api/audit_programs/{program_id}/daily/{day}", summary="Get daily summary", tags=["Audit Execution"])
def get_daily_summary(program_id: str, day: int, date: str = ""):
    ds = get_or_create_daily_summary(program_id, day, date)
    return ds.to_dict()


@app.put("/api/daily_summaries/{summary_id}", summary="Update daily summary", tags=["Audit Execution"])
def update_daily_summary_endpoint(summary_id: str, **kwargs):
    ds = update_daily_summary(summary_id, **kwargs)
    if not ds:
        raise HTTPException(status_code=404, detail="Summary not found")
    return ds.to_dict()


@app.get("/api/audit_programs/{program_id}/daily", summary="List daily summaries", tags=["Audit Execution"])
def list_daily_summaries_endpoint(program_id: str):
    items = list_daily_summaries(program_id)
    return {"summaries": [s.to_dict() for s in items]}


# ── AI Model & Provider Endpoints ─────────────────────────────────────────

@app.get("/api/ai/models/status", summary="AI model status dashboard", tags=["AI"])
def get_ai_models_status():
    """Return status and performance data for all registered AI models."""
    perf = get_model_performance()
    models = []
    for name, caps in ALL_MODELS.items():
        p = perf.get(name, {})
        healthy = _prov_health.get(name, 0) < 3
        first_strength = caps.strengths[0] if caps.strengths else caps.tier
        models.append({
            "name": name,
            "tier": first_strength,
            "tier_category": caps.tier,
            "context_length": caps.context_length,
            "provider": caps.provider,
            "available": True,
            "healthy": healthy,
            "consecutive_fails": _prov_health.get(name, 0),
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


@app.post("/api/ai/validate", summary="Validate AI output quality", tags=["AI"])
def validate_ai_output(data: dict):
    task_type = data.get("task_type", "")
    ai_output = data.get("ai_output", {})
    model_used = data.get("model_used", "")
    if not task_type or not ai_output:
        raise HTTPException(status_code=400, detail="task_type and ai_output required")
    validator = ExportValidator(task_type)
    report = validator.get_quality_report(ai_output, model_used)
    return report


@app.get("/api/ai/quality-history", summary="Quality scores over time", tags=["AI"])
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


# ── Refinement Endpoints ──────────────────────────────────────────────────

@app.get("/api/refine/fields/{doc_type}", summary="List refinable fields for document type", tags=["Refinement"])
def list_refinable_fields(doc_type: str):
    return {'fields': get_refinable_fields(doc_type)}


@app.get("/api/refine/versions/{job_id}/{doc_type}", summary="Get field version history", tags=["Refinement"])
def get_versions_endpoint(job_id: str, doc_type: str, field: str = ''):
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    if field:
        return {'versions': get_field_versions(job_data, doc_type, field)}
    results = job_data.get('results') or {}
    doc_info = results.get(doc_type)
    versions = doc_info.get('_versions', {}) if isinstance(doc_info, dict) else {}
    return {'versions': versions}


@app.post("/api/refine", summary="Refine a single document field via AI", tags=["Refinement"])
async def refine_endpoint(request: Request):
    body = await request.json()
    job_id = body.get("job_id", "")
    doc_type = body.get("doc_type", "")
    field = body.get("field", "")
    instruction = body.get("instruction", "")
    api_key = body.get("api_key", "")
    if not all([job_id, doc_type, field, instruction]):
        raise HTTPException(status_code=400, detail="job_id, doc_type, field, and instruction are required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    result = refine_field(job_data, doc_type, field, instruction, api_key=api_key)
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    return result


@app.post("/api/refine/bulk/{job_id}/{doc_type}", summary="Refine all fields for a document type", tags=["Refinement"])
async def bulk_refine_endpoint(job_id: str, doc_type: str, request: Request):
    body = await request.json()
    instruction = body.get("instruction", "")
    api_key = body.get("api_key", "")
    if not instruction:
        raise HTTPException(status_code=400, detail="instruction is required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    result = bulk_refine(job_data, doc_type, instruction, api_key=api_key)
    return result


# ── AI Chat Endpoints ─────────────────────────────────────────────────────

@app.post("/api/chat", summary="Chat with AI about generated documents", tags=["AI Chat"])
async def chat_endpoint(request: Request):
    body = await request.json()
    job_id = body.get("job_id", "")
    message = body.get("message", "")
    history = body.get("history", [])
    if not job_id or not message:
        raise HTTPException(status_code=400, detail="job_id and message are required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    context = build_chat_context(job_data)
    result = chat_with_ai(message, context, history)
    return result


@app.post("/api/chat/stream", summary="Stream chat response via SSE", tags=["AI Chat"])
async def chat_stream_endpoint(request: Request):
    body = await request.json()
    job_id = body.get("job_id", "")
    message = body.get("message", "")
    history = body.get("history", [])
    if not job_id or not message:
        raise HTTPException(status_code=400, detail="job_id and message are required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    context = build_chat_context(job_data)

    async def event_stream():
        for token in chat_stream(message, context, history):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type='text/event-stream')


@app.post("/api/edit-field", summary="Directly edit a document field (no AI)", tags=["Refinement"])
async def edit_field_endpoint(request: Request):
    body = await request.json()
    job_id = body.get("job_id", "")
    doc_type = body.get("doc_type", "")
    field = body.get("field", "")
    value = body.get("value", "")
    if not all([job_id, doc_type, field]):
        raise HTTPException(status_code=400, detail="job_id, doc_type, and field are required")
    job_data = _get_progress(job_id)
    if not job_data:
        job_data = db.get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    doc_info = (job_data.get('results') or {}).get(doc_type)
    if not doc_info or not isinstance(doc_info, dict):
        raise HTTPException(status_code=404, detail="Document not found")
    if field not in RF.get(doc_type, []):
        raise HTTPException(status_code=400, detail=f"Field {field} is not editable for {doc_type}")
    doc_data = doc_info.get('_data')
    if doc_data is None:
        raise HTTPException(status_code=404, detail="Document data not found")
    old_val = doc_data.get(field)
    doc_data[field] = value
    if '_versions' not in doc_info:
        doc_info['_versions'] = {}
    tim = time.time()
    if field not in doc_info['_versions']:
        doc_info['_versions'][field] = []
    doc_info['_versions'][field].append({'value': value, 'timestamp': tim, 'instruction': 'manual edit'})
    _update_progress(job_id, results=job_data.get('results'))
    if not job_data.get('_ephemeral'):
        db.save_job(job_id, json.dumps(job_data, ensure_ascii=False, default=str))
    return {'field': field, 'value': value, 'previous_value': old_val, 'success': True}


@app.on_event("startup")
async def startup():
    cleanup_old_jobs()


# ── Serve frontend static files (for Railway single-container deployment) ──
frontend_dir = os.environ.get("FRONTEND_STATIC_DIR", "")
if frontend_dir and os.path.isdir(frontend_dir):
    try:
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        logger.info("Frontend static files mounted from %s", frontend_dir)
    except Exception as e:
        logger.warning("Could not mount frontend: %s", e)
