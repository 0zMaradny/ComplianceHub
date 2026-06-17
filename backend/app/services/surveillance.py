"""Surveillance Audit Module — surveillance and recertification cycle management.

Manages post-certification surveillance audit cycles:
  - After initial certification (Gate 6 complete), projects enter "surveillance" status
  - Surveillance audits happen annually (Year 1, Year 2)
  - Recertification happens at Year 3
  - Surveillance scope is reduced vs initial cert — only critical clauses + previous NC areas + changes
  - Each surveillance cycle generates its own docs (reduced set)
"""

import os
import json
import logging
import uuid
import threading
from datetime import datetime
from dataclasses import dataclass, asdict
from app.services.clause_data import get_clause_data

logger = logging.getLogger(__name__)


@dataclass
class SurveillanceCycle:
    id: str
    project_id: str
    cycle_number: int  # 1, 2, or 3 (3 = recertification)
    cycle_type: str    # "surveillance" or "recertification"
    status: str        # "scheduled" | "in_progress" | "completed" | "overdue"
    scheduled_date: str = ""
    completed_date: str = ""
    scope_reduction_pct: int = 30  # 30% reduction for surveillance, 0 for recert
    previous_ncs_only: bool = True  # focus on previous NC clauses
    changes_reviewed: bool = True   # organizational changes since last audit
    created_at: str = ""
    notes: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class SurveillanceFinding:
    id: str
    cycle_id: str
    project_id: str
    clause: str
    finding_type: str  # "recurring_nc" | "new_nc" | "ofi" | "observation"
    severity: str      # "Major" | "Minor" | "OFI"
    description: str
    previous_nc_id: str = ""  # link to original NC if recurring
    status: str = "open"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# Critical clauses that are always in scope for surveillance audits
# These are the HLS core clauses that certification bodies always review
CRITICAL_CLAUSES = [
    "4",   # Context of the Organization
    "5",   # Leadership
    "6",   # Planning
    "7",   # Support
    "8",   # Operation
    "9",   # Performance Evaluation
    "10",  # Improvement
]

