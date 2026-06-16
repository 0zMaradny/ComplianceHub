import threading
import time
import logging
import shutil
import os
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)

from app.config import UPLOAD_FOLDER, OUTPUT_FOLDER

progress_store: dict = {}
_progress_lock = threading.Lock()
MAX_JOB_AGE = 3600

_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = threading.Lock()
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 300
MAX_FILE_SIZE = 50 * 1024 * 1024

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


def _check_rate_limit(client_id: str) -> bool:
    now = time.time()
    with _rate_limit_lock:
        timestamps = _rate_limit_store[client_id]
        _rate_limit_store[client_id] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_limit_store[client_id]) >= RATE_LIMIT_MAX_REQUESTS:
            return False
        _rate_limit_store[client_id].append(now)
        return True


def _update_progress(job_id: str, **kwargs):
    with _progress_lock:
        if job_id in progress_store:
            progress_store[job_id].update(kwargs)


def _get_progress(job_id: str) -> Optional[dict]:
    with _progress_lock:
        return progress_store.get(job_id)


def cleanup_old_jobs():
    try:
        now = time.time()
        with _progress_lock:
            for jid in list(progress_store.keys()):
                entry = progress_store.get(jid)
                if entry and (now - entry.get('created_at', 0)) > MAX_JOB_AGE:
                    del progress_store[jid]
                    for d in [os.path.join(UPLOAD_FOLDER, jid), os.path.join(OUTPUT_FOLDER, jid)]:
                        shutil.rmtree(d, ignore_errors=True)
    except Exception as e:
        logger.warning("cleanup_old_jobs error: %s", e)
