"""Audit Workflow Module — project lifecycle management.

Manages audit projects from creation through evidence collection,
NC tracking, CAPA, and closure. Implements the 6-gate delivery pipeline.
"""

import os
import json
import uuid
import threading
from datetime import datetime
from dataclasses import dataclass, field, asdict
from app.services.client_config import get_client


@dataclass
class AuditProject:
    id: str
    client_key: str
    title: str
    standards: list
    status: str = "active"
    current_gate: int = 1
    created_at: str = ""
    updated_at: str = ""
    target_date: str = ""
    lead_auditor: str = ""
    notes: str = ""
    gate_deliverables: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    nonconformities: list = field(default_factory=list)
    capa_items: list = field(default_factory=list)
    generated_docs: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Nonconformity:
    id: str
    project_id: str
    clause: str
    severity: str
    description: str
    evidence: str
    status: str = "open"
    auditee: str = ""
    due_date: str = ""
    created_at: str = ""
    closed_at: str = ""
    capa_id: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)


@dataclass
class CAPAItem:
    id: str
    project_id: str
    nc_id: str = ""
    root_cause: str = ""
    containment: str = ""
    corrective_action: str = ""
    preventive_action: str = ""
    effectiveness_verification: str = ""
    status: str = "draft"
    owner: str = ""
    due_date: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at

    def to_dict(self):
        return asdict(self)


@dataclass
class Evidence:
    id: str = ""
    project_id: str = ""
    clause: str = ""
    standard: str = ""
    file_name: str = ""
    file_path: str = ""
    uploaded_by: str = ""
    status: str = "pending"
    reviewer_notes: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:12]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)


GATES = [
    {"gate": 1, "name": "Scope & Context",
     "description": "Define audit scope, context, and stakeholder map",
     "deliverables": ["scope_statement", "context_doc", "stakeholder_map"]},
    {"gate": 2, "name": "Gap Analysis",
     "description": "Clause-by-clause gap assessment against standard requirements",
     "deliverables": ["gap_report", "nc_log", "ofi_log"]},
    {"gate": 3, "name": "Risk Register",
     "description": "Complete risk register with client-specific formulas",
     "deliverables": ["risk_register", "risk_treatment_plan"]},
    {"gate": 4, "name": "Implementation Docs",
     "description": "Policies, procedures, CAPA log, Arabic docs",
     "deliverables": ["policies", "procedures", "capa_log", "arabic_docs"]},
    {"gate": 5, "name": "Internal Audit",
     "description": "Pre-certification IMS audit report",
     "deliverables": ["internal_audit_report", "nc_summary", "readiness_score"]},
    {"gate": 6, "name": "Certification Package",
     "description": "8-document audit package via Platform",
     "deliverables": ["audit_plan_s1", "audit_plan_s2", "participation_list",
                      "audit_report", "iso_checklist", "certificate_text", "tnl", "certificate"]},
]

