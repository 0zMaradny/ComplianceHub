"""Enrich clause_data.py with audit_questions and evidence_to_check per sub-clause.

Usage: python scripts/enrich_clause_data.py
Reads clause_data.py, adds fields to every sub-clause/sub-section entry,
writes back the enriched file.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
HERE = Path(__file__).parent.parent
CLAUSE_DATA = HERE / "app" / "services" / "clause_data.py"

# ── Question/evidence templates keyed by keywords from clause titles ──────
QUESTION_TEMPLATES = {
    "context": [
        "How does the organization determine external and internal issues relevant to its purpose?",
        "How are interested parties identified and their requirements monitored?",
        "What process is used to review the scope of the management system?",
    ],
    "leadership": [
        "How does top management demonstrate leadership and commitment?",
        "How is the quality/environmental/OH&S policy communicated and maintained?",
        "How are roles, responsibilities, and authorities assigned and communicated?",
    ],
    "planning": [
        "How does the organization identify risks and opportunities?",
        "How are quality/environmental/OH&S objectives established and monitored?",
        "What process is in place for planning changes to the management system?",
    ],
    "support": [
        "How are resources needed for the management system determined and provided?",
        "How is competence of personnel ensured?",
        "How does the organization manage documented information?",
        "How is internal and external communication managed?",
    ],
    "operation": [
        "How are operational processes planned, implemented, and controlled?",
        "What criteria are in place for accepting products and services?",
        "How does the organization manage changes to operational processes?",
    ],
    "evaluation": [
        "How does the organization monitor, measure, analyze, and evaluate performance?",
        "How is the internal audit program planned and implemented?",
        "How does management review the management system?",
    ],
    "improvement": [
        "How does the organization identify and act on nonconformities?",
        "How is corrective action managed?",
        "How does the organization drive continual improvement?",
    ],
    "information security": [
        "How are information security policies established and reviewed?",
        "How is information security risk assessment conducted?",
        "How are information security controls selected and implemented?",
    ],
    "risk": [
        "How does the organization conduct risk assessment?",
        "How are risk treatment options evaluated and selected?",
        "How is the risk assessment process documented and maintained?",
    ],
    "policy": [
        "How is the policy documented, approved, and communicated?",
        "How is policy compliance monitored?",
        "How often is the policy reviewed for continuing suitability?",
    ],
    "internal audit": [
        "How is the internal audit program planned?",
        "How are auditors selected and their competence ensured?",
        "How are audit results reported and followed up?",
    ],
    "management review": [
        "How is the management review agenda determined?",
        "What inputs and outputs are part of the management review?",
        "How are management review action items tracked?",
    ],
    "document": [
        "How is document control managed?",
        "How are document changes approved and tracked?",
        "How is the retention of documented information ensured?",
    ],
    "competence": [
        "How is required competence determined for each role?",
        "How is competence evaluated and records maintained?",
        "What training or awareness programs are in place?",
    ],
    "awareness": [
        "How does the organization ensure awareness of the policy?",
        "How are employees made aware of their contribution to effectiveness?",
        "How is awareness of the implications of nonconformity ensured?",
    ],
    "communication": [
        "How is internal communication managed across levels?",
        "How is external communication regulated?",
        "How does the organization receive and respond to external communications?",
    ],
    "supplier": [
        "How are suppliers evaluated and selected?",
        "How is supplier performance monitored?",
        "How are outsourced processes controlled?",
    ],
    "design": [
        "How is the design and development process planned?",
        "How are design inputs, outputs, and reviews managed?",
        "How are design changes controlled and validated?",
    ],
    "customer": [
        "How are customer requirements determined and reviewed?",
        "How is customer communication managed?",
        "How does the organization handle customer complaints?",
    ],
    "product": [
        "How is product/service acceptance criteria defined?",
        "How is product traceability managed?",
        "How is product preservation handled during processing?",
    ],
    "emergency": [
        "How does the organization identify potential emergency situations?",
        "How are emergency response procedures tested and evaluated?",
        "How is emergency preparedness training conducted?",
    ],
    "monitoring": [
        "How are monitoring and measurement activities defined?",
        "What monitoring equipment is used and how is it calibrated?",
        "How are monitoring results analyzed and reported?",
    ],
    "nonconformity": [
        "How are nonconformities identified and documented?",
        "How does the organization determine the root cause of nonconformities?",
        "How is the effectiveness of corrective actions verified?",
    ],
    "corrective": [
        "How does the organization initiate corrective action?",
        "How is the effectiveness of corrective actions evaluated?",
        "How are corrective action records maintained?",
    ],
    "objective": [
        "How are objectives established at relevant functions and levels?",
        "How are objectives monitored and updated?",
        "How is progress toward objectives communicated?",
    ],
    "clause": [
        "What evidence demonstrates compliance with this clause?",
        "How does the organization address each requirement of this clause?",
        "How is conformance with this clause verified during audits?",
    ],
}

EVIDENCE_TEMPLATES = {
    "context": [
        "Review of strategic planning documentation including PESTLE/SWOT analysis",
        "Examination of interested party register with requirements traceability",
        "Review of scope statement and documented scope justification",
    ],
    "leadership": [
        "Interview with top management on leadership involvement",
        "Review of policy statements and communication records",
        "Review of organizational charts and responsibility matrices",
    ],
    "planning": [
        "Review of risk and opportunity register",
        "Examination of objectives and plans to achieve them",
        "Review of change management procedure and records",
    ],
    "support": [
        "Review of resource allocation documentation",
        "Examination of training records and competence matrices",
        "Review of documented information control procedure",
    ],
    "operation": [
        "Observation of operational processes in execution",
        "Review of operational planning and control documentation",
        "Examination of process performance records",
    ],
    "evaluation": [
        "Review of performance monitoring and measurement records",
        "Examination of internal audit program and reports",
        "Review of management meeting minutes and action logs",
    ],
    "improvement": [
        "Review of nonconformity logs and corrective action records",
        "Examination of continual improvement initiatives",
        "Review of preventive action documentation",
    ],
    "information security": [
        "Review of information security policy and procedures",
        "Examination of risk assessment and treatment documentation",
        "Review of access control and security incident records",
    ],
    "risk": [
        "Review of risk assessment methodology and criteria",
        "Examination of risk register and treatment plans",
        "Review of risk review and update records",
    ],
    "policy": [
        "Review of approved policy document with version history",
        "Examination of policy communication records",
        "Review of policy review meeting minutes",
    ],
    "internal audit": [
        "Review of internal audit schedule and program",
        "Examination of auditor qualification and selection records",
        "Review of audit reports and follow-up verification",
    ],
    "management review": [
        "Review of management review meeting minutes",
        "Examination of action item tracking records",
        "Review of management review input data and trend analysis",
    ],
    "document": [
        "Review of document control procedure",
        "Examination of document approval and change records",
        "Review of master document list and obsolete document handling",
    ],
    "competence": [
        "Review of job descriptions and competence requirements",
        "Examination of training records and effectiveness evaluation",
        "Review of certification and qualification records",
    ],
    "awareness": [
        "Interview with personnel on policy awareness",
        "Review of awareness training materials and attendance records",
        "Examination of communication campaign records",
    ],
    "communication": [
        "Review of communication procedure and matrix",
        "Examination of internal communication records and notice boards",
        "Review of external communication logs and responses",
    ],
    "supplier": [
        "Review of supplier evaluation and selection criteria",
        "Examination of approved supplier list",
        "Review of supplier performance monitoring records",
    ],
    "design": [
        "Review of design and development procedure",
        "Examination of design input/output/review/verification records",
        "Review of design change control and authorization records",
    ],
    "customer": [
        "Review of customer requirement review procedure",
        "Examination of customer communication records",
        "Review of customer complaint handling and resolution records",
    ],
    "product": [
        "Review of product acceptance criteria and inspection records",
        "Examination of traceability records",
        "Review of product preservation and handling procedures",
    ],
    "emergency": [
        "Review of emergency preparedness and response procedure",
        "Examination of emergency drill records and lessons learned",
        "Review of emergency equipment inspection and maintenance records",
    ],
    "monitoring": [
        "Review of monitoring and measurement equipment calibration records",
        "Examination of monitoring plans and reports",
        "Review of data analysis and performance evaluation records",
    ],
    "nonconformity": [
        "Review of nonconformity register and trend analysis",
        "Examination of nonconformity investigation and root cause records",
        "Review of re-verification of corrected items",
    ],
    "corrective": [
        "Review of corrective action procedure",
        "Examination of corrective action records and effectiveness verification",
        "Review of corrective action trend analysis",
    ],
    "objective": [
        "Review of objective documentation and performance indicators",
        "Examination of objective monitoring records",
        "Review of objective achievement status reports",
    ],
    "clause": [
        "Review of documented evidence of compliance with contractual requirements",
        "Examination of applicable regulatory permits and approvals",
    ],
}


def find_clause_category(title: str) -> str:
    """Return the best-matching template category for a clause title."""
    title_lower = title.lower()
    for cat in [
        "context", "leadership", "planning", "support", "operation",
        "evaluation", "improvement", "information security", "risk",
        "policy", "internal audit", "management review", "document",
        "competence", "awareness", "communication", "supplier", "design",
        "customer", "product", "emergency", "monitoring", "nonconformity",
        "corrective", "objective", "clause",
    ]:
        if cat in title_lower:
            return cat
    return "clause"


def make_questions(title: str, count: int = 2) -> list:
    cat = find_clause_category(title)
    templates = QUESTION_TEMPLATES.get(cat, QUESTION_TEMPLATES["clause"])
    return templates[:count]


def make_evidence(title: str, count: int = 2) -> list:
    cat = find_clause_category(title)
    templates = EVIDENCE_TEMPLATES.get(cat, EVIDENCE_TEMPLATES["clause"])
    return templates[:count]


def enrich_sub_clauses(sub_clauses: dict, _depth: int = 0) -> dict:
    """Recursively enrich a sub_clauses dict: convert string leaves to dicts, add new fields."""
    out = {}
    for key, value in sub_clauses.items():
        if isinstance(value, str):
            # Leaf node — convert string to dict with title + new fields
            title = value
            out[key] = {
                "title": title,
                "audit_questions": make_questions(title),
                "evidence_to_check": make_evidence(title),
            }
        elif isinstance(value, dict):
            # Branch node — may already have 'title' + optionally 'sub_clauses'
            entry = dict(value)  # shallow copy
            if "sub_clauses" in value:
                entry["sub_clauses"] = enrich_sub_clauses(value["sub_clauses"], _depth + 1)
            else:
                # It's a leaf presented as a single-key dict — treat as leaf
                pass
            # Add new fields at this level if not present
            title = entry.get("title", key)
            entry.setdefault("audit_questions", make_questions(title))
            entry.setdefault("evidence_to_check", make_evidence(title))
            out[key] = entry
        else:
            out[key] = value
    return out


def pprint_value(val, indent: int = 0) -> str:
    """Pretty-print a Python value as code."""
    sp = "    " * indent
    sp1 = "    " * (indent + 1)
    sp2 = "    " * (indent + 2)
    if val is None:
        return "None"
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, str):
        # Escape quotes
        escaped = val.replace("'", "\\'").replace("\n", "\\n")
        return f"'{escaped}'"
    if isinstance(val, list):
        if not val:
            return "[]"
        items = ",\n".join(f"{sp1}{pprint_value(v, indent + 1)}" for v in val)
        return f"[\n{items},\n{sp}]"
    if isinstance(val, dict):
        if not val:
            return "{}"
        items = []
        for k, v in val.items():
            k_str = pprint_value(k, indent + 1)
            v_str = pprint_value(v, indent + 1)
            items.append(f"{sp1}{k_str}: {v_str},")
        return "{\n" + "\n".join(items) + f"\n{sp}}}"
    return repr(val)


def write_structure(name: str, data: dict, f) -> None:
    """Write a top-level dict constant."""
    f.write(f"\n{name} = {{\n")
    for key, clause in data.items():
        key_str = pprint_value(key, 1)
        f.write(f"    {key_str}: {{\n")
        # Write fields in order: title, sub_clauses/sub_sections, evidence, typical_findings, audit_questions, evidence_to_check
        for field in ["title", "sub_clauses", "sub_sections", "evidence", "typical_findings", "audit_questions", "evidence_to_check"]:
            if field in clause:
                f.write(f"        '{field}': ")
                # Special handling for sub_clauses/sub_sections (may be enriched)
                if field in ("sub_clauses", "sub_sections"):
                    enriched = enrich_sub_clauses(clause[field])
                    f.write(pprint_value(enriched, 2))
                    f.write(",\n")
                else:
                    f.write(pprint_value(clause[field], 2))
                    f.write(",\n")
        f.write("    },\n")
    f.write("}\n\n")


def main():
    # Read and exec the existing clause_data to get the data structures
    import importlib.util
    import types

    # Use exec to load the module's data
    with open(CLAUSE_DATA) as f:
        source = f.read()

    # Extract just the top-level dict assignments (data structures)
    # We'll use ast to parse and identify top-level assignments
    import ast
    tree = ast.parse(source)

    # Find all top-level variable names that are dicts
    top_levels = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    top_levels.append(target.id)

    # Exec the module to get runtime values
    namespace = {}
    exec(compile(source, str(CLAUSE_DATA), "exec"), namespace)

    # Enrich and write back
    output = []
    with open(CLAUSE_DATA) as f:
        lines = f.readlines()

    # We'll write a new file with enriched data structures
    # First preserve the imports and comments up to the first data assignment
    output_lines = []
    in_data = False
    for line in lines:
        if line.strip().startswith("# ── ") or line.strip().startswith("from ") or line.strip().startswith("import "):
            output_lines.append(line)
            continue
        if line.strip().startswith("HLS_CORE"):
            in_data = True
            break
        output_lines.append(line)

    # Build enriched data structures
    enriched = {}
    for name in ["HLS_CORE", "CLAUSE_8", "ANNEX_A_27001", "ANNEX_A_42001", "PIMS_27701",
                  "FRAMEWORK_31000", "FRAMEWORK_10002"]:
        if name in namespace:
            enriched[name] = namespace[name]

    # Now write the enriched data
    with open(CLAUSE_DATA, "w") as f:
        # Write header section
        f.writelines(output_lines)

        # Write each enriched structure
        for name in ["HLS_CORE", "CLAUSE_8", "ANNEX_A_27001", "ANNEX_A_42001",
                      "PIMS_27701", "FRAMEWORK_31000", "FRAMEWORK_10002"]:
            if name in enriched:
                write_structure(name, enriched[name], f)

        # Write the rest of the file from SUPPORTING_STANDARDS_EVIDENCE onwards
        in_rest = False
        for line in lines:
            if line.strip().startswith("SUPPORTING_STANDARDS_EVIDENCE"):
                in_rest = True
            if in_rest:
                f.write(line)

    print(f"✅ Enriched {sum(len(v) for v in enriched.values())} top-level entries")
    print(f"   Structures: {', '.join(enriched.keys())}")


if __name__ == "__main__":
    main()
