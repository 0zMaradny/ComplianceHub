@"
import pytest
from app.services.validator import (
    check_client_isolation,
    check_formula_integrity,
    check_clause_hallucinations,
    verify_evidence_traceability,
    verify_temporal_consistency,
    check_show_dont_tell,
    check_track_separation,
    check_template_structure,
    validate_output,
)


class TestT1WrongFormula:
    def test_sagco_with_moi_formula_flagged(self):
        content = """
        SAGCO Risk Register
        Risk Score: V = S × (1 − U/4) = 4 × (1 − 3/4) = 1.0
        """
        issues = check_formula_integrity(content, "SAGCO")
        assert len(issues) > 0
        assert any("WRONG FORMULA" in i for i in issues)

    def test_sagco_with_correct_formula_passes(self):
        content = "Risk Score: L × S = 3 × 4 = 12"
        issues = check_formula_integrity(content, "SAGCO")
        wrong_formula_issues = [i for i in issues if "WRONG FORMULA" in i]
        assert len(wrong_formula_issues) == 0


class TestT2ClientContamination:
    def test_uacc_mentioning_sagco_keywords_flagged(self):
        content = "Scope: All energy-consuming equipment including HFO burners and LPG storage."
        issues = check_client_isolation(content, "UACC")
        assert len(issues) > 0
        assert any("CLIENT CONTAMINATION" in i or "V1 FAIL" in i for i in issues)

    def test_uacc_clean_content_passes(self):
        content = "Scope: All VFDs, DCS systems, and steam turbines at the Taif plant."
        issues = check_client_isolation(content, "UACC")
        assert len(issues) == 0


class TestT3ClauseHallucination:
    def test_fake_clause_6_99_flagged(self):
        content = "Per ISO 9001 Clause 6.99, the organization must establish..."
        issues = check_clause_hallucinations(content)
        assert len(issues) > 0
        assert any("6.99" in i for i in issues)

    def test_real_clauses_pass(self):
        content = "Per ISO 9001 Clause 6.1.2 and Clause 10.2."
        issues = check_clause_hallucinations(content)
        assert len(issues) == 0


class TestT4EvidenceTraceability:
    def test_audit_finding_missing_clause_flagged(self):
        content = "The audit team found a gap in the process."
        issues = verify_evidence_traceability(content, "audit_finding")
        assert len(issues) > 0

    def test_capa_missing_owner_flagged(self):
        content = "Root Cause: training gap. Corrective: retrain staff."
        issues = verify_evidence_traceability(content, "capa_plan")
        assert any("Owner" in i for i in issues)


class TestT5TemporalConsistency:
    def test_future_date_flagged(self):
        content = "Deadline: 15/08/2030"
        issues = verify_temporal_consistency(content)
        assert any("FUTURE DATE" in i for i in issues)

    def test_wrong_client_formula_flagged(self):
        content = "Risk = L × S"
        memory_ref = {"active_client": "Al-Ahsa"}
        issues = verify_temporal_consistency(content, memory_ref)
        assert any("WRONG CLIENT FORMULA" in i or "V7 FAIL" in i for i in issues)


class TestT6QualityGates:
    def test_show_dont_tell_meta_commentary_flagged(self):
        content = "Here's a concise version of the audit report as requested."
        issues = check_show_dont_tell(content)
        assert len(issues) > 0

    def test_track_a_with_solutions_flagged(self):
        content = "The audit team found a gap. We recommend implementing a new system."
        issues = check_track_separation(content, "audit_report")
        assert len(issues) > 0

    def test_template_structure_missing_section_flagged(self):
        content = "Risk ID: R001. Likelihood: 3. Severity: 4."
        issues = check_template_structure(content, "risk_register")
        assert any("Risk Level" in i or "G10 FAIL" in i for i in issues)


class TestT7Integration:
    @pytest.mark.asyncio
    async def test_bad_content_fails(self):
        content = """
        SAGCO Risk Register
        Per ISO 9001 Clause 6.99 requirements.
        Risk Score: V = S × (1 − U/4) = 1.0
        Reference: UACC-EnMS-POL-001
        Here's a concise summary as requested.
        """
        result = await validate_output(content, "SAGCO", "risk_register")
        assert result["passed"] is False
        assert len(result["issues"]) >= 3

    @pytest.mark.asyncio
    async def test_valid_content_passes(self):
        content = """
        SAGCO Risk Register
        Document Code: SAGCO-IMS-RSK-001
        Risk Rating: L × S = 3 × 4 = 12
        Risk Level: High
        """
        result = await validate_output(content, "SAGCO", "risk_register")
        assert result["passed"] is True
"@ | Out-File -FilePath "tests\test_validator.py" -Encoding UTF8
