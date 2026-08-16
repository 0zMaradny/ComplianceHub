"""RAG retriever — offline semantic-ish retrieval over historical audit packages.

Lighter than OpenSearch: uses SQLite FTS5 keyword ranking over stored job
results. Enriched context is injected into AI prompts to improve consistency
with past NCs / findings / terminology.

Embeddings via sqlite-vec are optional; FTS5 works with zero extra deps.
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAG_DB = DATA_DIR / "rag_index.db"


def _connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(RAG_DB))
    conn.row_factory = sqlite3.Row
    return conn


def init_rag():
    """Create FTS5 table if missing. Safe to call at app startup."""
    try:
        conn = _connect()
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS audit_packages_fts USING fts5(
                job_id, client_name, standard, doc_type, content,
                content=''
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("RAG init failed (FTS5 unavailable?): %s", e)


def index_job(job_id: str, results: dict):
    """Index a completed job's documents into the FTS store."""
    try:
        conn = _connect()
        for doc_type, result in results.items():
            doc_data = result.get('_data', {}) if isinstance(result, dict) else {}
            chunks = [
                str(doc_data.get(k, '')) for k in
                ('client_name', 'standard', 'findings_summary', 'conclusion',
                 'scope', 'positive_findings', 'opportunities_for_improvement',
                 'nonconformities', 'overall_assessment', 'sections', 'summary')
            ]
            text = ' '.join(c for c in chunks if c)
            conn.execute(
                "INSERT INTO audit_packages_fts (job_id, client_name, standard, doc_type, content) VALUES (?,?,?,?,?)",
                (job_id, str(doc_data.get('client_name', '')), str(doc_data.get('standard', '')),
                 doc_type, text),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("RAG index_job failed: %s", e)


def retrieve(query: str, top_k: int = 3) -> str:
    """Return top-k matching historical content snippets for prompt augmentation."""
    if not query.strip():
        return ""
    try:
        conn = _connect()
        rows = conn.execute(
            "SELECT client_name, standard, doc_type, snippet(audit_packages_fts, 4, '[', ']', '…', 12) AS snip "
            "FROM audit_packages_fts WHERE content MATCH ? ORDER BY rank LIMIT ?",
            (query.replace('"', ' ').strip(), top_k),
        ).fetchall()
        conn.close()
        if not rows:
            return ""
        parts = []
        for r in rows:
            parts.append(f"- [{r['standard']} / {r['doc_type']}] {r['client_name']}: {r['snip']}")
        return "\n== Historical Context (RAG) ==\n" + "\n".join(parts) + "\n"
    except Exception as e:
        logger.warning("RAG retrieve failed: %s", e)
        return ""