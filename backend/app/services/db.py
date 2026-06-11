"""SQLite persistence layer for job storage.
Replaces the in-memory progress_store dict with a persistent database.
Thread-safe via SQLite's built-in locking. WAL mode for concurrent reads."""
import sqlite3
import os
import json
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'compliancehub.db')


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
    return conn


def init_db():
    conn = _get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'uploaded',
            progress INTEGER DEFAULT 0,
            current_doc TEXT,
            created_at REAL,
            results TEXT,
            doc_progress TEXT DEFAULT '{}',
            error TEXT,
            download_url TEXT,
            zip_name TEXT DEFAULT 'TUV_Audit_Package.zip',
            manday_info TEXT,
            standards TEXT DEFAULT '[]'
        )
    ''')
    try:
        conn.execute('ALTER TABLE jobs ADD COLUMN standards TEXT DEFAULT \'[]\'')
    except Exception:
        logger.warning('ALTER TABLE jobs.standards skipped (column already exists or DB error)')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS compliance_assessments (
            standard_key TEXT PRIMARY KEY,
            assessments TEXT NOT NULL,
            updated_at REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_compliance_assessment(standard_key: str, assessments: dict):
    conn = _get_conn()
    conn.execute(
        'INSERT OR REPLACE INTO compliance_assessments (standard_key, assessments, updated_at) VALUES (?, ?, ?)',
        (standard_key, json.dumps(assessments), __import__('time').time()),
    )
    conn.commit()
    conn.close()


def load_compliance_assessment(standard_key: str) -> dict | None:
    conn = _get_conn()
    row = conn.execute(
        'SELECT assessments FROM compliance_assessments WHERE standard_key=?', (standard_key,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    try:
        return json.loads(row['assessments'])
    except (json.JSONDecodeError, TypeError):
        return None


def set_job(job_id, **kwargs):
    kwargs['job_id'] = job_id
    fields = ', '.join(kwargs.keys())
    placeholders = ', '.join('?' * len(kwargs))
    conn = _get_conn()
    conn.execute(
        f'INSERT OR REPLACE INTO jobs ({fields}) VALUES ({placeholders})',
        list(kwargs.values()),
    )
    conn.commit()
    conn.close()


def update_job(job_id, **kwargs):
    if not kwargs:
        return
    sets = []
    values = []
    for k, v in kwargs.items():
        sets.append(f'{k}=?')
        values.append(v)
    values.append(job_id)
    conn = _get_conn()
    conn.execute(f'UPDATE jobs SET {", ".join(sets)} WHERE job_id=?', values)
    conn.commit()
    conn.close()


def get_job(job_id):
    conn = _get_conn()
    row = conn.execute('SELECT * FROM jobs WHERE job_id=?', (job_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    d = dict(row)
    for field in ('results', 'doc_progress', 'manday_info'):
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


def delete_job(job_id):
    conn = _get_conn()
    conn.execute('DELETE FROM jobs WHERE job_id=?', (job_id,))
    conn.commit()
    conn.close()


def cleanup_old_jobs(max_age=3600):
    import time
    now = time.time()
    conn = _get_conn()
    rows = conn.execute(
        'SELECT job_id FROM jobs WHERE ? - created_at > ?',
        (now, max_age),
    ).fetchall()
    conn.execute('DELETE FROM jobs WHERE ? - created_at > ?', (now, max_age))
    conn.commit()
    conn.close()
    return [r['job_id'] for r in rows if r]


def list_jobs(limit=20, offset=0, search=""):
    conn = _get_conn()
    if search:
        rows = conn.execute(
            'SELECT job_id, status, progress, created_at, results, download_url, error, standards, zip_name '
            'FROM jobs WHERE job_id LIKE ? OR status LIKE ? OR standards LIKE ? '
            'ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (f'%{search}%', f'%{search}%', f'%{search}%', limit, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT job_id, status, progress, created_at, results, download_url, error, standards, zip_name '
            'FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset,)
        ).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        for f in ('results', 'standards'):
            if d.get(f) and isinstance(d[f], str):
                try:
                    d[f] = json.loads(d[f])
                except (json.JSONDecodeError, TypeError):
                    pass
        out.append(d)
    return out


def get_stats():
    """Return aggregated analytics from the jobs table."""
    import time, json
    now = time.time()
    conn = _get_conn()
    total = conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0]
    done = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='done'").fetchone()[0]
    failed = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='error'").fetchone()[0]
    generating = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='generating'").fetchone()[0]
    last_24h = conn.execute(
        'SELECT COUNT(*) FROM jobs WHERE ? - created_at < 86400', (now,)
    ).fetchone()[0]

    # Count unique standards used
    std_rows = conn.execute('SELECT standards FROM jobs WHERE standards IS NOT NULL').fetchall()
    standards_count = {}
    for r in std_rows:
        raw = r['standards']
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
        if isinstance(raw, (list, tuple)):
            for s in raw:
                key = s.replace('iso_', 'ISO ').replace('_', ':')
                standards_count[key] = standards_count.get(key, 0) + 1

    # Count certification outcomes from results JSON
    cert_count = {'Certified': 0, 'Conditional': 0, 'Non-Certified': 0, 'Other': 0}
    res_rows = conn.execute('SELECT results FROM jobs WHERE results IS NOT NULL').fetchall()
    for r in res_rows:
        raw = r['results']
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
        if isinstance(raw, dict):
            decisions = [
                v.get('certification_decision') for v in raw.values()
                if isinstance(v, dict) and v.get('certification_decision')
            ]
            for d in decisions:
                if d in cert_count:
                    cert_count[d] += 1
                else:
                    cert_count['Other'] += 1

    conn.close()
    return {
        'total_jobs': total,
        'jobs_completed': done,
        'jobs_failed': failed,
        'jobs_in_progress': generating,
        'jobs_last_24h': last_24h,
        'standards_used': standards_count,
        'certification_outcomes': cert_count,
        'success_rate': round(done / total * 100, 1) if total > 0 else 0,
    }


init_db()
