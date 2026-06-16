from fastapi import APIRouter, HTTPException

from app.services.client_config import get_client, list_clients, get_doc_code, validate_client_data

router = APIRouter(tags=["Clients"])


@router.get("/api/clients")
def get_clients():
    return {'clients': list_clients()}


@router.get("/api/clients/{client_key}")
def get_client_detail(client_key: str):
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


@router.post("/api/clients/{client_key}/validate")
def validate_client_doc(client_key: str, data: dict):
    errors = validate_client_data(client_key, data)
    return {'valid': len(errors) == 0, 'errors': errors}


@router.get("/api/clients/{client_key}/doc_code")
def generate_doc_code(client_key: str, doc_type: str = "DOC", sequence: int = 1):
    client = get_client(client_key)
    if not client:
        raise HTTPException(status_code=404, detail=f'Client not found: {client_key}')
    return {
        'doc_code': get_doc_code(client_key, doc_type, sequence),
        'prefix': client.doc_code_prefix,
    }
