import os
import json
import mimetypes
import zipfile
import uuid
import shutil
import threading
import time
import asyncio
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

logger = logging.getLogger(__name__)

from app.config import (
    UPLOAD_FOLDER, OUTPUT_FOLDER, ISO_STANDARDS,
    OUTPUT_DOCUMENTS, DOC_LABELS,
)
from app.utils import sanitize_filename, validate_job_id
from app.services.file_parser import extract_audit_notes, extract_manday_data, extract_manday_tables
from app.services.ai_pipeline import generate_document as ai_generate, extract_shared_context
from app.services.document_generator import generate_document_file
from app.services.pdf_generator import generate_pdf_file
from app.services.offline_generator import generate_all as offline_generate_all
from app.services import db
from app.routes import (
    progress_store, _progress_lock, _update_progress, _get_progress, MAX_FILE_SIZE
)

router = APIRouter(tags=["Document Generation"])

# MIME type allowlist: extension → set of allowed MIME types
_MIME_ALLOWLIST = {
    '.docx': {'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/zip'},
    '.txt': {'text/plain'},
    '.pdf': {'application/pdf'},
    '.png': {'image/png'},
    '.jpg': {'image/jpeg'},
    '.jpeg': {'image/jpeg'},
    '.tiff': {'image/tiff'},
    '.tif': {'image/tiff'},
    '.bmp': {'image/bmp'},
    '.gif': {'image/gif'},
}


def _validate_mime_type(content: bytes, ext: str) -> bool:
    """Validate file content against expected MIME type for the extension."""
    allowed = _MIME_ALLOWLIST.get(ext)
    if not allowed:
        return False
    # Try python-magic first (most accurate), fall back to mimetypes
    try:
        import magic
        detected = magic.from_buffer(content[:4096], mime=True)
        return detected in allowed
    except ImportError:
        pass
    # Fallback: check magic bytes directly (already done per-type in upload handler)
    return True


def _make_doc_result(output_dir, template_path, standard_key, doc_type, doc_data, client_key=None):
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

    offline_cache = None
    _offline_timer = None

    results = {}
    total = len(OUTPUT_DOCUMENTS)
    client_name = 'Client'
    completed = 0
    _nonlocal_lock = threading.Lock()

    def process_doc(doc_type):
        nonlocal offline_cache, client_name, _offline_timer
        try:
            _t_start = time.perf_counter()
            with _progress_lock:
                if job_id in progress_store:
                    progress_store[job_id]['doc_progress'][doc_type] = 'generating'

            doc_data = None
            ai_error = None
            _ai_attempted = False

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
                        if '_model_used' in ai_result:
                            _update_progress(job_id, provider_used=ai_result['_model_used'])
                    else:
                        ai_error = ai_result['error']
                except Exception as e:
                    ai_error = str(e)

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

            if doc_data:
                if client_key:
                    doc_data['client_key'] = client_key
                doc_data.pop('_model_used', None)
                doc_data.pop('_quality_score', None)
                doc_data.pop('_response_time_ms', None)
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
        except Exception as e:
            logger.error('JOB %s doc %s CRASHED: %s', job_id, doc_type, e)
            return doc_type, {'error': str(e)}

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(process_doc, dt): dt for dt in OUTPUT_DOCUMENTS}
        for future in as_completed(futures):
            dt, result = future.result()
            results[dt] = result
            completed += 1
            _update_progress(job_id, status='generating', current_doc=DOC_LABELS.get(dt, dt),
                             progress=20 + int((completed / total) * 70))

    # All futures complete — ensure all file handles are flushed before packaging
    import gc
    gc.collect()

    _update_progress(job_id, progress=95, current_doc='Creating package...')

    try:
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

        # Safe to cleanup input directory after zip is fully written
        shutil.rmtree(job_dir, ignore_errors=True)
    except Exception as e:
        logger.error('JOB %s packaging failed: %s', job_id, e)
        _update_progress(job_id, status='error', error=str(e))
        return

    _update_progress(job_id, status='done', progress=100, current_doc=None,
                     results=results, download_url=f'/api/download/{job_id}',
                     zip_name=zip_name)

    _total = time.perf_counter() - _t0
    logger.info('JOB %s TOTAL: %.2fs for %d docs (%.2f avg)', job_id, _total, total, _total / total)


