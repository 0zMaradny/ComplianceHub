import json
import time
from fastapi import APIRouter, HTTPException, Request

from app.services.doc_refiner import refine_field, bulk_refine, get_field_versions, get_refinable_fields, REFINABLE_FIELDS as RF
from app.routes import _get_progress, _update_progress
from app.services import db

router = APIRouter(tags=["Refinement"])


@router.get("/api/refine/fields/{doc_type}", summary="List refinable fields for document type")
def list_refinable_fields(doc_type: str):
    return {'fields': get_refinable_fields(doc_type)}


@router.get("/api/refine/versions/{job_id}/{doc_type}", summary="Get field version history")
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


@router.post("/api/refine", summary="Refine a single document field via AI")
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


@router.post("/api/refine/bulk/{job_id}/{doc_type}", summary="Refine all fields for a document type")
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


@router.post("/api/edit-field", summary="Directly edit a document field (no AI)")
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
