import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

from app.config import UPLOAD_FOLDER, OUTPUT_FOLDER
from app.settings import CORS_ORIGINS as _CORS_CONFIG, FRONTEND_STATIC_DIR

from app.routes import (
    _check_rate_limit, cleanup_old_jobs
)

from app.routes.system import router as system_router
from app.routes.documents import router as documents_router
from app.routes.excel import router as excel_router
from app.routes.clients import router as clients_router
from app.routes.compliance import router as compliance_router
from app.routes.projects import router as projects_router
from app.routes.surveillance import router as surveillance_router
from app.routes.ims import router as ims_router
from app.routes.analytics import router as analytics_router
from app.routes.export import router as export_router
from app.routes.audit_programs import router as audit_programs_router
from app.routes.templates import router as templates_router
from app.routes.ai import router as ai_router
from app.routes.refine import router as refine_router
from app.routes.chat import router as chat_router

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
        {"name": "Audit Plan", "description": "Standalone audit plan generation"},
    ],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

CORS_ORIGINS = _CORS_CONFIG
if CORS_ORIGINS == "*":
    cors_origins = ["*"]
else:
    cors_origins = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_origins != ["*"] and "*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    response.headers["X-Response-Time"] = f"{elapsed:.1f}ms"
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        client_id = request.client.host if request.client else "unknown"
        if not _check_rate_limit(client_id):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Try again later."},
            )
    return await call_next(request)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


app.include_router(system_router)
app.include_router(documents_router)
app.include_router(excel_router)
app.include_router(clients_router)
app.include_router(compliance_router)
app.include_router(projects_router)
app.include_router(surveillance_router)
app.include_router(ims_router)
app.include_router(analytics_router)
app.include_router(export_router)
app.include_router(audit_programs_router)
app.include_router(templates_router)
app.include_router(ai_router)
app.include_router(refine_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    cleanup_old_jobs()


frontend_dir = FRONTEND_STATIC_DIR
if frontend_dir and os.path.isdir(frontend_dir):
    try:
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        logger.info("Frontend static files mounted from %s", frontend_dir)
    except Exception as e:
        logger.warning("Could not mount frontend: %s", e)