@router.post("/api/upload")
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

    # Sanitize extension: only allow known safe extensions, strip path separators
    raw_ext = os.path.splitext(audit_notes.filename)[1].lower()
    safe_ext = re.sub(r'[^.a-z0-9]', '', raw_ext)[:10]  # Strip any non-alphanumeric chars
    if not safe_ext or safe_ext not in ('.docx', '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'):
        safe_ext = '.bin'  # Fallback for unknown types
    notes_path = os.path.join(job_dir, f'audit_notes{safe_ext}')
    manday_path = os.path.join(job_dir, 'manday.docx')

    content = await audit_notes.read()
    if len(content) > MAX_FILE_SIZE:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=413, detail=f'Audit notes file exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
    if safe_ext == '.docx' and content[:2] != b'PK':
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail='Invalid audit notes file: not a valid DOCX')
    if safe_ext == '.txt':
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail='Invalid audit notes file: not a valid text file')
    if safe_ext == '.pdf' and content[:5] != b'%PDF-':
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail='Invalid audit notes file: not a valid PDF')
    if safe_ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
        valid_headers = {
            '.png': (b'\x89PNG',),
            '.jpg': (b'\xff\xd8\xff',),
            '.jpeg': (b'\xff\xd8\xff',),
            '.bmp': (b'BM',),
            '.gif': (b'GIF8',),
        }
        expected = valid_headers.get(safe_ext, ())
        if expected and not any(content[:len(h)] == h for h in expected):
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f'Invalid image file: header does not match {safe_ext} format')
    if safe_ext in ('.tiff', '.tif'):
        if content[:4] not in (b'II\x2a\x00', b'MM\x00\x2a'):
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail='Invalid TIFF file: unrecognized header')
    with open(notes_path, 'wb') as f:
        f.write(content)

    content = await manday.read()
    if len(content) > MAX_FILE_SIZE:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=413, detail=f'Manday file exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
    # Validate manday file is a valid DOCX (PK header)
    if not manday.filename.lower().endswith('.docx') or content[:2] != b'PK':
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail='Invalid manday file: must be a valid DOCX')
    with open(manday_path, 'wb') as f:
        f.write(content)

    if checklist_template and checklist_template.filename:
        content = await checklist_template.read()
        if len(content) > MAX_FILE_SIZE:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=413, detail=f'Template file exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit')
        if not checklist_template.filename.lower().endswith('.docx') or content[:2] != b'PK':
            shutil.rmtree(job_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail='Invalid template file: must be a valid DOCX')
        template_path = os.path.join(job_dir, 'checklist_template.docx')
        with open(template_path, 'wb') as f:
            f.write(content)

    try:
        notes_data = extract_audit_notes(notes_path)
        manday_data = extract_manday_data(manday_path)
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f'Failed to parse documents: {str(e)}')
    if isinstance(notes_data, dict) and 'error' in notes_data:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f'Invalid audit notes file: {notes_data["error"]}')
    if isinstance(manday_data, dict) and 'error' in manday_data:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f'Invalid manday file: {manday_data["error"]}')

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


@router.post("/api/generate")
async def generate_docs(
    job_id: str = Form(...),
    api_key: str = Form(''),
    standards: str = Form('[]'),
    client_key: str = Form(''),
    manday_config: str = Form('null'),
):
    mc = json.loads(manday_config) if manday_config not in ('null', 'None', '') else None
    selected_standards = json.loads(standards)

    if not job_id:
        raise HTTPException(status_code=400, detail='Job ID is required')

    entry = _get_progress(job_id)
    if not entry:
        raise HTTPException(status_code=400, detail='Job not found')

    # Empty api_key → offline mode (template-based generation, no AI)
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    # Find audit notes file — supports .docx, .txt, .pdf, and image formats
    notes_path = None
    for f in os.listdir(job_dir):
        if f.startswith('audit_notes'):
            notes_path = os.path.join(job_dir, f)
            break
    if notes_path is None:
        raise HTTPException(status_code=400, detail='No audit notes file found for this job')

    manday_path = os.path.join(job_dir, 'manday.docx')
    notes_data = extract_audit_notes(notes_path)
    manday_data = extract_manday_data(manday_path)
    standards_full = [ISO_STANDARDS.get(s, s) for s in selected_standards]

    t = threading.Thread(
        target=generate_background,
        args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards, client_key or None, mc),
        daemon=True,
    )
    t.start()
    mode = 'offline' if not api_key else 'ai'
    return {'success': True, 'job_id': job_id, 'async': True, 'mode': mode, 'status_url': f'/api/status/{job_id}'}


@router.get("/api/status/{job_id}")
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


@router.get("/api/download/{job_id}")
def download(job_id: str):
    if not validate_job_id(job_id):
        raise HTTPException(status_code=400, detail='Invalid job ID')
    entry = _get_progress(job_id)
    zip_path = os.path.join(OUTPUT_FOLDER, f'{job_id}.zip')
    if os.path.exists(zip_path):
        zip_name = entry.get('zip_name', 'TUV_Audit_Package.zip') if entry else 'TUV_Audit_Package.zip'
        return FileResponse(zip_path, filename=zip_name, media_type='application/zip')
    raise HTTPException(status_code=404, detail='Package not found')


@router.get("/api/download_doc/{job_id}/{doc_type}")
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


@router.get("/api/download_doc/{job_id}/{doc_type}/pdf")
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


@router.get("/api/progress/{job_id}")
async def stream_progress(job_id: str):
    """SSE endpoint for real-time job progress updates."""
    from app.services import db as db_module

    async def event_stream():
        last_status = None
        last_progress = -1
        while True:
            job = db_module.get_job(job_id)
            entry = _get_progress(job_id)

            if not entry and not job:
                yield 'event: error\ndata: {"error": "job_not_found"}\n\n'
                break

            status = (entry or job).get('status', 'unknown')
            progress = (entry or job).get('progress', 0)
            current_doc = (entry or job).get('current_doc', '')
            provider_used = (entry or job).get('provider_used', '')

            if status != last_status or progress != last_progress:
                data = json.dumps({
                    'status': status,
                    'progress': progress,
                    'current_doc': current_doc,
                    'provider_used': provider_used,
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
