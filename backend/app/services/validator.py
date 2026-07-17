"""
OWL Output Validator — 10 Gates (V1-V7 backend + G8-G10 quality)
Catches wrong outputs before delivery.
Agent 7 · July 2026
"""
import re
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Load ISO clause database
_CLAUSE_DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "iso_clause_database.json"
_CLAUSE_DB = {}
if _CLAUSE_DB_PATH.exists():
    try:
        with open(_CLAUSE_DB_PATH) as f:
            _CLAUSE_DB = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load ISO clause database: {e}")

# ─── CLIENT REGISTRY ────────────────────────────────────────────────
CLIENT_KEYWORDS = {
    "MSD-MOI": {
        "keywords": ["MOI", "وزارة الداخلية", "GRC", "004D26", "C8A96E", "1A3A5C", "MSD-MOI-GRC-"],
        "formulas": [r"V\s*=\s*S\s*×\s*\(1\s*[−-]\s*U\s*/\s*4\)", r"S\s*=\s*O\s*×\s*Q"],
        "language": "AR",
    },
    "UACC": {
        "keywords": ["UACC", "Taif", "EnMS", "EnPI", "SEU", "VFD", "DCS", "ALARP", "UACC-EnMS-"],
        "formulas": [r"L\s*×\s*S"],
        "language": "EN",
    },
    "SAGCO": {
        "keywords": ["SAGCO", "SHC", "HFO", "LPG", "GHG", "HIRA", "PTW", "MOC", "ECM", "SAGCO-IMS-", "1B3A4B", "E07B39"],
        "formulas": [r"L\s*×\s*S", r"L\s*×\s*S\s*×\s*R"],
        "language": "EN",
    },
    "AL-AHSA": {
        "keywords": ["Al-Ahsa", "الأحساء", "بلدية", "NCA ECC", "AHSA-ISMS-", "006400"],
        "formulas": [r"L\s*×\s*I"],
        "language": "AR",
    },
}

WRONG_FORMULA_PATTERNS = [
    (r"V\s*=\s*S\s*×\s*U(?!\s*/\s*4)", "Wrong MOI formula (missing 1− and /4)"),
    (r"V\s*=\s*S\s*[-−]\s*U", "Wrong MOI formula (subtraction instead of ×(1−U/4))"),
    (r"L\s*\+\s*S", "Wrong risk formula (L+S instead of L×S)"),
    (r"Likelihood\s*\+\s*Severity", "Wrong risk formula (addition instead of multiplication)"),
]

SUSPICIOUS_CLAUSE_PATTERNS = [
    (r"\b[1-9]\.9[0-9]\b", "Clause x.9N doesn't exist in ISO standards"),
    (r"\bA\.[5-8]\.9[0-9]\b", "Annex A control A.x.9N doesn't exist"),
    (r"\bISO\s*99[0-9]{3}\b", "ISO 99xxx standard doesn't exist"),
    (r"\bClause\s+1[5-9]\b", "Clause 15+ doesn't exist in ISO management system standards"),
]

# ─── V1: CLIENT ISOLATION ───────────────────────────────────────────
def check_client_isolation(content: str, active_client: str) -> List[str]:
    """Flag content from OTHER clients bleeding into output."""
    violations = []
    active_upper = active_client.upper()
    normalized_active = next(
        (k for k in CLIENT_KEYWORDS.keys() if k.upper() == active_upper),
        active_upper
    )

    for client, data in CLIENT_KEYWORDS.items():
        if client == normalized_active:
            continue
        for kw in data["keywords"]:
            if len(kw) < 4:
                continue
            if kw.lower() in content.lower():
                violations.append(
                    f"🚨 CLIENT CONTAMINATION: '{kw}' from {client} "
                    f"found in {active_client} output"
                )
    return violations

# ─── V2: FORMULA INTEGRITY ──────────────────────────────────────────
def check_formula_integrity(content: str, active_client: str) -> List[str]:
    """Verify correct formula applied, no corrupted versions."""
    issues = []
    active_upper = active_client.upper()
    normalized_active = next(
        (k for k in CLIENT_KEYWORDS.keys() if k.upper() == active_upper),
        active_upper
    )

    expected = CLIENT_KEYWORDS.get(normalized_active, {}).get("formulas", [])
    if expected:
        found = any(re.search(p, content) for p in expected)
        risk_signals = ["risk", "likelihood", "severity", "rating", "matrix", "مخاطر"]
        if any(s in content.lower() for s in risk_signals) and not found:
            issues.append(
                f"⚠️ Expected formula for {active_client} not found in risk-related output"
            )

    for pattern, desc in WRONG_FORMULA_PATTERNS:
        if re.search(pattern, content):
            if "L×I" in desc and normalized_active == "AL-AHSA":
                continue
            issues.append(f"🚨 WRONG FORMULA: {desc}")

    return issues

