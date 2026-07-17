"""
OWL ComplianceHub Validator — 10-Gate Anti-Hallucination Protocol
July 2026 · Agent 7 (Platform Engineer)
"""
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# ─── CLIENT REGISTRY ──────────────────────────────────────────────────
CLIENT_KEYWORDS = {
    "MSD-MOI": {"keywords": ["MOI", "وزارة الداخلية", "GRC", "004D26", "C8A96E", "1A3A5C", "MSD-MOI-GRC-"], "formulas": [r"V\s*=\s*S\s*×\s*\(1\s*[−-]\s*U\s*/\s*4\)"]},
    "UACC": {"keywords": ["UACC", "Taif", "EnMS", "EnPI", "SEU", "VFD", "UACC-EnMS-"], "formulas": [r"L\s*×\s*S"]},
    "SAGCO": {"keywords": ["SAGCO", "SHC", "HFO", "LPG", "GHG", "HIRA", "SAGCO-IMS-", "1B3A4B", "E07B39"], "formulas": [r"L\s*×\s*S", r"L\s*×\s*S\s*×\s*R"]},
    "AL-AHSA": {"keywords": ["Al-Ahsa", "الأحساء", "بلدية", "NCA ECC", "AHSA-ISMS-", "006400"], "formulas": [r"L\s*×\s*I"]},
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
]

# ─── V1: CLIENT ISOLATION ─────────────────────────────────────────────
def check_client_isolation(content: str, active_client: str) -> List[str]:
    violations = []
    normalized_active = next((k for k in CLIENT_KEYWORDS.keys() if k.upper() == active_client.upper()), active_client.upper())
    for client, data in CLIENT_KEYWORDS.items():
        if client == normalized_active: continue
        for kw in data["keywords"]:
            if len(kw) >= 4 and kw.lower() in content.lower():
                violations.append(f"🚨 CLIENT CONTAMINATION: '{kw}' from {client} found in {active_client} output")
    return violations

# ─── V2: FORMULA INTEGRITY ────────────────────────────────────────────
def check_formula_integrity(content: str, active_client: str) -> List[str]:
    issues = []
    normalized_active = next((k for k in CLIENT_KEYWORDS.keys() if k.upper() == active_client.upper()), active_client.upper())
    expected = CLIENT_KEYWORDS.get(normalized_active, {}).get("formulas", [])
    
    if expected and not any(re.search(p, content) for p in expected):
        risk_signals = ["risk", "likelihood", "severity", "rating", "مخاطر"]
        if any(s in content.lower() for s in risk_signals):
            issues.append(f"⚠️ Expected formula for {active_client} not found in risk-related output")
            
    for pattern, desc in WRONG_FORMULA_PATTERNS:
        if re.search(pattern, content):
            if "L×I" in desc and normalized_active == "AL-AHSA": continue
            issues.append(f"🚨 WRONG FORMULA: {desc}")
    return issues

# ─── V3: CLAUSE HALLUCINATION ─────────────────────────────────────────
def check_clause_hallucinations(content: str) -> List[str]:
    issues = []
    for pattern, desc in SUSPICIOUS_CLAUSE_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in set(matches):
            issues.append(f"🚨 POSSIBLE HALLUCINATION: '{match}' — {desc}")
    return issues

# ─── V5: EVIDENCE TRACEABILITY ────────────────────────────────────────
def verify_evidence_traceability(content: str, task_type: str) -> List[str]:
    issues = []
    if task_type in ["audit_finding", "nc_report", "audit_report"]:
        if not re.search(r'[Cc]lause\s+\d+\.\d+', content):
            issues.append("🚨 MISSING EVIDENCE: ISO clause reference required for finding")
        if not re.search(r'[Ee]vidence[:\s]', content):
            issues.append("🚨 MISSING EVIDENCE: Objective evidence citation required")
    if task_type in ["capa_plan", "capa"]:
        if not re.search(r'[Rr]oot\s*[Cc]ause[:\s]', content):
            issues.append("🚨 MISSING EVIDENCE: Root cause analysis required")
        if not re.search(r'[Oo]wner[:\s]\S+', content):
            issues.append("🚨 MISSING EVIDENCE: Responsible owner required")
    return issues

