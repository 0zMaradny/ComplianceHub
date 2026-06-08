"""Audit Program & Live Audit Execution Module.

Provides day-by-day audit program building, clause-level checklist tracking,
evidence capture, findings registration, and daily summary generation.
"""

import os
import json
import uuid
import threading
from datetime import datetime
from dataclasses import dataclass, field, asdict

from app.services.clause_data import get_all_clause_items


# ── Data Classes ──────────────────────────────────────────────────────────

@dataclass
class AuditProgramEntry:
    id: str
    program_id: str
    day: int = 1
    date: str = ""
    start_time: str = ""
    end_time: str = ""
    department: str = ""
    auditor: str = ""
    clause_refs: list = field(default_factory=list)
    standard: str = ""
    description: str = ""
    room: str = ""
    status: str = "planned"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)


@dataclass
class ClauseChecklistItem:
    id: str
    program_id: str
    standard: str = ""
    clause_ref: str = ""
    clause_title: str = ""
    status: str = "pending"
    evidence_required: str = ""
    evidence_suggestions: list = field(default_factory=list)  # Pre-filled evidence suggestions from standard
    evidence_found: str = ""
    auditor_notes: str = ""
    auditee: str = ""
    severity: str = ""
    nc_description: str = ""
    ofi_description: str = ""
    reviewed: bool = False
    reviewed_at: str = ""
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
class EvidenceRegisterEntry:
    id: str
    program_id: str
    clause_ref: str = ""
    standard: str = ""
    evidence_type: str = "document"
    description: str = ""
    collected_by: str = ""
    status: str = "collected"
    file_path: str = ""
    reviewer_notes: str = ""
    collected_at: str = ""
    reviewed_at: str = ""

    def __post_init__(self):
        if not self.collected_at:
            self.collected_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)


@dataclass
class AuditDailySummary:
    id: str
    program_id: str
    day: int = 1
    date: str = ""
    clauses_covered: list = field(default_factory=list)
    nc_major: list = field(default_factory=list)
    nc_minor: list = field(default_factory=list)
    ofi_items: list = field(default_factory=list)
    evidence_collected: list = field(default_factory=list)
    completion_pct: float = 0.0
    summary_notes: str = ""
    auditor_signoff: str = ""
    auditee_signoff: str = ""
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
class AuditProgram:
    id: str
    title: str = ""
    client_name: str = ""
    client_key: str = ""
    standards: list = field(default_factory=list)
    audit_type: str = "stage2"
    lead_auditor: str = ""
    audit_team: list = field(default_factory=list)
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    status: str = "draft"
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if isinstance(self.audit_team, str):
            self.audit_team = [t.strip() for t in self.audit_team.split(",") if t.strip()]

    def to_dict(self):
        return asdict(self)


# ── Persistence ───────────────────────────────────────────────────────────

_PROGRAMS: dict = {}
_ENTRIES: dict = {}
_CHECKLISTS: dict = {}
_EVIDENCE_REG: dict = {}
_DAILY_SUMMARIES: dict = {}
_STORE_LOCK = threading.Lock()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
AP_DIR = os.path.join(DATA_DIR, 'audit_programs')
PROGRAMS_FILE = os.path.join(AP_DIR, 'programs.json')
ENTRIES_FILE = os.path.join(AP_DIR, 'entries.json')
CHECKLISTS_FILE = os.path.join(AP_DIR, 'checklists.json')
EVIDENCE_FILE = os.path.join(AP_DIR, 'evidence_reg.json')
SUMMARIES_FILE = os.path.join(AP_DIR, 'daily_summaries.json')


def _ensure_dir():
    os.makedirs(AP_DIR, exist_ok=True)


def _save_programs():
    _ensure_dir()
    with _STORE_LOCK:
        with open(PROGRAMS_FILE, 'w') as f:
            json.dump({k: v.to_dict() for k, v in _PROGRAMS.items()}, f, indent=2, ensure_ascii=False)


def _save_entries():
    _ensure_dir()
    with _STORE_LOCK:
        with open(ENTRIES_FILE, 'w') as f:
            json.dump({k: v.to_dict() for k, v in _ENTRIES.items()}, f, indent=2, ensure_ascii=False)