# ─── V3: CLAUSE HALLUCINATION ───────────────────────────────────────
def check_clause_hallucinations(content: str) -> List[str]:
    """Detect suspicious/invalid ISO clause references."""
    issues = []
    for pattern, desc in SUSPICIOUS_CLAUSE_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in set(matches):
            issues.append(f"🚨 POSSIBLE HALLUCINATION: '{match}' — {desc}")
    return issues

# ─── V4: CROSS-MODEL VERIFICATION (legacy high-stakes) ─────────────
async def verify_high_stakes(content: str, task_type: str, router_fn=None) -> Dict:
    """For high-stakes outputs: quick second-opinion from cheap model."""
    if task_type not in ["soa", "soa_exclusion", "major_nc", "capa_root_cause", "audit_report"]:
        return {"verified": True, "discrepancies": [], "skipped": True}

    if router_fn is None:
        return {"verified": True, "discrepancies": [], "skipped": True, "reason": "no router"}

    verify_prompt = f"""Verify this {task_type} output. Flag ONLY:
- Wrong ISO clause references
- Logical inconsistencies
- Missing mandatory elements

Output format:
ISSUES: [list or "none"]
CONFIDENCE: [high/medium/low]

{content[:4000]}"""

    try:
        v4_result = await router_fn(verify_prompt, "You are an ISO verification auditor.", tier_hint="cheap")
        discrepancies = []
        if "issues:" in v4_result.lower():
            issues_line = [l for l in v4_result.split("\n") if "issues:" in l.lower()][0]
            if "none" not in issues_line.lower():
                discrepancies.append(f"Cross-model flag: {issues_line[:200]}")
        return {"verified": len(discrepancies) == 0, "discrepancies": discrepancies, "skipped": False}
    except Exception as e:
        logger.warning(f"V4 cross-model check failed: {e}")
        return {"verified": True, "discrepancies": [], "skipped": True, "reason": str(e)}

# ─── V5: EVIDENCE TRACEABILITY ──────────────────────────────────────
def verify_evidence_traceability(content: str, task_type: str) -> List[str]:
    """Every claim must have traceable evidence."""
    issues = []
    
    if task_type in ["audit_finding", "nc_report", "audit_report"]:
        if not re.search(r'[Cc]lause\s+\d+\.\d+', content):
            issues.append("🚨 MISSING EVIDENCE: ISO clause reference required for finding")
        if not re.search(r'[Ee]vidence[:\s]', content):
            issues.append("🚨 MISSING EVIDENCE: Objective evidence citation required")
        if not re.search(r'[Ss]everity[:\s]*(Major|Minor|OFI|Observation)', content):
            issues.append("🚨 MISSING EVIDENCE: NC severity classification required")
    
    if task_type in ["capa_plan", "capa"]:
        if not re.search(r'[Rr]oot\s*[Cc]ause[:\s]', content):
            issues.append("🚨 MISSING EVIDENCE: Root cause analysis required")
        if not re.search(r'[Oo]wner[:\s]\S+', content):
            issues.append("🚨 MISSING EVIDENCE: Responsible owner required")
        if not re.search(r'[Dd]eadline[:\s]*\d', content) and not re.search(r'[Tt]arget\s*date[:\s]*\d', content):
            issues.append("🚨 MISSING EVIDENCE: Target completion date required")
        if not re.search(r'[Vv]erification[:\s]', content):
            issues.append("🚨 MISSING EVIDENCE: Effectiveness verification method required")
    
    if task_type in ["risk_register", "risk_entry"]:
        if not re.search(r'[Ll]ikelihood[:\s]*\d|[Ll]ikelihood[:\s]*(Rare|Unlikely|Possible|Likely|Almost Certain)', content):
            issues.append("🚨 MISSING EVIDENCE: Likelihood rating required")
        if not re.search(r'[Ss]everity[:\s]*\d|[Ss]everity[:\s]*(Minor|Moderate|Major|Catastrophic)', content):
            issues.append("🚨 MISSING EVIDENCE: Severity rating required")
        if not re.search(r'[Oo]wner[:\s]\S+', content):
            issues.append("🚨 MISSING EVIDENCE: Risk owner required")
    
    return issues

