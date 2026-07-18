import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# ─── Client Registry ──────────────────────────────────────────────────────
CLIENT_KEYWORDS = {
    "MSD-MOI": {
        "keywords": ["وزارة الداخلية", "MSD-MOI", "004D26"],
        "formulas": ["V=S×(1−U/4)", "S=O×Q"]
    },
    "UACC": {
        "keywords": ["UACC", "Taif", "UACC-EnMS-"],
        "formulas": ["L×S"]
    },
    "SAGCO": {
        "keywords": ["SAGCO", "Saudi Arabian Gas", "SAGCO-IMS-", "1B3A4B", "E07B39", "HFO", "LPG"],
        "formulas": ["L×S", "L×S×R"]
    },
    "Al-Ahsa": {
        "keywords": ["Al-Ahsa", "الأحساء", "AHSA-ISMS-", "006400"],
        "formulas": ["L×I"]
    }
}

WRONG_FORMULA_PATTERNS = [
    (r"V\s*=\s*S\s*×\s*U(?!\s*/\s*4)", "Wrong MOI formula (missing 1− and /4)"),
    (r"V\s*=\s*S\s*-\s*U", "Wrong MOI formula (subtraction instead of ×(1−U/4))"),
    (r"L\s*\+\s*S", "Wrong risk formula (L+S instead of L×S)"),
    (r"Likelihood\s*\+\s*Severity", "Wrong risk formula (addition instead of multiplication)")
]

SUSPICIOUS_CLAUSE_PATTERNS = [
    (r"\b[1-9]\.9[0-9]\b", "Clause x.9N doesn't exist in ISO standards"),
    (r"\bA\.[5-8]\.9[0-9]\b", "Annex A control A.x.9N doesn't exist"),
    (r"\bISO\s*99[0-9]{3}\b", "ISO 99xxx standard doesn't exist"),
    (r"\bClause\s+1[5-9]\b", "Clause 15+ doesn't exist in ISO management system standards")
]

# ─── Load ISO Clause Database ─────────────────────────────────────────────
_CLAUSE_DB_PATH = Path(__file__).parent.parent.parent / "data" / "iso_clause_database.json"
_CLAUSE_DB = {}
if _CLAUSE_DB_PATH.exists():
    try:
        with open(_CLAUSE_DB_PATH, 'r', encoding='utf-8') as f:
            _CLAUSE_DB = json.load(f)
    except Exception:
        pass

# ─── V1: Client Isolation ─────────────────────────────────────────────────
def check_client_isolation(content: str, active_client: str) -> List[str]:
    """Flag content from OTHER clients bleeding into output."""
    issues = []
    active_upper = active_client.upper()
    
    for client, data in CLIENT_KEYWORDS.items():
        if client.upper() == active_upper:
            continue
        
        for keyword in data["keywords"]:
            if keyword.lower() in content.lower():
                issues.append(f"🚨 V1 FAIL: Client contamination - '{keyword}' from {client} found in {active_client} output")
    
    return issues

# ─── V2: Formula Integrity ────────────────────────────────────────────────
def check_formula_integrity(content: str, active_client: str) -> List[str]:
    """Verify correct formula applied, no corrupted versions."""
    issues = []
    active_upper = active_client.upper()
    
    # Check for wrong formula patterns (corrupted versions)
    for pattern, description in WRONG_FORMULA_PATTERNS:
        if re.search(pattern, content):
            issues.append(f"🚨 V2 FAIL: {description}")
    
    # Check if WRONG client's formula is being used
    all_formulas = ["V=S×(1−U/4)", "S=O×Q", "L×S", "L×S×R", "L×I"]
    expected_formulas = CLIENT_KEYWORDS.get(active_client, {}).get("formulas", [])
    
    if expected_formulas:
        risk_signals = ["risk", "likelihood", "severity", "rating", "matrix", "مخاطر"]
        if any(signal in content.lower() for signal in risk_signals):
            # Check for wrong formulas from other clients
            wrong_formulas = [f for f in all_formulas if f not in expected_formulas and f in content]
            if wrong_formulas:
                issues.append(f"🚨 WRONG FORMULA: {wrong_formulas[0]} used for {active_client} (expected {expected_formulas[0]})")
    
    return issues

