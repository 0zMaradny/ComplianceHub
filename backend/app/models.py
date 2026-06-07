"""Data models for the Audit Workflow Module.

Uses dataclasses for structure + JSON file storage for persistence.
No database dependency — all data stored in backend/data/ as JSON.
"""

import os
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)


# ── Audit Project ─────────────────────────────────────────────────────────

@dataclass
class AuditProject:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    client_key: str = ""
    title: str = ""
    standards: list = field(default_factory=list)
    status: str = "draft"  # draft → active → evidence_review → nc_review → closed
    lead_auditor: str = ""
    audit_team: list = field(default_factory=list)
    scope: str = ""
    audit_date: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    gates: dict = field(default_factory=lambda: {
        "G1_Scope": "pending",
        "G2_GapAnalysis": "pending",
        "G3_RiskRegister": "pending",
        "G4_Implementation": "pending",
        "G5_InternalAudit": "pending",
        "G6_Certification": "pending",
    })


@dataclass
class Evidence:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    clause: str = ""
    standard: str = ""
    file_name: str = ""
    file_path: str = ""
    uploaded_by: str = ""
    status: str = "pending"  # pending → reviewed → accepted → rejected
    reviewer_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Nonconformity:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    clause: str = ""
    severity: str = "Minor"  # Major | Minor
    description: str = ""
    evidence_ref: str = ""
    status: str = "open"  # open → containment → corrective → preventive → verified → closed
    root_cause: str = ""
    containment_action: str = ""
    corrective_action: str = ""
    preventive_action: str = ""
    effectiveness_verification: str = ""
    due_date: str = ""
    closed_date: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CAPA:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    project_id: str = ""
    nc_id: str = ""
    type: str = "corrective"  # corrective | preventive
    description: str = ""
    root_cause: str = ""
    action: str = ""
    owner: str = ""
    due_date: str = ""
    status: str = "open"  # open → in_progress → completed → verified
    verification_notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ── JSON Storage ──────────────────────────────────────────────────────────

def _storage_path(entity_type: str) -> str:
    return os.path.join(DATA_DIR, f'{entity_type}.json')


def _load_all(entity_type: str) -> list[dict]:
    path = _storage_path(entity_type)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return json.load(f)


def _save_all(entity_type: str, data: list[dict]):
    path = _storage_path(entity_type)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── CRUD: Audit Projects ──────────────────────────────────────────────────

def create_project(project: AuditProject) -> AuditProject:
    projects = _load_all('projects')
    projects.append(asdict(project))
    _save_all('projects', projects)
    return project


def get_project(project_id: str) -> Optional[AuditProject]:
    projects = _load_all('projects')
    for p in projects:
        if p['id'] == project_id:
            return AuditProject(**p)
    return None


def list_projects(client_key: str = None) -> list[AuditProject]:
    projects = _load_all('projects')
    if client_key:
        projects = [p for p in projects if p.get('client_key') == client_key]
    return [AuditProject(**p) for p in projects]


def update_project(project_id: str, **kwargs) -> Optional[AuditProject]:
    projects = _load_all('projects')
    for i, p in enumerate(projects):
        if p['id'] == project_id:
            p.update(kwargs)
            p['updated_at'] = datetime.now().isoformat()
            projects[i] = p
            _save_all('projects', projects)
            return AuditProject(**p)
    return None


def delete_project(project_id: str) -> bool:
    projects = _load_all('projects')
    original_len = len(projects)
    projects = [p for p in projects if p['id'] != project_id]
    if len(projects) < original_len:
        _save_all('projects', projects)
        return True
    return False


# ── CRUD: Evidence ────────────────────────────────────────────────────────

def create_evidence(evidence: Evidence) -> Evidence:
    items = _load_all('evidence')
    items.append(asdict(evidence))
    _save_all('evidence', items)
    return evidence


def list_evidence(project_id: str) -> list[Evidence]:
    items = _load_all('evidence')
    items = [e for e in items if e.get('project_id') == project_id]
    return [Evidence(**e) for e in items]


def update_evidence(evidence_id: str, **kwargs) -> Optional[Evidence]:
    items = _load_all('evidence')
    for i, e in enumerate(items):
        if e['id'] == evidence_id:
            e.update(kwargs)
            items[i] = e
            _save_all('evidence', items)
            return Evidence(**e)
    return None


# ── CRUD: Nonconformities ─────────────────────────────────────────────────

def create_nc(nc: Nonconformity) -> Nonconformity:
    items = _load_all('nonconformities')
    items.append(asdict(nc))
    _save_all('nonconformities', items)
    return nc


def list_ncs(project_id: str) -> list[Nonconformity]:
    items = _load_all('nonconformities')
    items = [n for n in items if n.get('project_id') == project_id]
    return [Nonconformity(**n) for n in items]


def update_nc(nc_id: str, **kwargs) -> Optional[Nonconformity]:
    items = _load_all('nonconformities')
    for i, n in enumerate(items):
        if n['id'] == nc_id:
            n.update(kwargs)
            items[i] = n
            _save_all('nonconformities', items)
            return Nonconformity(**n)
    return None


# ── CRUD: CAPA ────────────────────────────────────────────────────────────

def create_capa(capa: CAPA) -> CAPA:
    items = _load_all('capa')
    items.append(asdict(capa))
    _save_all('capa', items)
    return capa


def list_capa(project_id: str) -> list[CAPA]:
    items = _load_all('capa')
    items = [c for c in items if c.get('project_id') == project_id]
    return [CAPA(**c) for c in items]


def update_capa(capa_id: str, **kwargs) -> Optional[CAPA]:
    items = _load_all('capa')
    for i, c in enumerate(items):
        if c['id'] == capa_id:
            c.update(kwargs)
            items[i] = c
            _save_all('capa', items)
            return CAPA(**c)
    return None


# ── Project Statistics ────────────────────────────────────────────────────

def get_project_stats(project_id: str) -> dict:
    """Return summary statistics for a project."""
    evidence = list_evidence(project_id)
    ncs = list_ncs(project_id)
    capas = list_capa(project_id)

    return {
        "total_evidence": len(evidence),
        "evidence_accepted": len([e for e in evidence if e.status == "accepted"]),
        "evidence_pending": len([e for e in evidence if e.status == "pending"]),
        "total_ncs": len(ncs),
        "open_ncs": len([n for n in ncs if n.status not in ("closed", "verified")]),
        "major_ncs": len([n for n in ncs if n.severity == "Major"]),
        "minor_ncs": len([n for n in ncs if n.severity == "Minor"]),
        "total_capa": len(capas),
        "open_capa": len([c for c in capas if c.status not in ("completed", "verified")]),
    }
