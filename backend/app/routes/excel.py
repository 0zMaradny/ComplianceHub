from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse
import os

from app.config import OUTPUT_FOLDER
from app.services.client_config import get_client


router = APIRouter(tags=["Excel Export"])


@router.post("/api/generate_excel")
def generate_excel_endpoint(
    client_key: str = Form(''),
    doc_type: str = Form('risk_register'),
):
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