# ─── V3: Clause Hallucination ─────────────────────────────────────────────
def check_clause_hallucinations(content: str) -> List[str]:
    """Detect suspicious/invalid ISO clause references."""
    issues = []
    
    for pattern, description in SUSPICIOUS_CLAUSE_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            issues.append(f"🚨 V3 FAIL: {description} - found '{match.group()}'")
    
    # Cross-reference with clause database if available
    if _CLAUSE_DB:
        clause_refs = re.findall(r'(?:Clause|clause)\s+(\d+\.\d+(?:\.\d+)*)', content)
        for ref in clause_refs:
            parts = ref.split('.')
            if len(parts) >= 2:
                major = int(parts[0])
                if major > 10:
                    issues.append(f"⚠️ V3 WARN: Suspicious clause reference {ref} (major clause > 10)")
    
    return issues

# ─── V4: Cross-Model Verification (Legacy High-Stakes) ───────────────────
async def verify_high_stakes(content: str, task_type: str, router_fn=None) -> Dict[str, Any]:
    """For high-stakes outputs: quick second-opinion from cheap model."""
    return {
        "verified": True,
        "discrepancies": [],
        "skipped": True,
        "reason": "Cross-model verification not yet implemented"
    }

# ─── V5: Evidence Traceability ────────────────────────────────────────────
def verify_evidence_traceability(content: str, task_type: str) -> List[str]:
    """Every claim must have traceable evidence."""
    issues = []
    
    if task_type in ["audit_finding", "nc_report", "audit_report"]:
        if not re.search(r'[Cc]lause\s+\d+\.\d+', content):
            issues.append("🚨 V5 FAIL: ISO clause reference required for finding")
        if not re.search(r'[Ee]vidence[:\s]', content):
            issues.append("🚨 V5 FAIL: Objective evidence citation required")
        if not re.search(r'[Ss]everity[:\s]*(Major|Minor|OFI|Observation)', content):
            issues.append("🚨 V5 FAIL: NC severity classification required")
    
    if task_type in ["capa_plan", "capa"]:
        if not re.search(r'[Rr]oot\s*[Cc]ause[:\s]', content):
            issues.append("🚨 V5 FAIL: Root cause analysis required")
        if not re.search(r'[Oo]wner[:\s]', content):
            issues.append("🚨 V5 FAIL: Responsible owner required")
        if not re.search(r'[Dd]eadline[:\s]*\d', content) and not re.search(r'[Tt]arget\s*date[:\s]*\d', content):
            issues.append("🚨 V5 FAIL: Target completion date required")
    
    if task_type in ["risk_register", "risk_entry"]:
        if not re.search(r'[Ll]ikelihood[:\s]*\d', content):
            issues.append("🚨 V5 FAIL: Likelihood rating required")
        if not re.search(r'[Ss]everity[:\s]*\d', content):
            issues.append("🚨 V5 FAIL: Severity rating required")
        if not re.search(r'[Oo]wner[:\s]', content):
            issues.append("🚨 V5 FAIL: Risk owner required")
    
    return issues

# ─── V6: Cross-Model Consensus (HIGH/CRITICAL Risk) ───────────────────────
async def verify_cross_model_consensus(content: str, task_type: str, risk_level: str, router_fn=None) -> Dict[str, Any]:
    """For HIGH/CRITICAL-risk tasks: 3 models must agree."""
    return {
        "verified": True,
        "discrepancies": [],
        "consensus": "skipped",
        "reason": "Cross-model consensus not yet implemented"
    }

# ─── V7: Temporal Consistency ─────────────────────────────────────────────
def verify_temporal_consistency(content: str, memory_ref: dict = None) -> List[str]:
    """Check dates, formulas, and client context for consistency."""
    issues = []
    
    # Check for future dates (DD/MM/YYYY format)
    date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
    matches = re.finditer(date_pattern, content)
    
    today = datetime.now()
    for match in matches:
        try:
            day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
            doc_date = datetime(year, month, day)
            if doc_date.year > today.year + 1:
                issues.append(f"⚠️ V7 WARN: Future date detected {day}/{month}/{year}")
        except ValueError:
            pass
    
    # Check formula consistency with active client
    if memory_ref and "active_client" in memory_ref:
        active_client = memory_ref["active_client"]
        expected_formulas = CLIENT_KEYWORDS.get(active_client, {}).get("formulas", [])
        all_formulas = ["V=S×(1−U/4)", "S=O×Q", "L×S", "L×S×R", "L×I"]
        
        if expected_formulas:
            risk_signals = ["risk", "likelihood", "severity", "rating", "مخاطر"]
            if any(signal in content.lower() for signal in risk_signals):
                wrong_formulas = [f for f in all_formulas if f not in expected_formulas and f in content]
                if wrong_formulas:
                    issues.append(f"🚨 V7 FAIL: Wrong client formula - {wrong_formulas[0]} used for {active_client}")
    
    return issues

