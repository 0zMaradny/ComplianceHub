"""Tests for the Surveillance Audit Module.

Tests cover: cycle creation, auto-typing, scope generation, finding management,
auto-scheduling, overdue detection, and dashboard statistics.
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Override data directory to a temp dir before importing
_test_dir = tempfile.mkdtemp()


def _setup_test_env():
    """Set up isolated test data directory."""
    from app.services import surveillance as surv_mod
    surv_mod.DATA_DIR = _test_dir
    surv_mod.CYCLES_FILE = os.path.join(_test_dir, 'surveillance.json')
    surv_mod.FINDINGS_FILE = os.path.join(_test_dir, 'surveillance_findings.json')
    surv_mod._CYCLES.clear()
    surv_mod._FINDINGS.clear()


def teardown_function():
    """Clean up temp files after each test."""
    if os.path.exists(_test_dir):
        shutil.rmtree(_test_dir, ignore_errors=True)


# ── Test Fixtures ──

@pytest.fixture(autouse=True)
def isolated_data():
    """Provide isolated surveillance data for each test."""
    _setup_test_env()
    yield
    teardown_function()


def _make_cycle(project_id="proj-001", cycle_number=1, scheduled_date=None, notes=""):
    from app.services.surveillance import create_surveillance_cycle
    if not scheduled_date:
        scheduled_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    return create_surveillance_cycle(project_id, cycle_number, scheduled_date, notes)


# ── Cycle Creation & Auto-Typing ──

class TestCycleCreation:
    def test_create_surveillance_cycle_basic(self):
        cycle = _make_cycle()
        assert cycle.id.startswith("SRV-")
        assert cycle.project_id == "proj-001"
        assert cycle.cycle_number == 1
        assert cycle.status == "scheduled"
        assert cycle.created_at != ""

    def test_cycle_type_surveillance_for_cycle_1(self):
        cycle = _make_cycle(cycle_number=1)
        assert cycle.cycle_type == "surveillance"
        assert cycle.scope_reduction_pct == 30

    def test_cycle_type_surveillance_for_cycle_2(self):
        cycle = _make_cycle(cycle_number=2)
        assert cycle.cycle_type == "surveillance"
        assert cycle.scope_reduction_pct == 30

    def test_cycle_type_recertification_for_cycle_3(self):
        cycle = _make_cycle(cycle_number=3)
        assert cycle.cycle_type == "recertification"
        assert cycle.scope_reduction_pct == 0

    def test_surveillance_flags_default(self):
        cycle = _make_cycle()
        assert cycle.previous_ncs_only is True
        assert cycle.changes_reviewed is True

    def test_recertification_flags(self):
        cycle = _make_cycle(cycle_number=3)
        # Recertification: previous_ncs_only = False (cycle_type != "surveillance")
        assert cycle.previous_ncs_only is False
        assert cycle.changes_reviewed is True

    def test_cycle_notes_preserved(self):
        cycle = _make_cycle(notes="Year 1 surveillance after initial cert")
        assert cycle.notes == "Year 1 surveillance after initial cert"


# ── Cycle Retrieval & Listing ──

class TestCycleRetrieval:
    def test_get_surveillance_cycle(self):
        cycle = _make_cycle()
        from app.services.surveillance import get_surveillance_cycle
        fetched = get_surveillance_cycle(cycle.id)
        assert fetched is not None
        assert fetched.id == cycle.id

    def test_get_nonexistent_cycle(self):
        from app.services.surveillance import get_surveillance_cycle
        assert get_surveillance_cycle("SRV-NONEXIST") is None

    def test_list_by_project_id(self):
        _make_cycle(project_id="proj-A", cycle_number=1)
        _make_cycle(project_id="proj-A", cycle_number=2)
        _make_cycle(project_id="proj-B", cycle_number=1)
        from app.services.surveillance import list_surveillance_cycles
        result = list_surveillance_cycles(project_id="proj-A")
        assert len(result) == 2

    def test_list_by_status(self):
        c1 = _make_cycle()
        from app.services.surveillance import update_surveillance_cycle
        update_surveillance_cycle(c1.id, status="in_progress")
        _make_cycle()
        from app.services.surveillance import list_surveillance_cycles
        result = list_surveillance_cycles(status="in_progress")
        assert len(result) == 1
        assert result[0].status == "in_progress"


# ── Cycle Updates ──

class TestCycleUpdates:
    def test_update_status(self):
        cycle = _make_cycle()
        from app.services.surveillance import update_surveillance_cycle
        updated = update_surveillance_cycle(cycle.id, status="in_progress")
        assert updated is not None
        assert updated.status == "in_progress"

    def test_update_scheduled_date(self):
        cycle = _make_cycle()
        from app.services.surveillance import update_surveillance_cycle
        updated = update_surveillance_cycle(cycle.id, scheduled_date="2027-06-15")
        assert updated.scheduled_date == "2027-06-15"

    def test_update_nonexistent_returns_none(self):
        from app.services.surveillance import update_surveillance_cycle
        result = update_surveillance_cycle("SRV-FAKE", status="completed")
        assert result is None


# ── Scope Generation ──

class TestScopeGeneration:
    def test_generate_scope_surveillance_reduces_clauses(self):
        """Surveillance scope should be reduced (excluded_clauses not empty)."""
        from app.services.audit_workflow import create_project
        from app.services.surveillance import generate_surveillance_scope

        # Create a project first
        project = create_project("msd_moi", "Test Project", ["iso_27001"])
        cycle = _make_cycle(project_id=project.id, cycle_number=1)

        scope = generate_surveillance_scope(project.id, cycle.id)
        assert "error" not in scope
        assert scope["cycle_type"] == "surveillance"
        assert scope["manday_reduction_pct"] == 30
        assert len(scope["included_clauses"]) > 0
        assert "4" in scope["included_clauses"]  # Critical clause always included
        assert "excluded_clauses" in scope

    def test_generate_scope_recertification_full_scope(self):
        """Recertification scope should have 0% reduction and full scope."""
        from app.services.audit_workflow import create_project
        from app.services.surveillance import generate_surveillance_scope, get_surveillance_cycle

        project = create_project("msd_moi", "Test Project", ["iso_27001"])
        cycle = _make_cycle(project_id=project.id, cycle_number=3)

        scope = generate_surveillance_scope(project.id, cycle.id)
        assert "error" not in scope
        assert scope["cycle_type"] == "recertification"
        assert scope["manday_reduction_pct"] == 0
        assert len(scope["excluded_clauses"]) == 0  # Full scope

    def test_generate_scope_nonexistent_cycle(self):
        from app.services.surveillance import generate_surveillance_scope
        scope = generate_surveillance_scope("proj-123", "SRV-FAKE")
        assert "error" in scope

    def test_rationale_includes_nc_count(self):
        from app.services.audit_workflow import create_project, create_nc
        from app.services.surveillance import generate_surveillance_scope

        project = create_project("msd_moi", "Test Project", ["iso_27001"])
        create_nc(project.id, "4.1", "Minor", "Previous gap in context analysis")
        cycle = _make_cycle(project_id=project.id, cycle_number=1)

        scope = generate_surveillance_scope(project.id, cycle.id)
        assert "previous_nc_count" in scope
        assert scope["previous_nc_count"] >= 1


# ── Finding Management ──

class TestFindingManagement:
    def test_create_surveillance_finding(self):
        from app.services.surveillance import create_surveillance_finding

        cycle = _make_cycle()
        finding = create_surveillance_finding(
            cycle_id=cycle.id,
            clause="4.1",
            finding_type="new_nc",
            severity="Minor",
            description="Organizational context not updated",
        )
        assert finding is not None
        assert finding.id.startswith("SF-")
        assert finding.clause == "4.1"
        assert finding.finding_type == "new_nc"
        assert finding.severity == "Minor"
        assert finding.status == "open"

    def test_create_finding_with_previous_nc_link(self):
        from app.services.surveillance import create_surveillance_finding

        cycle = _make_cycle()
        finding = create_surveillance_finding(
            cycle_id=cycle.id,
            clause="6.1",
            finding_type="recurring_nc",
            severity="Major",
            description="Risk assessment still not comprehensive",
            previous_nc_id="NC-ORIG001",
        )
        assert finding.finding_type == "recurring_nc"
        assert finding.previous_nc_id == "NC-ORIG001"

    def test_create_finding_nonexistent_cycle(self):
        from app.services.surveillance import create_surveillance_finding
        result = create_surveillance_finding(
            cycle_id="SRV-FAKE", clause="4.1",
            finding_type="new_nc", severity="Minor", description="test",
        )
        assert result is None

    def test_list_findings_by_cycle(self):
        from app.services.surveillance import create_surveillance_finding, list_surveillance_findings

        cycle = _make_cycle()
        create_surveillance_finding(cycle.id, "4.1", "new_nc", "Minor", "Finding 1")
        create_surveillance_finding(cycle.id, "6.1", "ofi", "OFI", "Finding 2")

        findings = list_surveillance_findings(cycle_id=cycle.id)
        assert len(findings) == 2

    def test_list_findings_by_project(self):
        from app.services.surveillance import create_surveillance_finding, list_surveillance_findings

        c1 = _make_cycle(project_id="proj-X", cycle_number=1)
        c2 = _make_cycle(project_id="proj-Y", cycle_number=1)
        create_surveillance_finding(c1.id, "4.1", "new_nc", "Minor", "F1")
        create_surveillance_finding(c2.id, "5.1", "new_nc", "Major", "F2")

        findings = list_surveillance_findings(project_id="proj-X")
        assert len(findings) == 1
        assert findings[0].project_id == "proj-X"


# ── Auto-Scheduling ──

class TestAutoScheduling:
    def test_auto_schedule_creates_three_cycles(self):
        from app.services.surveillance import auto_schedule_surveillance, list_surveillance_cycles

        cycles = auto_schedule_surveillance("proj-auto", "2025-01-15")
        assert len(cycles) == 3

        # Verify cycle numbers
        cycle_numbers = [c.cycle_number for c in cycles]
        assert sorted(cycle_numbers) == [1, 2, 3]

    def test_auto_schedule_cycle_types(self):
        from app.services.surveillance import auto_schedule_surveillance

        cycles = auto_schedule_surveillance("proj-auto", "2025-01-15")
        cycle_1 = [c for c in cycles if c.cycle_number == 1][0]
        cycle_2 = [c for c in cycles if c.cycle_number == 2][0]
        cycle_3 = [c for c in cycles if c.cycle_number == 3][0]

        assert cycle_1.cycle_type == "surveillance"
        assert cycle_2.cycle_type == "surveillance"
        assert cycle_3.cycle_type == "recertification"

    def test_auto_schedule_dates(self):
        from app.services.surveillance import auto_schedule_surveillance

        cycles = auto_schedule_surveillance("proj-auto", "2025-01-15")
        cycle_1 = [c for c in cycles if c.cycle_number == 1][0]
        cycle_2 = [c for c in cycles if c.cycle_number == 2][0]
        cycle_3 = [c for c in cycles if c.cycle_number == 3][0]

        # Cycle 1 ~ 12 months from cert date
        assert "2026-01" in cycle_1.scheduled_date
        # Cycle 2 ~ 24 months from cert date
        assert "2027-01" in cycle_2.scheduled_date
        # Cycle 3 ~ 36 months from cert date
        assert "2028-01" in cycle_3.scheduled_date

    def test_auto_schedule_invalid_date(self):
        from app.services.surveillance import auto_schedule_surveillance
        result = auto_schedule_surveillance("proj-auto", "not-a-date")
        assert result == []


# ── Overdue Detection ──

class TestOverdueDetection:
    def test_check_overdue_marks_past_cycles(self):
        from app.services.surveillance import check_overdue_cycles, create_surveillance_cycle

        past_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cycle = create_surveillance_cycle("proj-001", 1, past_date, "Should be overdue")
        assert cycle.status == "scheduled"

        overdue = check_overdue_cycles()
        assert len(overdue) >= 1
        # Verify the cycle was updated in the store
        from app.services.surveillance import get_surveillance_cycle
        updated = get_surveillance_cycle(cycle.id)
        assert updated.status == "overdue"

    def test_check_overdue_skips_completed(self):
        from app.services.surveillance import check_overdue_cycles, create_surveillance_cycle, update_surveillance_cycle

        past_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        cycle = create_surveillance_cycle("proj-001", 1, past_date, "Completed already")
        update_surveillance_cycle(cycle.id, status="completed")

        overdue = check_overdue_cycles()
        from app.services.surveillance import get_surveillance_cycle
        updated = get_surveillance_cycle(cycle.id)
        assert updated.status == "completed"  # Not changed to overdue

    def test_check_overdue_skips_future(self):
        from app.services.surveillance import check_overdue_cycles, create_surveillance_cycle

        future_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        cycle = create_surveillance_cycle("proj-001", 1, future_date, "Future cycle")

        overdue = check_overdue_cycles()
        from app.services.surveillance import get_surveillance_cycle
        updated = get_surveillance_cycle(cycle.id)
        assert updated.status == "scheduled"  # Not overdue


# ── Dashboard Stats ──

class TestDashboardStats:
    def test_empty_dashboard(self):
        from app.services.surveillance import get_surveillance_dashboard_stats

        stats = get_surveillance_dashboard_stats()
        assert stats["total_cycles"] == 0
        assert stats["upcoming_30d"] == 0
        assert stats["overdue"] == 0
        assert stats["recurring_nc_rate"] == 0.0
        assert stats["avg_reduction_pct"] == 0.0

    def test_dashboard_with_cycles(self):
        from app.services.surveillance import get_surveillance_dashboard_stats, create_surveillance_cycle

        create_surveillance_cycle("proj-001", 1, "2026-01-15", "")
        create_surveillance_cycle("proj-001", 2, "2027-01-15", "")
        create_surveillance_cycle("proj-001", 3, "2028-01-15", "")

        stats = get_surveillance_dashboard_stats()
        assert stats["total_cycles"] == 3
        # 2 surveillance at 30% + 1 recert at 0% = avg 20%
        assert stats["avg_reduction_pct"] == 20.0

    def test_dashboard_with_findings(self):
        from app.services.surveillance import (
            get_surveillance_dashboard_stats,
            create_surveillance_cycle,
            create_surveillance_finding,
        )

        cycle = create_surveillance_cycle("proj-001", 1, "2026-01-15", "")
        create_surveillance_finding(cycle.id, "4.1", "recurring_nc", "Major", "Recurring issue")
        create_surveillance_finding(cycle.id, "6.1", "new_nc", "Minor", "New issue")
        create_surveillance_finding(cycle.id, "7.1", "ofi", "OFI", "Opportunity")

        stats = get_surveillance_dashboard_stats()
        assert stats["total_findings"] == 3
        assert stats["major_findings"] == 1
        # 1 recurring out of 3 = 33.3%
        assert stats["recurring_nc_rate"] == 33.3

    def test_dashboard_status_breakdown(self):
        from app.services.surveillance import (
            get_surveillance_dashboard_stats,
            create_surveillance_cycle,
            update_surveillance_cycle,
        )

        c1 = create_surveillance_cycle("proj-001", 1, "2026-01-15", "")
        c2 = create_surveillance_cycle("proj-001", 2, "2027-01-15", "")
        update_surveillance_cycle(c1.id, status="in_progress")

        stats = get_surveillance_dashboard_stats()
        assert stats["status_breakdown"]["in_progress"] == 1
        assert stats["status_breakdown"]["scheduled"] == 1


# ── API Endpoint Tests ──

class TestAPIEndpoints:
    @pytest.fixture
    def api_client(self):
        from app.main import app
        from fastapi.testclient import TestClient
        return TestClient(app)

    def test_create_cycle_endpoint(self, api_client):
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-api-1",
            "cycle_number": "1",
            "scheduled_date": "2026-06-15",
            "notes": "API test cycle",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["cycle"]["cycle_type"] == "surveillance"

    def test_create_cycle_missing_fields(self, api_client):
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-api-1",
        })
        assert r.status_code == 400

    def test_create_cycle_invalid_number(self, api_client):
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-api-1",
            "cycle_number": "5",
            "scheduled_date": "2026-06-15",
        })
        assert r.status_code == 400

    def test_list_cycles_endpoint(self, api_client):
        # Create a cycle first
        api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-list",
            "cycle_number": "1",
            "scheduled_date": "2026-06-15",
        })
        r = api_client.get("/api/surveillance/cycles?project_id=proj-list")
        assert r.status_code == 200
        data = r.json()
        assert len(data["cycles"]) >= 1

    def test_get_cycle_endpoint(self, api_client):
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-get",
            "cycle_number": "1",
            "scheduled_date": "2026-06-15",
        })
        cycle_id = r.json()["cycle"]["id"]
        r = api_client.get(f"/api/surveillance/cycles/{cycle_id}")
        assert r.status_code == 200
        assert r.json()["id"] == cycle_id

    def test_get_nonexistent_cycle_endpoint(self, api_client):
        r = api_client.get("/api/surveillance/cycles/SRV-NONEXIST")
        assert r.status_code == 404

    def test_add_finding_endpoint(self, api_client):
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-finding",
            "cycle_number": "1",
            "scheduled_date": "2026-06-15",
        })
        cycle_id = r.json()["cycle"]["id"]
        r = api_client.post(f"/api/surveillance/cycles/{cycle_id}/findings", data={
            "clause": "4.1",
            "finding_type": "new_nc",
            "severity": "Minor",
            "description": "Test finding via API",
        })
        assert r.status_code == 200
        assert r.json()["clause"] == "4.1"

    def test_list_findings_endpoint(self, api_client):
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": "proj-list-find",
            "cycle_number": "1",
            "scheduled_date": "2026-06-15",
        })
        cycle_id = r.json()["cycle"]["id"]
        api_client.post(f"/api/surveillance/cycles/{cycle_id}/findings", data={
            "clause": "4.1", "finding_type": "new_nc",
            "severity": "Minor", "description": "F1",
        })
        r = api_client.get(f"/api/surveillance/cycles/{cycle_id}/findings")
        assert r.status_code == 200
        assert len(r.json()["findings"]) >= 1

    def test_auto_schedule_endpoint(self, api_client):
        r = api_client.post("/api/projects/proj-auto-api/auto-schedule", params={
            "cert_date": "2025-01-15",
        })
        assert r.status_code == 200
        assert len(r.json()["cycles"]) == 3

    def test_auto_schedule_missing_date(self, api_client):
        r = api_client.post("/api/projects/proj-auto-api/auto-schedule")
        assert r.status_code == 400

    def test_dashboard_endpoint(self, api_client):
        r = api_client.get("/api/surveillance/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert "total_cycles" in data
        assert "upcoming_30d" in data
        assert "overdue" in data

    def test_check_overdue_endpoint(self, api_client):
        r = api_client.post("/api/surveillance/check-overdue")
        assert r.status_code == 200
        data = r.json()
        assert "newly_overdue" in data

    def test_scope_endpoint(self, api_client):
        from app.services.audit_workflow import create_project
        project = create_project("msd_moi", "Scope Test Project", ["iso_27001"])
        r = api_client.post("/api/surveillance/cycles", data={
            "project_id": project.id,
            "cycle_number": "1",
            "scheduled_date": "2026-06-15",
        })
        cycle_id = r.json()["cycle"]["id"]
        r = api_client.post(f"/api/surveillance/cycles/{cycle_id}/scope")
        assert r.status_code == 200
        data = r.json()
        assert "included_clauses" in data
        assert "manday_reduction_pct" in data
