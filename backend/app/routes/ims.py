from fastapi import APIRouter, HTTPException, Form
import json

from app.services.ims import (
    get_ims_mapping, get_integrated_clause_list,
    get_shared_docs, get_unique_requirements,
    generate_ims_gap_analysis,
    IMS_MAPPINGS,
)

router = APIRouter(tags=["IMS Multi-Standard"])


@router.get("/api/ims/mapping")
def get_ims_mapping_endpoint(standards: str = ""):
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required (comma-separated)")
    std_list = [s.strip() for s in standards.split(",")]
    mapping = get_ims_mapping(std_list)
    if not mapping:
        return {"available_mappings": [list(k) for k in IMS_MAPPINGS.keys()], "message": "No mapping for this combination"}
    return mapping


@router.get("/api/ims/clauses")
def get_ims_clauses_endpoint(standards: str = ""):
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    clauses = get_integrated_clause_list(std_list)
    return {"standards": std_list, "clauses": clauses, "total": len(clauses)}


@router.get("/api/ims/shared-docs")
def get_ims_shared_docs_endpoint(standards: str = ""):
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    docs = get_shared_docs(std_list)
    return {"standards": std_list, "shared_documents": docs, "total": len(docs)}


@router.get("/api/ims/unique-requirements")
def get_ims_unique_endpoint(standards: str = ""):
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    unique = get_unique_requirements(std_list)
    return {"standards": std_list, "unique_requirements": unique}


@router.post("/api/ims/gap-analysis")
def ims_gap_analysis_endpoint(standards: str = Form(""), compliance_data: str = Form("{}")):
    if not standards:
        raise HTTPException(status_code=400, detail="standards parameter required")
    std_list = [s.strip() for s in standards.split(",")]
    data = json.loads(compliance_data) if compliance_data else {}
    result = generate_ims_gap_analysis(std_list, data)
    return result