def _save_checklists():
    _ensure_dir()
    with _STORE_LOCK:
        with open(CHECKLISTS_FILE, 'w') as f:
            json.dump({k: v.to_dict() for k, v in _CHECKLISTS.items()}, f, indent=2, ensure_ascii=False)


def _save_evidence():
    _ensure_dir()
    with _STORE_LOCK:
        with open(EVIDENCE_FILE, 'w') as f:
            json.dump({k: v.to_dict() for k, v in _EVIDENCE_REG.items()}, f, indent=2, ensure_ascii=False)


def _save_summaries():
    _ensure_dir()
    with _STORE_LOCK:
        with open(SUMMARIES_FILE, 'w') as f:
            json.dump({k: v.to_dict() for k, v in _DAILY_SUMMARIES.items()}, f, indent=2, ensure_ascii=False)


def _load_all():
    _ensure_dir()
    with _STORE_LOCK:
        for filepath, target, cls in [
            (PROGRAMS_FILE, '_PROGRAMS', AuditProgram),
            (ENTRIES_FILE, '_ENTRIES', AuditProgramEntry),
            (CHECKLISTS_FILE, '_CHECKLISTS', ClauseChecklistItem),
            (EVIDENCE_FILE, '_EVIDENCE_REG', EvidenceRegisterEntry),
            (SUMMARIES_FILE, '_DAILY_SUMMARIES', AuditDailySummary),
        ]:
            if os.path.exists(filepath):
                with open(filepath) as f:
                    data = json.load(f)
                    loaded = {k: cls(**v) for k, v in data.items()}
                    globals()[target].update(loaded)


_load_all()


# ── Program CRUD ──────────────────────────────────────────────────────────

def create_program(title, client_name, client_key, standards, audit_type,
                   lead_auditor, audit_team, start_date, end_date,
                   location="", notes=""):
    pid = uuid.uuid4().hex[:12]
    program = AuditProgram(
        id=pid, title=title, client_name=client_name,
        client_key=client_key, standards=standards,
        audit_type=audit_type, lead_auditor=lead_auditor,
        audit_team=audit_team, start_date=start_date,
        end_date=end_date, location=location, notes=notes,
    )
    with _STORE_LOCK:
        _PROGRAMS[pid] = program
    _save_programs()
    return program


def get_program(pid):
    return _PROGRAMS.get(pid)


def list_programs(client_key=None, status=None):
    programs = list(_PROGRAMS.values())
    if client_key:
        programs = [p for p in programs if p.client_key == client_key]
    if status:
        programs = [p for p in programs if p.status == status]
    return sorted(programs, key=lambda p: p.created_at, reverse=True)


def update_program(pid, **kwargs):
    program = _PROGRAMS.get(pid)
    if not program:
        return None
    for k, v in kwargs.items():
        if hasattr(program, k):
            setattr(program, k, v)
    program.updated_at = datetime.now().isoformat()
    _save_programs()
    return program


def delete_program(pid):
    if pid not in _PROGRAMS:
        return False
    with _STORE_LOCK:
        del _PROGRAMS[pid]
        del_entries = [k for k, v in _ENTRIES.items() if getattr(v, 'program_id', None) == pid]
        del_cl = [k for k, v in _CHECKLISTS.items() if getattr(v, 'program_id', None) == pid]
        del_ev = [k for k, v in _EVIDENCE_REG.items() if getattr(v, 'program_id', None) == pid]
        del_ds = [k for k, v in _DAILY_SUMMARIES.items() if getattr(v, 'program_id', None) == pid]
        for k in del_entries:
            del _ENTRIES[k]
        for k in del_cl:
            del _CHECKLISTS[k]
        for k in del_ev:
            del _EVIDENCE_REG[k]
        for k in del_ds:
            del _DAILY_SUMMARIES[k]
    _save_entries()
    _save_checklists()
    _save_evidence()
    _save_summaries()
    return True


# ── Program Entry CRUD ────────────────────────────────────────────────────