_CYCLES: dict = {}
_FINDINGS: dict = {}
_STORE_LOCK = threading.Lock()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
CYCLES_FILE = os.path.join(DATA_DIR, 'surveillance.json')
FINDINGS_FILE = os.path.join(DATA_DIR, 'surveillance_findings.json')


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _save_cycles():
    _ensure_data_dir()
    with _STORE_LOCK:
        data = {k: v.to_dict() for k, v in _CYCLES.items()}
        with open(CYCLES_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _save_findings():
    _ensure_data_dir()
    with _STORE_LOCK:
        data = {k: v.to_dict() for k, v in _FINDINGS.items()}
        with open(FINDINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def _load_all():
    _ensure_data_dir()
    global _CYCLES, _FINDINGS
    with _STORE_LOCK:
        if os.path.exists(CYCLES_FILE):
            with open(CYCLES_FILE) as f:
                _CYCLES = {k: SurveillanceCycle.from_dict(v) for k, v in json.load(f).items()}
        if os.path.exists(FINDINGS_FILE):
            with open(FINDINGS_FILE) as f:
                _FINDINGS = {k: SurveillanceFinding.from_dict(v) for k, v in json.load(f).items()}


_load_all()


def _determine_cycle_type(cycle_number):
    """Auto-set cycle_type based on cycle_number: 1-2=surveillance, 3=recertification."""
    if cycle_number == 3:
        return "recertification"
    return "surveillance"


def _determine_scope_reduction(cycle_number):
    """Surveillance cycles get 30% manday reduction; recertification gets 0%."""
    if cycle_number == 3:
        return 0
    return 30


def create_surveillance_cycle(project_id, cycle_number, scheduled_date, notes=""):
    """Create a new surveillance/recertification cycle.

    Auto-sets cycle_type based on cycle_number (1-2=surveillance, 3=recertification).
    Auto-sets scope_reduction_pct (30 for surveillance, 0 for recertification).
    """
    cycle_id = f"SRV-{uuid.uuid4().hex[:8].upper()}"
    cycle_type = _determine_cycle_type(cycle_number)
    scope_reduction = _determine_scope_reduction(cycle_number)
    cycle = SurveillanceCycle(
        id=cycle_id,
        project_id=project_id,
        cycle_number=cycle_number,
        cycle_type=cycle_type,
        status="scheduled",
        scheduled_date=scheduled_date,
        scope_reduction_pct=scope_reduction,
        previous_ncs_only=(cycle_type == "surveillance"),
        changes_reviewed=True,
        notes=notes,
    )
    with _STORE_LOCK:
        _CYCLES[cycle_id] = cycle
    _save_cycles()
    return cycle


def get_surveillance_cycle(cycle_id):
    """Get a surveillance cycle by ID."""
    return _CYCLES.get(cycle_id)


def list_surveillance_cycles(project_id=None, status=None):
    """List surveillance cycles with optional filters."""
    cycles = list(_CYCLES.values())
    if project_id:
        cycles = [c for c in cycles if c.project_id == project_id]
    if status:
        cycles = [c for c in cycles if c.status == status]
    return sorted(cycles, key=lambda c: c.created_at, reverse=True)


def update_surveillance_cycle(cycle_id, **kwargs):
    """Update a surveillance cycle's fields."""
    cycle = _CYCLES.get(cycle_id)
    if not cycle:
        return None
    for key, value in kwargs.items():
        if hasattr(cycle, key):
            setattr(cycle, key, value)
    _save_cycles()
    return cycle


def generate_surveillance_scope(project_id, cycle_id):
    """Compute reduced scope for a surveillance audit.

    Takes the previous audit's NC clauses + critical clauses + any changes.
    Returns a dict with included_clauses, excluded_clauses, rationale, manday_reduction_pct.
    """
    from app.services.audit_workflow import get_project, list_ncs

    cycle = _CYCLES.get(cycle_id)
    if not cycle:
        return {"error": "Cycle not found"}

    project = get_project(project_id)
    if not project:
        return {"error": "Project not found"}

    # Gather all clauses from the project's standards
    all_clauses = set()
    for std_key in project.standards:
        try:
            clause_data = get_clause_data(std_key)
            if isinstance(clause_data, dict):
                # Framework standards (ISO 31000, ISO 10002)
                if "sections" in clause_data and isinstance(clause_data["sections"], dict):
                    for sid in clause_data["sections"]:
                        all_clauses.add(sid)
                else:
                    for cid in clause_data:
                        all_clauses.add(str(cid))
                        entry = clause_data[cid]
                        if isinstance(entry, dict):
                            sub = entry.get("sub_clauses", {})
                            if isinstance(sub, dict):
                                for sub_id in sub:
                                    all_clauses.add(sub_id)
        except Exception as e:
            logger.warning("Failed to collect clauses: %s", e)

    # Always include critical clauses
    included = set(CRITICAL_CLAUSES)
    rationale_parts = [
        "Critical HLS clauses (4-10) always included per certification body requirements.",
    ]

    # Add previous NC clauses
    previous_ncs = list_ncs(project_id=project_id)
    nc_clauses = set()
    for nc in previous_ncs:
        nc_clauses.add(nc.clause.split(".")[0])  # top-level clause
        nc_clauses.add(nc.clause)
    if nc_clauses:
        included.update(nc_clauses)
        rationale_parts.append(f"{len(nc_clauses)} clause(s) from previous NCs included.")

    # For recertification, full scope
    if cycle.cycle_type == "recertification":
        included = all_clauses
        excluded = set()
        manday_reduction = 0
        rationale_parts = ["Recertification requires full scope — no reduction applied."]
    else:
        excluded = all_clauses - included
        manday_reduction = cycle.scope_reduction_pct

    return {
        "cycle_id": cycle_id,
        "project_id": project_id,
        "cycle_type": cycle.cycle_type,
        "cycle_number": cycle.cycle_number,
        "included_clauses": sorted(included),
        "excluded_clauses": sorted(excluded),
        "rationale": " ".join(rationale_parts),
        "manday_reduction_pct": manday_reduction,
        "previous_nc_count": len(previous_ncs),
        "total_clauses": len(all_clauses),
    }


def create_surveillance_finding(cycle_id, clause, finding_type, severity, description, previous_nc_id=""):
    """Create a new finding (NC, OFI, observation) for a surveillance cycle."""
    cycle = _CYCLES.get(cycle_id)
    if not cycle:
        return None
    finding_id = f"SF-{uuid.uuid4().hex[:8].upper()}"
    finding = SurveillanceFinding(
        id=finding_id,
        cycle_id=cycle_id,
        project_id=cycle.project_id,
        clause=clause,
        finding_type=finding_type,
        severity=severity,
        description=description,
        previous_nc_id=previous_nc_id,
    )
    with _STORE_LOCK:
        _FINDINGS[finding_id] = finding
    _save_findings()
    return finding


def get_surveillance_finding(finding_id):
    """Get a surveillance finding by ID."""
    return _FINDINGS.get(finding_id)


def list_surveillance_findings(cycle_id=None, project_id=None):
    """List surveillance findings with optional filters."""
    findings = list(_FINDINGS.values())
    if cycle_id:
        findings = [f for f in findings if f.cycle_id == cycle_id]
    if project_id:
        findings = [f for f in findings if f.project_id == project_id]
    return sorted(findings, key=lambda f: f.created_at, reverse=True)


def update_surveillance_finding(finding_id, **kwargs):
    """Update a surveillance finding."""
    finding = _FINDINGS.get(finding_id)
    if not finding:
        return None
    for key, value in kwargs.items():
        if hasattr(finding, key):
            setattr(finding, key, value)
    _save_findings()
    return finding


def get_surveillance_dashboard_stats():
    """Return surveillance-specific dashboard statistics.

    Returns: total_cycles, upcoming_30d, overdue, recurring_nc_rate, avg_reduction_pct
    """
    cycles = list(_CYCLES.values())
    findings = list(_FINDINGS.values())

    total_cycles = len(cycles)

    # Upcoming within 30 days
    now = datetime.now()
    upcoming_30d = 0
    for c in cycles:
        if c.status == "scheduled" and c.scheduled_date:
            try:
                sd = datetime.strptime(c.scheduled_date, "%Y-%m-%d")
                if 0 <= (sd - now).days <= 30:
                    upcoming_30d += 1
            except (ValueError, TypeError):
                pass

    # Overdue count
    overdue = len([c for c in cycles if c.status == "overdue"])

    # Recurring NC rate
    if findings:
        recurring = len([f for f in findings if f.finding_type == "recurring_nc"])
        recurring_nc_rate = round(recurring / len(findings) * 100, 1)
    else:
        recurring_nc_rate = 0.0

    # Average scope reduction pct
    if cycles:
        avg_reduction_pct = round(
            sum(c.scope_reduction_pct for c in cycles) / len(cycles), 1
        )
    else:
        avg_reduction_pct = 0.0

    # Status breakdown
    status_counts = {}
    for c in cycles:
        status_counts[c.status] = status_counts.get(c.status, 0) + 1

    return {
        "total_cycles": total_cycles,
        "upcoming_30d": upcoming_30d,
        "overdue": overdue,
        "recurring_nc_rate": recurring_nc_rate,
        "avg_reduction_pct": avg_reduction_pct,
        "status_breakdown": status_counts,
        "total_findings": len(findings),
        "open_findings": len([f for f in findings if f.status == "open"]),
        "major_findings": len([f for f in findings if f.severity == "Major"]),
    }


def auto_schedule_surveillance(project_id, cert_date):
    """Auto-create 3 surveillance cycles from a certification date.

    Year 1: cert_date + 12 months (surveillance)
    Year 2: cert_date + 24 months (surveillance)
    Year 3: cert_date + 36 months (recertification)
    """
    try:
        cert_dt = datetime.strptime(cert_date, "%Y-%m-%d")
    except (ValueError, TypeError):
        return []

    cycles = []
    schedules = [
        (1, 12, "annual surveillance audit" ),
        (2, 24, "annual surveillance audit"),
        (3, 36, "recertification audit"),
    ]

    for cycle_num, months_offset, label in schedules:
        # Proper calendar month arithmetic
        m = cert_dt.month + months_offset
        y = cert_dt.year + (m - 1) // 12
        m = (m - 1) % 12 + 1
        d = min(cert_dt.day, 28)  # avoid month-end overflow
        scheduled_dt = cert_dt.replace(year=y, month=m, day=d)
        cycle = create_surveillance_cycle(
            project_id=project_id,
            cycle_number=cycle_num,
            scheduled_date=scheduled_dt.strftime("%Y-%m-%d"),
            notes=f"Year {cycle_num} {label} — auto-scheduled from cert date {cert_date}",
        )
        cycles.append(cycle)

    return cycles


def check_overdue_cycles():
    """Mark cycles past their scheduled_date as 'overdue'.

    Only cycles with status 'scheduled' or 'in_progress' are checked.
    Returns the list of newly overdue cycles.
    """
    now = datetime.now().strftime("%Y-%m-%d")
    newly_overdue = []
    with _STORE_LOCK:
        for cycle in _CYCLES.values():
            if cycle.status in ("scheduled", "in_progress") and cycle.scheduled_date:
                if cycle.scheduled_date < now:
                    cycle.status = "overdue"
                    newly_overdue.append(cycle)
    if newly_overdue:
        _save_cycles()
    return newly_overdue


def _reset_data():
    """Clear all in-memory data and delete persistence files. For testing only."""
    # Access module-level globals via globals() to avoid pyflaws false positive
    g = globals()
    with _STORE_LOCK:
        g['_CYCLES'].clear()
        g['_FINDINGS'].clear()
    for f in (CYCLES_FILE, FINDINGS_FILE):
        if os.path.exists(f):
            os.remove(f)
