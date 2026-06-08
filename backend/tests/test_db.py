"""Unit tests for the SQLite persistence layer."""
import time
from app.services import db


class TestDB:
    def setup_method(self):
        self.jid = 'test_job_001'

    def teardown_method(self):
        try:
            db.delete_job(self.jid)
        except Exception:
            pass

    def test_set_and_get_job(self):
        db.set_job(job_id=self.jid, status='uploaded', progress=5)
        j = db.get_job(self.jid)
        assert j is not None
        assert j['status'] == 'uploaded'
        assert j['progress'] == 5

    def test_update_job(self):
        db.set_job(job_id=self.jid, status='uploaded', progress=5)
        db.update_job(self.jid, status='generating', progress=50)
        j = db.get_job(self.jid)
        assert j['status'] == 'generating'
        assert j['progress'] == 50

    def test_get_nonexistent(self):
        j = db.get_job('nonexistent_job_id')
        assert j is None

    def test_delete_job(self):
        db.set_job(job_id=self.jid, status='testing')
        db.delete_job(self.jid)
        j = db.get_job(self.jid)
        assert j is None

    def test_job_with_json_fields(self):
        db.set_job(job_id=self.jid, status='done', results='{"key": "value"}', doc_progress='{"doc1": "done"}')
        j = db.get_job(self.jid)
        assert j['results'] == {'key': 'value'}
        assert j['doc_progress'] == {'doc1': 'done'}

    def test_job_with_null_fields(self):
        db.set_job(job_id=self.jid, status='uploaded', results=None, error=None)
        j = db.get_job(self.jid)
        assert j['results'] is None
        assert j['error'] is None

    def test_cleanup_old_jobs(self):
        db.set_job(job_id=self.jid, status='old', created_at=time.time() - 10000)
        old = db.cleanup_old_jobs(max_age=3600)
        assert self.jid in old
        j = db.get_job(self.jid)
        assert j is None

    def test_cleanup_does_not_remove_recent(self):
        db.set_job(job_id=self.jid, status='recent', created_at=time.time())
        old = db.cleanup_old_jobs(max_age=3600)
        assert self.jid not in old
        j = db.get_job(self.jid)
        assert j is not None
        db.delete_job(self.jid)

    def test_set_job_with_partial_fields(self):
        db.set_job(job_id=self.jid, status='running', progress=42)
        j = db.get_job(self.jid)
        assert j['status'] == 'running'
        assert j['progress'] == 42
        assert j['zip_name'] == 'TUV_Audit_Package.zip'  # default

    def test_update_nonexistent_job(self):
        db.update_job('nonexistent', status='lost')
        # should not raise
        assert True
