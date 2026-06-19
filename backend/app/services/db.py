"""Persistence layer — SQLite (local) or PostgreSQL (Railway) via auto-detect.
Thread-safe. If DATABASE_URL env var is set, uses PostgreSQL; else SQLite."""

import os
import json
import time
import logging
from typing import Any

from app.settings import DATABASE_URL as _RAW_DATABASE_URL

logger = logging.getLogger(__name__)

_DATABASE_URL = _RAW_DATABASE_URL.strip()
_IS_POSTGRES = _DATABASE_URL.startswith('postgresql://') or _DATABASE_URL.startswith('postgres://')
_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'compliancehub.db')


def _fix_sql(sql: str) -> str:
    return sql.replace('?', '%s') if _IS_POSTGRES else sql


def _get_conn():
    if _IS_POSTGRES:
        import psycopg2
        conn = psycopg2.connect(_DATABASE_URL)
        conn.autocommit = True
        return conn
    import sqlite3
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
    return conn


def _exec(sql: str, params: list | tuple = None):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(_fix_sql(sql), params or [])
        if not _IS_POSTGRES:
            conn.commit()
        return cur
    finally:
        if not _IS_POSTGRES:
            conn.close()


def _fetchone(sql: str, params: list | tuple = None) -> dict | None:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(_fix_sql(sql), params or [])
        row = cur.fetchone()
        if row is None:
            return None
        if _IS_POSTGRES:
            return dict(row)
        return dict(row)
    finally:
        conn.close()


def _fetchall(sql: str, params: list | tuple = None) -> list[dict]:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(_fix_sql(sql), params or [])
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def _commit(cur=None):
    if not _IS_POSTGRES and cur is not None:
        try:
            cur.connection.commit()
        except Exception as e:
            logger.warning("Commit failed: %s", e)


def init_db():
    if _IS_POSTGRES:
        _exec('''
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
            _exec("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS standards TEXT DEFAULT '[]'")
        except Exception:
            logger.warning('ALTER TABLE jobs.standards skipped')
        _exec('''
            CREATE TABLE IF NOT EXISTS compliance_assessments (
                standard_key TEXT PRIMARY KEY,
                assessments TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
    else:
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
            conn.execute("ALTER TABLE jobs ADD COLUMN standards TEXT DEFAULT '[]'")
        except Exception:
            logger.warning('ALTER TABLE jobs.standards skipped (already exists)')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS compliance_assessments (
                standard_key TEXT PRIMARY KEY,
                assessments TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()


def _parse_json(val: Any) -> Any:
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return val
    return val


def save_compliance_assessment(standard_key: str, assessments: dict):
    if _IS_POSTGRES:
        _exec(
            'INSERT INTO compliance_assessments (standard_key, assessments, updated_at) '
            'VALUES (%s, %s, %s) '
            'ON CONFLICT (standard_key) DO UPDATE SET assessments=%s, updated_at=%s',
            (standard_key, json.dumps(assessments), time.time(), json.dumps(assessments), time.time()),
        )
    else:
        conn = _get_conn()
        conn.execute(
            'INSERT OR REPLACE INTO compliance_assessments (standard_key, assessments, updated_at) VALUES (?, ?, ?)',
            (standard_key, json.dumps(assessments), time.time()),
        )
        conn.commit()
        conn.close()


def load_compliance_assessment(standard_key: str) -> dict | None:
    row = _fetchone(
        'SELECT assessments FROM compliance_assessments WHERE standard_key=?', (standard_key,)
    )
    if row is None:
        return None
    val = row['assessments']
    if isinstance(val, str):
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            return None
    return val


def set_job(job_id, **kwargs):
    kwargs['job_id'] = job_id
    fields = ', '.join(kwargs.keys())
    placeholders = ', '.join(['%s'] * len(kwargs)) if _IS_POSTGRES else ', '.join(['?'] * len(kwargs))
    if _IS_POSTGRES:
        cols = ', '.join(kwargs.keys())
        vals = ', '.join(['%s'] * len(kwargs))
        updates = ', '.join([f'{k}=EXCLUDED.{k}' for k in kwargs.keys() if k != 'job_id'])
        sql = f'INSERT INTO jobs ({cols}) VALUES ({vals}) ON CONFLICT (job_id) DO UPDATE SET {updates}'
        _exec(sql, list(kwargs.values()))
    else:
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
    sets = ', '.join([f'{k}=%s' if _IS_POSTGRES else f'{k}=?' for k in kwargs.keys()])
    values = list(kwargs.values()) + [job_id]
    _exec(f'UPDATE jobs SET {sets} WHERE job_id=?', values)


def get_job(job_id):
    row = _fetchone('SELECT * FROM jobs WHERE job_id=?', (job_id,))
    if row is None:
        return None
    for field in ('results', 'doc_progress', 'manday_info', 'standards'):
        if row.get(field):
            row[field] = _parse_json(row[field])
    return row


def delete_job(job_id):
    _exec('DELETE FROM jobs WHERE job_id=?', (job_id,))


def cleanup_old_jobs(max_age=3600):
    now = time.time()
    rows = _fetchall('SELECT job_id FROM jobs WHERE ? - created_at > ?', (now, max_age))
    _exec('DELETE FROM jobs WHERE ? - created_at > ?', (now, max_age))
    return [r['job_id'] for r in rows if r]


def list_jobs(limit=20, offset=0, search=""):
    if search:
        rows = _fetchall(
            'SELECT job_id, status, progress, created_at, results, download_url, error, standards, zip_name '
            'FROM jobs WHERE job_id LIKE ? OR status LIKE ? OR standards LIKE ? '
            'ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (f'%{search}%', f'%{search}%', f'%{search}%', limit, offset),
        )
    else:
        rows = _fetchall(
            'SELECT job_id, status, progress, created_at, results, download_url, error, standards, zip_name '
            'FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (limit, offset,),
        )
    for d in rows:
        for f in ('results', 'standards'):
            if d.get(f):
                d[f] = _parse_json(d[f])
    return rows


def get_stats():
    now = time.time()
    total = _fetchone('SELECT COUNT(*) AS cnt FROM jobs')['cnt']
    done = _fetchone("SELECT COUNT(*) AS cnt FROM jobs WHERE status='done'")['cnt']
    failed = _fetchone("SELECT COUNT(*) AS cnt FROM jobs WHERE status='error'")['cnt']
    generating = _fetchone("SELECT COUNT(*) AS cnt FROM jobs WHERE status='generating'")['cnt']
    last_24h = _fetchone(
        'SELECT COUNT(*) AS cnt FROM jobs WHERE ? - created_at < 86400', (now,)
    )['cnt']

    std_rows = _fetchall('SELECT standards FROM jobs WHERE standards IS NOT NULL')
    standards_count = {}
    for r in std_rows:
        raw = _parse_json(r['standards'])
        if isinstance(raw, (list, tuple)):
            for s in raw:
                key = s.replace('iso_', 'ISO ').replace('_', ':')
                standards_count[key] = standards_count.get(key, 0) + 1

    cert_count = {'Certified': 0, 'Conditional': 0, 'Non-Certified': 0, 'Other': 0}
    res_rows = _fetchall('SELECT results FROM jobs WHERE results IS NOT NULL')
    for r in res_rows:
        raw = _parse_json(r['results'])
        if isinstance(raw, dict):
            for v in raw.values():
                if isinstance(v, dict) and v.get('certification_decision'):
                    d = v['certification_decision']
                    if d in cert_count:
                        cert_count[d] += 1
                    else:
                        cert_count['Other'] += 1

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