# ─── V7: TEMPORAL CONSISTENCY ─────────────────────────────────────────
def verify_temporal_consistency(content: str, memory_ref: dict = None) -> List[str]:
    issues = []
    today = datetime.now()
    date_matches = re.findall(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', content)
    for day, month, year in date_matches:
        try:
            doc_date = datetime(int(year), int(month), int(day))
            if doc_date.year > today.year + 1:
                issues.append(f"⚠️ FUTURE DATE: {day}/{month}/{year} is far in the future")
        except ValueError: pass
    return issues

# ─── G8: SHOW-DON'T-TELL ──────────────────────────────────────────────
def check_show_dont_tell(content: str) -> List[str]:
    banned_patterns = [
        r"(?i)here'?s a concise", r"(?i)I'?ve (?:checked|verified|reviewed) this",
        r"(?i)per your (?:request|instructions)", r"(?i)this output (?:follows|adheres to)",
    ]
    for pattern in banned_patterns:
        if re.search(pattern, content):
            return ["🚨 G8 FAIL: Meta-commentary detected — show don't tell"]
    return []

# ─── G9: TRACK SEPARATION ─────────────────────────────────────────────
def check_track_separation(content: str, task_type: str) -> List[str]:
    issues = []
    if task_type in ["audit_report", "nc_finding", "gap_analysis"]:
        if re.search(r"(?i)recommend(?:ed|ation)? (?:to|that) (?:implement|build)", content):
            issues.append("🚨 G9 FAIL: Track A output contains Track B implementation language.")
    return issues

# ─── G10: TEMPLATE STRUCTURE ──────────────────────────────────────────
def check_template_structure(content: str, task_type: str) -> List[str]:
    issues = []
    required = {
        "soa": ["Control ID", "Applicable?", "Justification"],
        "capa_plan": ["Root Cause", "Containment", "Corrective", "Preventive"],
        "audit_report": ["Executive Summary", "Scope", "Findings"],
    }
    if task_type in required:
        for section in required[task_type]:
            if section.lower() not in content.lower():
                issues.append(f"🚨 G10 FAIL: Missing required section '{section}'")
    return issues

# ─── MASTER VALIDATOR ─────────────────────────────────────────────────
async def validate_output(
    content: str,
    active_client: str,
    task_type: str = "general",
    risk_level: str = "LOW",
    high_stakes: bool = False,
    router_fn=None,
    memory_ref: dict = None,
) -> Dict[str, Any]:
    all_issues = []
    gates_run = []
    
    # Backend Gates (V1-V7)
    v1 = check_client_isolation(content, active_client); all_issues.extend(v1); gates_run.append(("V1-isolation", len(v1)==0))
    v2 = check_formula_integrity(content, active_client); all_issues.extend(v2); gates_run.append(("V2-formula", len(v2)==0))
    v3 = check_clause_hallucinations(content); all_issues.extend(v3); gates_run.append(("V3-clauses", len(v3)==0))
    v5 = verify_evidence_traceability(content, task_type); all_issues.extend(v5); gates_run.append(("V5-evidence", len(v5)==0))
    v7 = verify_temporal_consistency(content, memory_ref); all_issues.extend(v7); gates_run.append(("V7-temporal", len(v7)==0))
    
    # Quality Gates (G8-G10)
    g8 = check_show_dont_tell(content); all_issues.extend(g8); gates_run.append(("G8-show-dont-tell", len(g8)==0))
    g9 = check_track_separation(content, task_type); all_issues.extend(g9); gates_run.append(("G9-track-separation", len(g9)==0))
    g10 = check_template_structure(content, task_type); all_issues.extend(g10); gates_run.append(("G10-template", len(g10)==0))
    
    return {
        "passed": len(all_issues) == 0,
        "issues": all_issues,
        "gates_run": gates_run,
        "client": active_client,
        "task_type": task_type,
    }