_PROJECTS: dict = {}
_NCS: dict = {}
_CAPAS: dict = {}
_EVIDENCE: dict = {}
_STORE_LOCK = threading.Lock()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
PROJECTS_FILE = os.path.join(DATA_DIR, 'projects.json')
NCS_FILE = os.path.join(DATA_DIR, 'ncs.json')
CAPAS_FILE = os.path.join(DATA_DIR, 'capas.json')
EVIDENCE_FILE = os.path.join(DATA_DIR, 'evidence.json')


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _save_projects():
    _ensure_data_dir()
    with _STORE_LOCK:
        data = {k: v.to_dict() for k, v in _PROJECTS.items()}
        with open(PROJECTS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _save_ncs():
    _ensure_data_dir()
    with _STORE_LOCK:
        data = {k: v.to_dict() for k, v in _NCS.items()}
        with open(NCS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _save_capas():
    _ensure_data_dir()
    with _STORE_LOCK:
        data = {k: v.to_dict() for k, v in _CAPAS.items()}
        with open(CAPAS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _save_evidence():
    _ensure_data_dir()
    with _STORE_LOCK:
        data = {k: v.to_dict() for k, v in _EVIDENCE.items()}
        with open(EVIDENCE_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _load_all():
    _ensure_data_dir()
    global _PROJECTS, _NCS, _CAPAS, _EVIDENCE
    with _STORE_LOCK:
        if os.path.exists(PROJECTS_FILE):
            with open(PROJECTS_FILE) as f:
                _PROJECTS = {k: AuditProject.from_dict(v) for k, v in json.load(f).items()}
        if os.path.exists(NCS_FILE):
            with open(NCS_FILE) as f:
                _NCS = {k: Nonconformity(**v) for k, v in json.load(f).items()}
        if os.path.exists(CAPAS_FILE):
            with open(CAPAS_FILE) as f:
                _CAPAS = {k: CAPAItem(**v) for k, v in json.load(f).items()}
        if os.path.exists(EVIDENCE_FILE):
            with open(EVIDENCE_FILE) as f:
                _EVIDENCE = {k: Evidence(**v) for k, v in json.load(f).items()}


_load_all()


def create_project(client_key, title, standards, target_date="", lead_auditor="", notes=""):
    project_id = uuid.uuid4().hex[:12]
    project = AuditProject(
        id=project_id, client_key=client_key, title=title,
        standards=standards, target_date=target_date,
        lead_auditor=lead_auditor, notes=notes,
    )
    with _STORE_LOCK:
        _PROJECTS[project_id] = project
    _save_projects()
    return project


def get_project(project_id):
    return _PROJECTS.get(project_id)


def list_projects(client_key=None, status=None):
    projects = list(_PROJECTS.values())
    if client_key:
        projects = [p for p in projects if p.client_key == client_key]
    if status:
        projects = [p for p in projects if p.status == status]
    return sorted(projects, key=lambda p: p.created_at, reverse=True)


def update_project(project_id, **kwargs):
    project = _PROJECTS.get(project_id)
    if not project:
        return None
    for key, value in kwargs.items():
        if hasattr(project, key):
            setattr(project, key, value)
    project.updated_at = datetime.now().isoformat()
    _save_projects()
    return project


def delete_project(project_id):
    if project_id not in _PROJECTS:
        return False
    with _STORE_LOCK:
        del _PROJECTS[project_id]
        for nc_id in [k for k, v in _NCS.items() if v.project_id == project_id]:
            del _NCS[nc_id]
        for capa_id in [k for k, v in _CAPAS.items() if v.project_id == project_id]:
            del _CAPAS[capa_id]
    _save_projects()
    _save_ncs()
    _save_capas()
    return True


def advance_gate(project_id):
    project = _PROJECTS.get(project_id)
    if not project or project.current_gate >= 6:
        return None
    project.current_gate += 1
    project.updated_at = datetime.now().isoformat()
    _save_projects()
    return project


def set_gate(project_id, gate):
    if gate < 1 or gate > 6:
        return None
    project = _PROJECTS.get(project_id)
    if not project:
        return None
    project.current_gate = gate
    project.updated_at = datetime.now().isoformat()
    _save_projects()
    return project


def get_gate_info(gate_num):
    for g in GATES:
        if g["gate"] == gate_num:
            return g
    return {}


def get_project_progress(project_id):
    project = _PROJECTS.get(project_id)
    if not project:
        return {}
    client = get_client(project.client_key)
    ncs = [nc for nc in _NCS.values() if nc.project_id == project_id]
    capas = [c for c in _CAPAS.values() if c.project_id == project_id]
    return {
        "project": project.to_dict(),
        "client_name": client.name if client else "Unknown",
        "current_gate_info": get_gate_info(project.current_gate),
        "all_gates": GATES,
        "nc_summary": {
            "total": len(ncs),
            "open": len([n for n in ncs if n.status == "open"]),
            "major": len([n for n in ncs if n.severity == "Major"]),
            "minor": len([n for n in ncs if n.severity == "Minor"]),
            "closed": len([n for n in ncs if n.status == "closed"]),
        },
        "capa_summary": {
            "total": len(capas),
            "draft": len([c for c in capas if c.status == "draft"]),
            "in_progress": len([c for c in capas if c.status == "in_progress"]),
            "verified": len([c for c in capas if c.status == "verified"]),
        },
        "generated_docs": project.generated_docs,
    }


def create_nc(project_id, clause, severity, description, evidence="", auditee="", due_date=""):
    if project_id not in _PROJECTS:
        return None
    nc_id = f"NC-{uuid.uuid4().hex[:8].upper()}"
    nc = Nonconformity(
        id=nc_id, project_id=project_id, clause=clause,
        severity=severity, description=description,
        evidence=evidence, auditee=auditee, due_date=due_date,
    )
    with _STORE_LOCK:
        _NCS[nc_id] = nc
    _save_ncs()
    return nc


def get_nc(nc_id):
    return _NCS.get(nc_id)


def list_ncs(project_id=None, status=None):
    ncs = list(_NCS.values())
    if project_id:
        ncs = [n for n in ncs if n.project_id == project_id]
    if status:
        ncs = [n for n in ncs if n.status == status]
    return ncs


def update_nc(nc_id, **kwargs):
    nc = _NCS.get(nc_id)
    if not nc:
        return None
    for key, value in kwargs.items():
        if hasattr(nc, key):
            setattr(nc, key, value)
    if kwargs.get("status") == "closed" and not nc.closed_at:
        nc.closed_at = datetime.now().isoformat()
    _save_ncs()
    return nc


def create_capa(project_id, nc_id="", root_cause="", containment="",
                corrective_action="", preventive_action="", owner="", due_date=""):
    if project_id not in _PROJECTS:
        return None
    capa_id = f"CAPA-{uuid.uuid4().hex[:8].upper()}"
    capa = CAPAItem(
        id=capa_id, project_id=project_id, nc_id=nc_id,
        root_cause=root_cause, containment=containment,
        corrective_action=corrective_action, preventive_action=preventive_action,
        owner=owner, due_date=due_date,
    )
    with _STORE_LOCK:
        _CAPAS[capa_id] = capa
    _save_capas()
    return capa


def get_capa(capa_id):
    return _CAPAS.get(capa_id)


def list_capas(project_id=None, status=None):
    capas = list(_CAPAS.values())
    if project_id:
        capas = [c for c in capas if c.project_id == project_id]
    if status:
        capas = [c for c in capas if c.status == status]
    return capas


def update_capa(capa_id, **kwargs):
    capa = _CAPAS.get(capa_id)
    if not capa:
        return None
    for key, value in kwargs.items():
        if hasattr(capa, key):
            setattr(capa, key, value)
    capa.updated_at = datetime.now().isoformat()
    _save_capas()
    return capa


def add_evidence(project_id, gate, filename, description="", uploaded_by=""):
    project = _PROJECTS.get(project_id)
    if not project:
        return {}
    item = {
        "id": uuid.uuid4().hex[:8], "gate": gate, "filename": filename,
        "description": description, "uploaded_by": uploaded_by,
        "uploaded_at": datetime.now().isoformat(),
    }
    project.evidence.append(item)
    project.updated_at = datetime.now().isoformat()
    _save_projects()
    return item


def get_dashboard_stats(client_key=None):
    projects = list(_PROJECTS.values())
    if client_key:
        projects = [p for p in projects if p.client_key == client_key]
    ncs = list(_NCS.values())
    capas = list(_CAPAS.values())
    if client_key:
        pids = {p.id for p in projects}
        ncs = [n for n in ncs if n.project_id in pids]
        capas = [c for c in capas if c.project_id in pids]
    gate_dist = {i: 0 for i in range(1, 7)}
    for p in projects:
        gate_dist[p.current_gate] = gate_dist.get(p.current_gate, 0) + 1
    return {
        "total_projects": len(projects),
        "active_projects": len([p for p in projects if p.status == "active"]),
        "completed_projects": len([p for p in projects if p.status == "completed"]),
        "gate_distribution": gate_dist,
        "total_ncs": len(ncs),
        "open_ncs": len([n for n in ncs if n.status == "open"]),
        "major_ncs": len([n for n in ncs if n.severity == "Major"]),
        "total_capas": len(capas),
        "pending_capas": len([c for c in capas if c.status in ("draft", "in_progress")]),
        "recent_projects": [p.to_dict() for p in sorted(projects, key=lambda x: x.updated_at, reverse=True)[:5]],
    }


def create_evidence(project_id, clause, standard, file_name, file_path, uploaded_by=""):
    if project_id not in _PROJECTS:
        return None
    ev = Evidence(
        project_id=project_id, clause=clause, standard=standard,
        file_name=file_name, file_path=file_path, uploaded_by=uploaded_by,
    )
    with _STORE_LOCK:
        _EVIDENCE[ev.id] = ev
    _save_evidence()
    return ev


def list_evidence(project_id=None):
    items = list(_EVIDENCE.values())
    if project_id:
        items = [e for e in items if e.project_id == project_id]
    return sorted(items, key=lambda e: e.created_at, reverse=True)


def update_evidence(evidence_id, **kwargs):
    ev = _EVIDENCE.get(evidence_id)
    if not ev:
        return None
    for key, value in kwargs.items():
        if hasattr(ev, key):
            setattr(ev, key, value)
    _save_evidence()
    return ev


def get_gate_deliverable_status(project):
    return project.gate_deliverables if project else {}


def set_gate_deliverable(project_id, deliverable, status="complete"):
    project = _PROJECTS.get(project_id)
    if not project:
        return None
    project.gate_deliverables[deliverable] = status
    project.updated_at = datetime.now().isoformat()
    _save_projects()
    return project
