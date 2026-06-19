import os
import time
import subprocess
from fastapi import APIRouter, Request

from app.config import ISO_STANDARDS, STANDARD_CATEGORIES, OUTPUT_DOCUMENTS, DOC_LABELS, AUDIT_PACKAGE_DOCS, STANDALONE_DOCS
from app.settings import TUNNEL_MODE as _TUNNEL_MODE_CONFIG

TUNNEL_URL_FILE = "/tmp/compliancehub-url.txt"

router = APIRouter(tags=["System"])

def _read_tunnel_url() -> str:
    if os.path.exists(TUNNEL_URL_FILE):
        try:
            with open(TUNNEL_URL_FILE) as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""

def _read_tunnel_mode() -> str:
    pid_dir = "/tmp/compliancehub-pids"
    tunnel_pid_file = os.path.join(pid_dir, "tunnel.pid")
    if os.path.exists(tunnel_pid_file):
        return _TUNNEL_MODE_CONFIG
    return "disconnected"


@router.get("/api/health")
def health():
    from app.services.surveillance import check_overdue_cycles
    check_overdue_cycles()
    import shutil
    total, used, free = shutil.disk_usage("/")
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": time.time(),
        "database": "connected",
        "disk_free_mb": free // (1024 * 1024),
    }


@router.get("/api/diagnostics")
def diagnostics():
    import py_compile
    errors = []
    for root, dirs, files in os.walk("app"):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(f"Syntax: {path}: {e}")
    from app.services.db import init_db
    try:
        init_db()
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
        errors.append(f"DB: {e}")
    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "db": db_status,
        "version": "2.0.0",
        "timestamp": time.time(),
    }


@router.get("/api/tunnel", summary="Get tunnel status")
def get_tunnel():
    url = _read_tunnel_url()
    mode = _read_tunnel_mode()
    return {
        "tunnel_url": url,
        "tunnel_mode": mode,
        "connected": bool(url),
    }


@router.post("/api/tunnel-url", summary="Receive tunnel URL from watchdog")
async def set_tunnel_url(request: Request):
    body = await request.json()
    url = body.get("tunnel_url", "")
    if url:
        os.makedirs(os.path.dirname(TUNNEL_URL_FILE), exist_ok=True)
        with open(TUNNEL_URL_FILE, "w") as f:
            f.write(url)
        return {"status": "ok", "tunnel_url": url}
    return {"status": "error", "message": "No tunnel_url provided"}


@router.post("/api/tunnel-retry", summary="Force tunnel reconnection")
def retry_tunnel():
    try:
        subprocess.run(["pkill", "-f", "tunnel.sh"], capture_output=True, timeout=5)
        subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True, timeout=5)
        subprocess.run(["pkill", "-f", "serveo.net"], capture_output=True, timeout=5)
        return {"status": "ok", "message": "Tunnel processes terminated. Watchdog will auto-restart."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/api/standards", summary="List all ISO standards",
            description="Returns all supported ISO standards, categories, and document types.")
def get_standards():
    return {
        'standards': ISO_STANDARDS,
        'categories': STANDARD_CATEGORIES,
        'documents': OUTPUT_DOCUMENTS,
        'doc_labels': DOC_LABELS,
        'audit_package_docs': AUDIT_PACKAGE_DOCS,
        'standalone_docs': STANDALONE_DOCS,
    }
