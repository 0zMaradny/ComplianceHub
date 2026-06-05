import os
import json
import zipfile
import uuid
import shutil
import threading
import time
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import (
    UPLOAD_FOLDER, OUTPUT_FOLDER, ISO_STANDARDS,
    OUTPUT_DOCUMENTS, DOC_LABELS, STANDARD_CATEGORIES
)
from app.services.file_parser import extract_audit_notes, extract_manday_data
from app.services.ai_pipeline import generate_document as ai_generate, extract_shared_context
from app.services.document_generator import generate_document_file
from app.services.template_manager import get_template_path
from app.services.pdf_converter import convert_to_pdf
from app.services.offline_generator import generate_all as offline_generate_all

app = FastAPI(title="ComplianceHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

progress_store: dict = {}
MAX_JOB_AGE = 3600


def cleanup_old_jobs():
    now = time.time()
    for jid in list(progress_store.keys()):
        entry = progress_store.get(jid)
        if entry and (now - entry.get('created_at', 0)) > MAX_JOB_AGE:
            del progress_store[jid]
            for d in [os.path.join(UPLOAD_FOLDER, jid), os.path.join(OUTPUT_FOLDER, jid)]:
                shutil.rmtree(d, ignore_errors=True)


def _make_doc_result(output_dir, template_path, standard_key, doc_type, doc_data):
    """Generate a DOCX file from data, return doc_info dict or None."""
    path = generate_document_file(doc_type, doc_data, output_dir, template_path, standard_key)
    if not path:
        return None
    filename = os.path.basename(path)
    doc_info = {'path': path, 'filename': filename}
    pdf_path = convert_to_pdf(path)
    if pdf_path:
        doc_info['pdf_path'] = pdf_path
    return doc_info


def generate_background(job_id, api_key, notes_data, manday_data, standards_full, selected_standards):
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    os.makedirs(output_dir, exist_ok=True)

    template_path = os.path.join(job_dir, 'checklist_template.docx')
    if not os.path.exists(template_path):
        template_path = None

    standard_key = selected_standards[0] if selected_standards else None
    notes_text = notes_data['text']
    manday_text = manday_data['text']

    progress_store[job_id]['status'] = 'extracting_context'
    progress_store[job_id]['progress'] = 10
    progress_store[job_id]['current_doc'] = 'Analyzing documents...'

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
        progress_store[job_id]['status'] = 'generating'
        progress_store[job_id]['current_doc'] = label
        progress_store[job_id]['doc_progress'][doc_type] = 'generating'
        base_progress = 20 + int((idx / total) * 70)
        progress_store[job_id]['progress'] = base_progress

        # 1) Try AI pipeline (router → local/cloud provider)
        doc_data = None
        ai_error = None
        if True:
            try:
                ai_result = ai_generate(
                    api_key, notes_text, manday_text,
                    standards_full, doc_type, shared_context
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
            doc_info = _make_doc_result(output_dir, template_path, standard_key, doc_type, doc_data)
            if doc_info:
                if not client_name or client_name == 'Client':
                    client_name = doc_data.get('client_name', 'Client')
                results[doc_type] = doc_info
                progress_store[job_id]['doc_progress'][doc_type] = 'done'
                progress_store[job_id]['progress'] = 20 + int(((idx + 1) / total) * 70)
                continue

        results[doc_type] = {'error': ai_error or 'Document generation failed'}
        progress_store[job_id]['doc_progress'][doc_type] = 'error'
        progress_store[job_id]['progress'] = 20 + int(((idx + 1) / total) * 70)

    progress_store[job_id]['progress'] = 95
    progress_store[job_id]['current_doc'] = 'Creating package...'

    safe_name = client_name.replace(' ', '_')
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

    progress_store[job_id].update({
        'status': 'done',
        'progress': 100,
        'current_doc': None,
        'results': results,
        'download_url': f'/api/download/{job_id}',
        'zip_name': zip_name,
    })


@app.get("/api/standards")
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
    content = await audit_notes.read()
    with open(notes_path, 'wb') as f:
        f.write(content)
    content = await manday.read()
    with open(manday_path, 'wb') as f:
        f.write(content)

    if checklist_template and checklist_template.filename:
        template_path = os.path.join(job_dir, 'checklist_template.docx')
        content = await checklist_template.read()
        with open(template_path, 'wb') as f:
            f.write(content)

    try:
        notes_data = extract_audit_notes(notes_path)
        manday_data = extract_manday_data(manday_path)
    except Exception as e:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=f'Failed to parse documents: {str(e)}')

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
    }

    if api_key:
        standards_full = [ISO_STANDARDS.get(s, s) for s in selected_standards]
        t = threading.Thread(
            target=generate_background,
            args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards),
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
):
    selected_standards = json.loads(standards)

    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    output_dir = os.path.join(OUTPUT_FOLDER, job_id)

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
    }

    t = threading.Thread(
        target=generate_background,
        args=(job_id, api_key, notes_data, manday_data, standards_full, selected_standards),
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
    entry = progress_store.get(job_id)
    if not entry:
        raise HTTPException(status_code=404, detail='Job not found')

    result_data = entry.get('results')
    cleaned_results = None
    if result_data:
        cleaned_results = {}
        for doc_type, result in result_data.items():
            cleaned = {}
            for k, v in result.items():
                if k not in ('path', 'pdf_path'):
                    cleaned[k] = v
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
    entry = progress_store.get(job_id)
    zip_path = os.path.join(OUTPUT_FOLDER, f'{job_id}.zip')
    if os.path.exists(zip_path):
        zip_name = entry.get('zip_name', 'TUV_Audit_Package.zip') if entry else 'TUV_Audit_Package.zip'
        return FileResponse(zip_path, filename=zip_name, media_type='application/zip')
    raise HTTPException(status_code=404, detail='Package not found')


@app.get("/api/download_doc/{job_id}/{doc_type}")
def download_doc(job_id: str, doc_type: str):
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


@app.on_event("startup")
async def startup():
    cleanup_old_jobs()
