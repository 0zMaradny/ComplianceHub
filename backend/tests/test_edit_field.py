"""Tests for POST /api/edit-field — direct field editing."""

import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.routes import progress_store

client = TestClient(app)

_JOB_COUNTER = 0


def _seed_job():
    """Seed an in-memory job with an Audit_Report that has a refinable field."""
    global _JOB_COUNTER
    _JOB_COUNTER += 1
    job_id = f'test-edit-{uuid.uuid4().hex[:8]}'
    progress_store[job_id] = {
        'status': 'done',
        'progress': 100,
        'current_doc': '',
        'doc_progress': {'Audit_Report': 'done'},
        'results': {
            'Audit_Report': {
                '_created_at': 1000000.0,
                '_data': {
                    'client_name': 'Acme Corp',
                    'scope': 'Original scope statement',
                    'findings_summary': 'Minor nonconformities found.',
                },
            },
        },
        '_ephemeral': True,
    }
    return job_id


class TestEditField:
    def test_edit_success(self):
        job_id = _seed_job()
        r = client.post('/api/edit-field', json={
            'job_id': job_id,
            'doc_type': 'Audit_Report',
            'field': 'scope',
            'value': 'Updated scope statement',
        })
        assert r.status_code == 200
        data = r.json()
        assert data['success'] is True
        assert data['field'] == 'scope'
        assert data['value'] == 'Updated scope statement'
        assert data['previous_value'] == 'Original scope statement'

        stored = progress_store[job_id]['results']['Audit_Report']['_data']['scope']
        assert stored == 'Updated scope statement'

    def test_edit_stores_version(self):
        job_id = _seed_job()
        r = client.post('/api/edit-field', json={
            'job_id': job_id,
            'doc_type': 'Audit_Report',
            'field': 'scope',
            'value': 'v2 scope',
        })
        assert r.status_code == 200
        versions = progress_store[job_id]['results']['Audit_Report']['_versions']['scope']
        assert len(versions) == 1
        assert versions[0]['value'] == 'v2 scope'
        assert versions[0]['instruction'] == 'manual edit'

    def test_missing_job_id(self):
        r = client.post('/api/edit-field', json={
            'job_id': '',
            'doc_type': 'Audit_Report',
            'field': 'scope',
            'value': 'x',
        })
        assert r.status_code == 400

    def test_job_not_found(self):
        r = client.post('/api/edit-field', json={
            'job_id': 'nonexistent-job',
            'doc_type': 'Audit_Report',
            'field': 'scope',
            'value': 'x',
        })
        assert r.status_code == 404

    def test_field_not_refinable(self):
        job_id = _seed_job()
        r = client.post('/api/edit-field', json={
            'job_id': job_id,
            'doc_type': 'Audit_Report',
            'field': 'client_name',
            'value': 'New name',
        })
        assert r.status_code == 400
        assert 'not editable' in r.json()['detail']

    def test_doc_type_not_found(self):
        job_id = _seed_job()
        r = client.post('/api/edit-field', json={
            'job_id': job_id,
            'doc_type': 'Nonexistent',
            'field': 'scope',
            'value': 'x',
        })
        assert r.status_code == 404

    def test_edit_appends_to_existing_versions(self):
        job_id = _seed_job()
        pi = progress_store[job_id]['results']['Audit_Report']
        pi['_versions'] = {'scope': [{'value': 'v1', 'instruction': 'original'}]}

        r = client.post('/api/edit-field', json={
            'job_id': job_id,
            'doc_type': 'Audit_Report',
            'field': 'scope',
            'value': 'v2',
        })
        assert r.status_code == 200
        versions = pi['_versions']['scope']
        assert len(versions) == 2
        assert versions[-1]['value'] == 'v2'