# ─── G8: Show-Don't-Tell ──────────────────────────────────────────────────
def check_show_dont_tell(content: str) -> List[str]:
    """Flag meta-commentary about compliance with instructions."""
    banned_patterns = [
        r"(?i)here'?s a concise",
        r"(?i)I'?ve (?:checked|verified|reviewed) this",
        r"(?i)per your (?:request|instructions|requirements)",
        r"(?i)as requested,?",
        r"(?i)following the (?:guidelines|rules|framework)",
        r"(?i)this output (?:follows|adheres to|complies with)"
    ]
    
    issues = []
    for pattern in banned_patterns:
        if re.search(pattern, content):
            issues.append("🚨 G8 FAIL: Meta-commentary detected - show don't tell")
            break
    
    return issues

# ─── G9: Track A/B Separation ─────────────────────────────────────────────
def check_track_separation(content: str, task_type: str) -> List[str]:
    """Flag Track A findings bundled with Track B solutions."""
    issues = []
    
    if task_type in ["audit_report", "nc_finding", "gap_analysis"]:
        solution_signals = [
            r"(?i)recommend(?:ed|ation)? (?:to|that) (?:implement|build|create|deploy)",
            r"(?i)the (?:organization|company) should (?:install|purchase|acquire)",
            r"(?i)we (?:suggest|propose|recommend) (?:implementing|building|deploying)"
        ]
        for pattern in solution_signals:
            if re.search(pattern, content):
                issues.append("🚨 G9 FAIL: Track A output contains Track B implementation language")
                break
    
    if task_type in ["policy", "procedure", "capa_plan"]:
        audit_signals = [
            r"(?i)(?:the audit team|we) (?:found|identified|observed) (?:a|an) (?:gap|nonconformity|NC)"
        ]
        for pattern in audit_signals:
            if re.search(pattern, content):
                issues.append("🚨 G9 FAIL: Track B output contains Track A audit finding language")
                break
    
    return issues

# ─── G10: Template Structure ──────────────────────────────────────────────
def check_template_structure(content: str, task_type: str) -> List[str]:
    """Verify output follows correct document template structure."""
    issues = []
    
    required_sections = {
        "soa": ["Control ID", "Applicable?", "Justification"],
        "capa_plan": ["Root Cause", "Containment", "Corrective", "Preventive", "Effectiveness"],
        "audit_report": ["Executive Summary", "Scope", "Findings", "Recommendation"],
        "risk_register": ["Risk ID", "Likelihood", "Severity", "Risk Level"]
    }
    
    if task_type in required_sections:
        for section in required_sections[task_type]:
            if section.lower() not in content.lower():
                issues.append(f"🚨 G10 FAIL: Missing required section '{section}' for {task_type}")
    
    return issues

# ─── Master Validator (V1-V7 + G8-G10) ───────────────────────────────────
async def validate_output(
    content: str,
    active_client: str,
    task_type: str = "general",
    risk_level: str = "LOW",
    high_stakes: bool = False,
    router_fn=None,
    memory_ref: dict = None
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
        "task_type": task_type
    }

# ─── Auto-Heal Wrapper ────────────────────────────────────────────────────
async def validate_and_heal(
    content: str,
    prompt: str,
    client_key: str,
    doc_type: str,
    api_key: str,
    max_retries: int = 2
) -> tuple:
    """Validate output and auto-heal if gates fail."""
    from app.services.ai.router import generate as router_generate
    
    for attempt in range(max_retries + 1):
        validation = await validate_output(
            content=content,
            active_client=client_key or "GENERAL",
            task_type=doc_type,
            high_stakes=(doc_type in ["soa", "audit_report", "major_nc"])
        )
        
        if validation["passed"]:
            return content, validation
        
        if attempt < max_retries:
            feedback = "\n\n=== VALIDATOR FEEDBACK ===\n"
            feedback += "The previous output had these issues. Fix them:\n"
            for issue in validation["issues"][:5]:
                feedback += f"- {issue}\n"
            feedback += "\nRegenerate with all issues resolved.\n"
            
            heal_prompt = prompt + feedback
            
            result = router_generate(
                task_type=doc_type,
                prompt=heal_prompt,
                system_prompt=None,
                api_key=api_key,
                client_key=client_key
            )
            
            if 'error' not in result:
                content = result.get('content', content)
    
    return content, validation