def create_entry(program_id, day, date, start_time, end_time, department,
                 auditor, clause_refs, standard, description="", room=""):
    eid = uuid.uuid4().hex[:12]
    entry = AuditProgramEntry(
        id=eid, program_id=program_id, day=day, date=date,
        start_time=start_time, end_time=end_time,
        department=department, auditor=auditor,
        clause_refs=clause_refs, standard=standard,
        description=description, room=room,
    )
    with _STORE_LOCK:
        _ENTRIES[eid] = entry
    _save_entries()
    return entry


def get_entry(eid):
    return _ENTRIES.get(eid)


def list_entries(program_id, day=None):
    entries = [e for e in _ENTRIES.values() if e.program_id == program_id]
    if day is not None:
        entries = [e for e in entries if e.day == day]
    return sorted(entries, key=lambda e: (e.day, e.start_time))


def update_entry(eid, **kwargs):
    entry = _ENTRIES.get(eid)
    if not entry:
        return None
    for k, v in kwargs.items():
        if hasattr(entry, k):
            setattr(entry, k, v)
    _save_entries()
    return entry


def delete_entry(eid):
    with _STORE_LOCK:
        if eid in _ENTRIES:
            del _ENTRIES[eid]
    _save_entries()
    return True


# ── Clause Checklist CRUD ─────────────────────────────────────────────────

def build_checklist_for_program(program_id):
    program = _PROGRAMS.get(program_id)
    if not program:
        return []

    items = []
    for std in program.standards:
        all_items = get_all_clause_items(std)
        for ci in all_items:
            item = ClauseChecklistItem(
                id=uuid.uuid4().hex[:12],
                program_id=program_id,
                standard=std,
                clause_ref=ci['id'],
                clause_title=ci.get('title', ''),
                evidence_required=ci.get('evidence_text', ''),
                evidence_suggestions=ci.get('evidence', []),
            )
            with _STORE_LOCK:
                _CHECKLISTS[item.id] = item
            items.append(item)

    _save_checklists()
    return items


def get_checklist_item(cid):
    return _CHECKLISTS.get(cid)


def list_checklist(program_id, standard=None, status=None):
    items = [c for c in _CHECKLISTS.values() if c.program_id == program_id]
    if standard:
        items = [c for c in items if c.standard == standard]
    if status:
        items = [c for c in items if c.status == status]
    return items


def list_checklist_by_day(program_id, day):
    entries = list_entries(program_id, day=day)
    clause_refs = set()
    for e in entries:
        clause_refs.update(e.clause_refs)
    items = [c for c in _CHECKLISTS.values()
             if c.program_id == program_id and c.clause_ref in clause_refs]
    return items


def update_checklist_item(cid, **kwargs):
    item = _CHECKLISTS.get(cid)
    if not item:
        return None
    for k, v in kwargs.items():
        if hasattr(item, k):
            setattr(item, k, v)
    item.updated_at = datetime.now().isoformat()
    if kwargs.get('status') in ('minor_nc', 'major_nc', 'ofi'):
        item.reviewed = True
        item.reviewed_at = datetime.now().isoformat()
    _save_checklists()
    return item


def bulk_update_checklist(program_id, updates):
    results = []
    for item_id, fields in updates.items():
        item = _CHECKLISTS.get(item_id)
        if item and item.program_id == program_id:
            for k, v in fields.items():
                if hasattr(item, k):
                    setattr(item, k, v)
            item.updated_at = datetime.now().isoformat()
            results.append(item)
    _save_checklists()
    return results


# ── Evidence Register CRUD ────────────────────────────────────────────────

def add_evidence(program_id, clause_ref, standard, evidence_type,
                 description, collected_by, file_path=""):
    eid = uuid.uuid4().hex[:12]
    ev = EvidenceRegisterEntry(
        id=eid, program_id=program_id, clause_ref=clause_ref,
        standard=standard, evidence_type=evidence_type,
        description=description, collected_by=collected_by,
        file_path=file_path,
    )
    with _STORE_LOCK:
        _EVIDENCE_REG[eid] = ev
    _save_evidence()
    return ev


def list_evidence_register(program_id, clause_ref=None, standard=None):
    items = [e for e in _EVIDENCE_REG.values() if e.program_id == program_id]
    if clause_ref:
        items = [e for e in items if e.clause_ref == clause_ref]
    if standard:
        items = [e for e in items if e.standard == standard]
    return items