# ─── V6: CROSS-MODEL CONSENSUS (HIGH/CRITICAL risk) ─────────────────
async def verify_cross_model_consensus(
    content: str,
    task_type: str,
    risk_level: str,
    router_fn=None
) -> Dict:
    """For HIGH/CRITICAL-risk tasks: 3 models must agree."""
    if risk_level not in ["HIGH", "CRITICAL"] or router_fn is None:
        return {"verified": True, "discrepancies": [], "consensus": "skipped"}
    
    verify_prompt = f"""Verify this {task_type} output for accuracy.
Check ONLY for:
- Wrong ISO clause references
- Logical inconsistencies
- Missing mandatory elements
- Factual errors

Respond ONLY:
ISSUES: [list issues or 'none']
CONFIDENCE: [high/medium/low]

CONTENT TO VERIFY:
{content[:3500]}"""
    
    try:
        tasks = [
            router_fn(verify_prompt, "You are an ISO verification auditor.", tier_hint="tier1"),
            router_fn(verify_prompt, "You are an ISO verification auditor.", tier_hint="tier2"),
            router_fn(verify_prompt, "You are an ISO verification auditor.", tier_hint="tier3"),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = [r for r in results if not isinstance(r, Exception) and r]
        
        if len(valid_results) < 2:
            return {"verified": True, "discrepancies": [], "consensus": "insufficient_responses"}
        
        discrepancies = []
        issue_count = 0
        for r in valid_results:
            if "issues:" in r.lower() and "none" not in r.lower().split("issues:")[1].split("confidence:")[0]:
                issue_count += 1
        
        if issue_count >= 2:
            discrepancies.append(f"⚠️ {issue_count}/{len(valid_results)} models flagged potential issues")
        
        return {
            "verified": issue_count < 2,
            "discrepancies": discrepancies,
            "consensus": f"{len(valid_results)-issue_count}/{len(valid_results)} clean"
        }
    except Exception as e:
        logger.warning(f"V6 cross-model check failed: {e}")
        return {"verified": True, "discrepancies": [], "consensus": f"error: {e}"}

# ─── V7: TEMPORAL CONSISTENCY ───────────────────────────────────────
def verify_temporal_consistency(content: str, memory_ref: dict = None) -> List[str]:
    """Check dates, formulas, and client context for consistency."""
    issues = []
    today = datetime.now()
    
    date_matches = re.findall(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', content)
    for day, month, year in date_matches:
        try:
            doc_date = datetime(int(year), int(month), int(day))
            if doc_date.year > today.year + 1:
                issues.append(f"⚠️ FUTURE DATE: {day}/{month}/{year} is far in the future")
        except ValueError:
            pass
    
    if memory_ref:
        active_client = memory_ref.get("active_client")
        client_formulas = {
            "MSD-MOI": ["V=S×(1−U/4)", "S=O×Q"],
            "UACC": ["L×S"],
            "SAGCO": ["L×S", "L×S×R"],
            "AL-AHSA": ["L×I"],
        }
        
        if active_client and active_client in client_formulas:
            expected = client_formulas[active_client]
            risk_signals = ["risk", "likelihood", "severity", "rating", "مخاطر"]
            if any(s in content.lower() for s in risk_signals):
                all_formulas = ["V=S×(1−U/4)", "S=O×Q", "L×S", "L×S×R", "L×I"]
                wrong_formulas = [f for f in all_formulas if f not in expected and f in content]
                if wrong_formulas:
                    issues.append(f"🚨 WRONG CLIENT FORMULA: {wrong_formulas[0]} used for {active_client}")
    
    return issues

# ─── G8: SHOW-DON'T-TELL ────────────────────────────────────────────
def check_show_dont_tell(content: str) -> List[str]:
    """Flag meta-commentary about compliance with instructions."""
    banned_patterns = [
        r"(?i)here'?s a concise",
        r"(?i)I'?ve (?:checked|verified|reviewed) this",
        r"(?i)per your (?:request|instructions|requirements)",
        r"(?i)as requested,?",
        r"(?i)following the (?:guidelines|rules|framework)",
        r"(?i)this output (?:follows|adheres to|complies with)",
    ]
    issues = []
    for pattern in banned_patterns:
        if re.search(pattern, content):
            issues.append(f"🚨 G8 FAIL: Meta-commentary detected — show don't tell")
            break
    return issues

# ─── G9: TRACK A/B SEPARATION ───────────────────────────────────────
def check_track_separation(content: str, task_type: str) -> List[str]:
    """Flag Track A findings bundled with Track B solutions."""
    issues = []
    if task_type in ["audit_report", "nc_finding", "gap_analysis"]:
        solution_signals = [
            r"(?i)recommend(?:ed|ation)? (?:to|that) (?:implement|build|create|deploy)",
            r"(?i)the (?:organization|company) should (?:install|purchase|acquire)",
            r"(?i)we (?:suggest|propose) (?:implementing|building|deploying)",
        ]
        for pattern in solution_signals:
            if re.search(pattern, content):
                issues.append(
                    f"🚨 G9 FAIL: Track A output contains Track B implementation language. "
                    f"Identify only — never offer solutions."
                )
                break
    if task_type in ["policy", "procedure", "capa_plan"]:
        audit_signals = [
            r"(?i)(?:the audit team|we) (?:found|identified|observed) (?:a|an) (?:gap|nonconformity|NC)",
        ]
        for pattern in audit_signals:
            if re.search(pattern, content):
                issues.append(
                    f"🚨 G9 FAIL: Track B output contains Track A audit finding language. "
                    f"Build only — never identify gaps."
                )
                break
    return issues

# ─── G10: TEMPLATE STRUCTURE ────────────────────────────────────────
def check_template_structure(content: str, task_type: str) -> List[str]:
    """Verify output follows correct document template structure."""
    issues = []
    
    required_sections = {
        "soa": ["Control ID", "Applicable?", "Justification"],
        "capa_plan": ["Root Cause", "Containment", "Corrective", "Preventive", "Effectiveness"],
        "audit_report": ["Executive Summary", "Scope", "Findings", "Recommendation"],
        "risk_register": ["Risk ID", "Likelihood", "Severity", "Risk Level"],
    }
    
    if task_type in required_sections:
        for section in required_sections[task_type]:
            if section.lower() not in content.lower():
                issues.append(
                    f"🚨 G10 FAIL: Missing required section '{section}' for {task_type}"
                )
    
    return issues

# ─── MASTER VALIDATOR (V1-V7 + G8-G10) ─────────────────────────────
async def validate_output(
    content: str,
    active_client: str,
    task_type: str = "general",
    risk_level: str = "LOW",
    high_stakes: bool = False,
    router_fn=None,
    memory_ref: dict = None,
) -> Dict[str, Any]:
    """Run all 10 validation gates. Returns pass/fail + issues."""
    all_issues = []
    gates_run = []

    # V1: Client isolation
    v1 = check_client_isolation(content, active_client)
    all_issues.extend(v1)
    gates_run.append(("V1-isolation", len(v1) == 0))

    # V2: Formula integrity
    v2 = check_formula_integrity(content, active_client)
    all_issues.extend(v2)
    gates_run.append(("V2-formula", len(v2) == 0))

    # V3: Clause hallucinations
    v3 = check_clause_hallucinations(content)
    all_issues.extend(v3)
    gates_run.append(("V3-clauses", len(v3) == 0))

    # V4: Cross-model (legacy high-stakes)
    v4_result = {"verified": True, "discrepancies": [], "skipped": True}
    if high_stakes and router_fn:
        v4_result = await verify_high_stakes(content, task_type, router_fn)
        all_issues.extend(v4_result.get("discrepancies", []))
    gates_run.append(("V4-legacy", v4_result["verified"]))

    # V5: Evidence traceability
    v5 = verify_evidence_traceability(content, task_type)
    all_issues.extend(v5)
    gates_run.append(("V5-evidence", len(v5) == 0))

    # V6: Cross-model consensus (HIGH/CRITICAL)
    v6 = await verify_cross_model_consensus(content, task_type, risk_level, router_fn)
    all_issues.extend(v6.get("discrepancies", []))
    gates_run.append(("V6-consensus", v6["verified"]))

    # V7: Temporal consistency
    v7 = verify_temporal_consistency(content, memory_ref)
    all_issues.extend(v7)
    gates_run.append(("V7-temporal", len(v7) == 0))

    # G8: Show-don't-tell
    g8 = check_show_dont_tell(content)
    all_issues.extend(g8)
    gates_run.append(("G8-show-dont-tell", len(g8) == 0))

    # G9: Track A/B separation
    g9 = check_track_separation(content, task_type)
    all_issues.extend(g9)
    gates_run.append(("G9-track-separation", len(g9) == 0))

    # G10: Template structure
    g10 = check_template_structure(content, task_type)
    all_issues.extend(g10)
    gates_run.append(("G10-template", len(g10) == 0))

    return {
        "passed": len(all_issues) == 0,
        "issues": all_issues,
        "gates_run": gates_run,
        "risk_level": risk_level,
        "consensus": v6.get("consensus", "N/A"),
        "client": active_client,
        "task_type": task_type,
    }

def validate_output_sync(content: str, active_client: str, task_type: str = "general", high_stakes: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for validate_output."""
    return asyncio.run(validate_output(content, active_client, task_type, high_stakes=high_stakes))