def update_evidence_entry(eid, **kwargs):
    ev = _EVIDENCE_REG.get(eid)
    if not ev:
        return None
    for k, v in kwargs.items():
        if hasattr(ev, k):
            setattr(ev, k, v)
    if kwargs.get('status') == 'reviewed' and not ev.reviewed_at:
        ev.reviewed_at = datetime.now().isoformat()
    _save_evidence()
    return ev


def delete_evidence_entry(eid):
    with _STORE_LOCK:
        if eid in _EVIDENCE_REG:
            del _EVIDENCE_REG[eid]
    _save_evidence()
    return True


# ── Daily Summary CRUD ────────────────────────────────────────────────────

def get_or_create_daily_summary(program_id, day, date_str):
    for s in _DAILY_SUMMARIES.values():
        if s.program_id == program_id and s.day == day:
            return s
    sid = uuid.uuid4().hex[:12]
    ds = AuditDailySummary(id=sid, program_id=program_id, day=day, date=date_str)
    with _STORE_LOCK:
        _DAILY_SUMMARIES[sid] = ds
    _save_summaries()
    return ds


def update_daily_summary(sid, **kwargs):
    ds = _DAILY_SUMMARIES.get(sid)
    if not ds:
        return None
    for k, v in kwargs.items():
        if hasattr(ds, k):
            setattr(ds, k, v)
    ds.updated_at = datetime.now().isoformat()
    _save_summaries()
    return ds


def list_daily_summaries(program_id):
    items = [s for s in _DAILY_SUMMARIES.values() if s.program_id == program_id]
    return sorted(items, key=lambda s: s.day)


# ── Analytics ─────────────────────────────────────────────────────────────

def get_program_overview(program_id):
    program = _PROGRAMS.get(program_id)
    if not program:
        return None

    entries = list_entries(program_id)
    checklist = list_checklist(program_id)
    evidence = list_evidence_register(program_id)
    summaries = list_daily_summaries(program_id)

    days = {}
    for e in entries:
        key = f"day_{e.day}"
        if key not in days:
            days[key] = {"day": e.day, "date": e.date, "entries": []}
        days[key]["entries"].append(e.to_dict())

    cl_stats = {
        "total": len(checklist),
        "pending": len([c for c in checklist if c.status == "pending"]),
        "conforming": len([c for c in checklist if c.status == "conforming"]),
        "minor_nc": len([c for c in checklist if c.status == "minor_nc"]),
        "major_nc": len([c for c in checklist if c.status == "major_nc"]),
        "ofi": len([c for c in checklist if c.status == "ofi"]),
        "na": len([c for c in checklist if c.status == "na"]),
    }
    cl_stats["reviewed"] = (cl_stats["conforming"] + cl_stats["minor_nc"] +
                            cl_stats["major_nc"] + cl_stats["ofi"] + cl_stats["na"])
    cl_stats["completion_pct"] = round((cl_stats["reviewed"] / cl_stats["total"]) * 100, 1) if cl_stats["total"] > 0 else 0

    ncs = [
        {"clause": c.clause_ref, "title": c.clause_title,
         "severity": c.severity or c.status,
         "description": c.nc_description or c.ofi_description,
         "standard": c.standard}
        for c in checklist if c.status in ("minor_nc", "major_nc", "ofi")
    ]

    return {
        "program": program.to_dict(),
        "days": days,
        "entries_flat": [e.to_dict() for e in entries],
        "checklist_stats": cl_stats,
        "evidence_count": len(evidence),
        "ncs": ncs,
        "daily_summaries": [s.to_dict() for s in summaries],
    }


def get_checklist_export(program_id):
    checklist = list_checklist(program_id)
    program = _PROGRAMS.get(program_id)
    if not program:
        return []

    standards = {}
    for c in checklist:
        std = c.standard
        if std not in standards:
            standards[std] = {"standard": std, "items": []}
        standards[std]["items"].append(c.to_dict())

    result = []
    for std in program.standards:
        if std in standards:
            result.append(standards[std])
    return result
