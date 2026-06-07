"""IMS Multi-Standard Support — cross-standard clause mapping.

Enables Integrated Management System (IMS) document generation where
a single policy/procedure covers multiple standards simultaneously.

Example: SAGCO (ISO 45001 + ISO 14001) — one "Context of the Organization"
policy covers Clause 4.1 from both standards.

Mapping types:
- identical: Same requirement in both standards (e.g., Clause 4.1 Context)
- compatible: Similar but with standard-specific additions
- unique: Only exists in one standard (e.g., Clause 8.2 Emergency Prep for 45001)
"""

from typing import Optional

from app.services.clause_data import HLS_CORE, CLAUSE_8


# ── Cross-Standard Clause Mappings ─────────────────────────────────────────

IMS_MAPPINGS = {
    ("iso_45001", "iso_14001"): {
        "name": "IMS-OHS-ENV",
        "description": "Integrated OH&S and Environmental Management System",
        "clauses": {
            "4.1": {
                "title": "Context of the Organization",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Understanding the organization and its context"},
                    "iso_14001": {"title": "Understanding the organization and its context"},
                },
                "integrated_scope": "single",
                "notes": "Identical requirements — one context analysis covers both",
                "doc_suggestions": ["Context Analysis", "Stakeholder Register", "PESTLE Analysis"],
            },
            "4.2": {
                "title": "Needs and Expectations of Interested Parties",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "Understanding the needs and expectations of workers and other interested parties"},
                    "iso_14001": {"title": "Understanding the needs and expectations of interested parties"},
                },
                "integrated_scope": "single",
                "notes": "45001 specifically mentions workers — expand stakeholder list to include workforce",
                "doc_suggestions": ["Stakeholder Analysis Matrix", "Worker Consultation Records"],
            },
            "4.3": {
                "title": "Scope of the Management System",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Determining the scope of the OH&S management system"},
                    "iso_14001": {"title": "Determining the scope of the environmental management system"},
                },
                "integrated_scope": "note",
                "notes": "Combine into one IMS scope statement noting both OH&S and Environmental boundaries",
                "doc_suggestions": ["IMS Scope Statement"],
            },
            "4.4": {
                "title": "Management System and Its Processes",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "OH&S management system"},
                    "iso_14001": {"title": "Environmental management system"},
                },
                "integrated_scope": "single",
                "notes": "One IMS manual covers both systems — reference both standards",
                "doc_suggestions": ["IMS Manual"],
            },
            "5.1": {
                "title": "Leadership and Commitment",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Leadership and commitment"},
                    "iso_14001": {"title": "Leadership and commitment"},
                },
                "integrated_scope": "single",
                "notes": "Identical top management commitments — one leadership statement",
                "doc_suggestions": ["Management Commitment Statement", "IMS Policy"],
            },
            "5.2": {
                "title": "Policy",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "OH&S policy"},
                    "iso_14001": {"title": "Environmental policy"},
                },
                "integrated_scope": "single",
                "notes": "One IMS Policy with both OH&S and Environmental commitments",
                "doc_suggestions": ["Integrated Policy (OH&S + Environmental)"],
            },
            "5.3": {
                "title": "Roles, Responsibilities and Authorities",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Organizational roles, responsibilities and authorities"},
                    "iso_14001": {"title": "Organizational roles, responsibilities and authorities"},
                },
                "integrated_scope": "single",
                "notes": "One org chart and responsibility matrix covering both IMS roles",
                "doc_suggestions": ["IMS Organization Chart", "RACI Matrix"],
            },
            "6.1": {
                "title": "Actions to Address Risks and Opportunities",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "Actions to address risks and opportunities"},
                    "iso_14001": {"title": "Actions to address risks and opportunities"},
                },
                "integrated_scope": "integrated",
                "notes": "One risk register with OH&S hazards AND environmental aspects — use risk category column to distinguish",
                "doc_suggestions": ["IMS Risk Register", "Hazard Register", "Environmental Aspects Register"],
            },
            "6.2": {
                "title": "Objectives and Planning",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "OH&S objectives and planning to achieve them"},
                    "iso_14001": {"title": "Environmental objectives and planning to achieve them"},
                },
                "integrated_scope": "integrated",
                "notes": "One objectives framework with both OH&S and Environmental targets",
                "doc_suggestions": ["IMS Objectives Register", "KPI Framework"],
            },
            "7.1": {
                "title": "Resources",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Resources"},
                    "iso_14001": {"title": "Resources"},
                },
                "integrated_scope": "single",
                "notes": "Identical — one resource management plan",
                "doc_suggestions": ["Resource Management Plan"],
            },
            "7.2": {
                "title": "Competence",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Competence"},
                    "iso_14001": {"title": "Competence"},
                },
                "integrated_scope": "single",
                "notes": "Combined training needs analysis — OH&S and Environmental competence",
                "doc_suggestions": ["Training Needs Matrix", "Competence Register"],
            },
            "7.3": {
                "title": "Awareness",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Awareness"},
                    "iso_14001": {"title": "Awareness"},
                },
                "integrated_scope": "single",
                "notes": "Identical awareness requirements",
                "doc_suggestions": ["Awareness Training Program"],
            },
            "7.4": {
                "title": "Communication",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Communication"},
                    "iso_14001": {"title": "Communication"},
                },
                "integrated_scope": "single",
                "notes": "One communication plan — internal/external for both IMS",
                "doc_suggestions": ["Communication Plan"],
            },
            "7.5": {
                "title": "Documented Information",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Documented information"},
                    "iso_14001": {"title": "Documented information"},
                },
                "integrated_scope": "single",
                "notes": "One document control procedure",
                "doc_suggestions": ["Document Control Procedure", "Document Register"],
            },
            "8.1": {
                "title": "Operational Planning and Control",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "Operational planning and control"},
                    "iso_14001": {"title": "Operational planning and control"},
                },
                "integrated_scope": "integrated",
                "notes": "One operational control procedure — address OH&S hazards AND environmental aspects",
                "doc_suggestions": ["Operational Control Procedure", "Permit to Work System"],
            },
            "9.1": {
                "title": "Monitoring, Measurement, Analysis",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "Monitoring, measurement, analysis and performance evaluation"},
                    "iso_14001": {"title": "Monitoring, measurement, analysis and performance evaluation"},
                },
                "integrated_scope": "integrated",
                "notes": "One monitoring plan — OH&S KPIs AND Environmental indicators",
                "doc_suggestions": ["Monitoring and Measurement Plan", "KPI Dashboard"],
            },
            "9.2": {
                "title": "Internal Audit",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Internal audit"},
                    "iso_14001": {"title": "Internal audit"},
                },
                "integrated_scope": "single",
                "notes": "One IMS internal audit program covering both standards",
                "doc_suggestions": ["IMS Internal Audit Plan", "Integrated Audit Checklist"],
            },
            "9.3": {
                "title": "Management Review",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Management review"},
                    "iso_14001": {"title": "Management review"},
                },
                "integrated_scope": "single",
                "notes": "One IMS management review meeting covering both standards",
                "doc_suggestions": ["Management Review Agenda", "Management Review Minutes"],
            },
            "10.1": {
                "title": "General (Improvement)",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "General"},
                    "iso_14001": {"title": "General"},
                },
                "integrated_scope": "single",
                "notes": "Identical — one improvement process",
                "doc_suggestions": ["Improvement Procedure"],
            },
            "10.2": {
                "title": "Incident, Nonconformity and Corrective Action",
                "mapping_type": "compatible",
                "standards": {
                    "iso_45001": {"title": "Incident, nonconformity and corrective action"},
                    "iso_14001": {"title": "Nonconformity and corrective action"},
                },
                "integrated_scope": "single",
                "notes": "45001 includes 'incident' — combined procedure covers incidents, NCs, and CAPA for both IMS",
                "doc_suggestions": ["Incident Investigation Procedure", "CAPA Log", "NC Register"],
            },
            "10.3": {
                "title": "Continual Improvement",
                "mapping_type": "identical",
                "standards": {
                    "iso_45001": {"title": "Continual improvement"},
                    "iso_14001": {"title": "Continual improvement"},
                },
                "integrated_scope": "single",
                "notes": "Identical",
                "doc_suggestions": ["Continual Improvement Plan"],
            },
        },
    },
    ("iso_9001", "iso_14001"): {
        "name": "IMS-Q-ENV",
        "description": "Integrated Quality and Environmental Management System",
        "clauses": {
            "4.1": {"mapping_type": "identical", "title": "Context", "integrated_scope": "single"},
            "4.2": {"mapping_type": "identical", "title": "Interested Parties", "integrated_scope": "single"},
            "5.1": {"mapping_type": "identical", "title": "Leadership", "integrated_scope": "single"},
            "5.2": {"mapping_type": "compatible", "title": "Policy", "integrated_scope": "single"},
            "6.1": {"mapping_type": "compatible", "title": "Risks & Opportunities", "integrated_scope": "integrated"},
            "7.1": {"mapping_type": "identical", "title": "Resources", "integrated_scope": "single"},
            "8.1": {"mapping_type": "compatible", "title": "Operational Control", "integrated_scope": "integrated"},
            "9.1": {"mapping_type": "compatible", "title": "Monitoring", "integrated_scope": "integrated"},
            "10.2": {"mapping_type": "identical", "title": "NC & Corrective Action", "integrated_scope": "single"},
        },
    },
    ("iso_27001", "iso_27701"): {
        "name": "IMS-ISMS-PIMS",
        "description": "Integrated Information Security and Privacy Management System",
        "clauses": {
            "4.1": {"mapping_type": "identical", "title": "Context", "integrated_scope": "single"},
            "4.2": {"mapping_type": "compatible", "title": "Interested Parties", "integrated_scope": "single"},
            "6.1": {"mapping_type": "compatible", "title": "Risk Assessment", "integrated_scope": "integrated"},
            "8.1": {"mapping_type": "compatible", "title": "Operational Control", "integrated_scope": "integrated"},
            "9.1": {"mapping_type": "identical", "title": "Monitoring", "integrated_scope": "single"},
        },
    },
}


# ── Helper Functions ───────────────────────────────────────────────────────

def get_ims_mapping(standards: list) -> Optional[dict]:
    """Get IMS mapping for a combination of standards."""
    # Try both orderings
    key = tuple(standards)
    if key in IMS_MAPPINGS:
        return IMS_MAPPINGS[key]
    key_rev = tuple(reversed(standards))
    if key_rev in IMS_MAPPINGS:
        return IMS_MAPPINGS[key_rev]
    # Try sorted
    key_sorted = tuple(sorted(standards))
    return IMS_MAPPINGS.get(key_sorted)


def get_integrated_clause_list(standards: list) -> list:
    """Get a deduplicated list of clauses for an IMS, with mapping info."""
    mapping = get_ims_mapping(standards)  # handles any order
    if not mapping:
        return []

    clauses = []
    seen = set()
    # Start with HLS core clauses
    for clause_num, clause_info in HLS_CORE.items():
        seen.add(clause_num)
        clause_entry = {
            "clause": clause_num,
            "title": clause_info["title"],
            "mapping": mapping["clauses"].get(clause_num, {}),
        }
        clauses.append(clause_entry)

    # Add Clause 8 variants
    for std in standards:
        c8 = CLAUSE_8.get(std, {})
        if isinstance(c8, dict):
            for clause_num, clause_info in c8.items():
                if clause_num not in seen and clause_num != "title":
                    seen.add(clause_num)
                    title = clause_info.get("title", "") if isinstance(clause_info, dict) else str(clause_info)
                    clauses.append({
                        "clause": clause_num,
                        "title": title,
                        "mapping": {"mapping_type": "unique", "standards": {std: {"title": title}}},
                    })

    def clause_sort_key(x):
        try:
            c = x["clause"]
            return float(c) if "." in c else int(c)
        except (ValueError, TypeError):
            return 999

    return sorted(clauses, key=clause_sort_key)


def get_shared_docs(standards: list) -> list:
    """Get list of documents that can be shared across standards."""
    mapping = get_ims_mapping(standards)  # handles any order
    if not mapping:
        return []

    shared = []
    seen_docs = set()
    for clause_num, clause_map in mapping["clauses"].items():
        if clause_map.get("integrated_scope") in ("single", "integrated"):
            for doc in clause_map.get("doc_suggestions", []):
                if doc not in seen_docs:
                    seen_docs.add(doc)
                    shared.append({
                        "document": doc,
                        "clause": clause_num,
                        "title": clause_map["title"],
                        "scope": clause_map["integrated_scope"],
                        "standards": [s.replace("iso_", "ISO ").replace("_", "-") for s in standards],
                    })
    return shared


def get_unique_requirements(standards: list) -> dict:
    """Get requirements that are unique to each standard (not shareable)."""
    mapping = get_ims_mapping(standards)  # handles any order
    if not mapping:
        return {}

    unique = {std: [] for std in standards}
    all_clause_nums = set(HLS_CORE.keys())

    for std in standards:
        c8 = CLAUSE_8.get(std, {})
        for clause_num, clause_info in c8.items():
            if clause_num == "title":
                continue
            ims_clause = mapping["clauses"].get(clause_num, {})
            if ims_clause.get("mapping_type") == "unique" or clause_num not in all_clause_nums:
                title = clause_info.get("title", "") if isinstance(clause_info, dict) else str(clause_info)
                unique[std].append({
                    "clause": clause_num,
                    "title": title,
                    "note": "Standard-specific — separate section required",
                })

    return unique


def generate_ims_gap_analysis(standards: list, compliance_data: dict) -> dict:
    """Generate a clause-by-clause gap analysis for an IMS.

    compliance_data format: {clause_num: {"status": "conformant"|"partial"|"nc"|"not_reviewed", "evidence": "..."}}
    """
    clauses = get_integrated_clause_list(standards)
    mapping = get_ims_mapping(standards)  # handles any order

    results = []
    total_clauses = len(clauses)
    conformant = 0
    partial = 0
    nc = 0
    not_reviewed = 0

    for clause in clauses:
        compliance = compliance_data.get(clause["clause"], {"status": "not_reviewed"})
        status = compliance.get("status", "not_reviewed")

        if status == "conformant":
            conformant += 1
        elif status == "partial":
            partial += 1
        elif status in ("nc", "major_nc", "minor_nc"):
            nc += 1
        else:
            not_reviewed += 1

        clause_map = clause.get("mapping", {})
        results.append({
            "clause": clause["clause"],
            "title": clause["title"],
            "status": status,
            "evidence": compliance.get("evidence", ""),
            "mapping_type": clause_map.get("mapping_type", "n/a"),
            "integrated_scope": clause_map.get("integrated_scope", "n/a"),
            "notes": clause_map.get("notes", ""),
        })

    score = int((conformant / total_clauses) * 100) if total_clauses > 0 else 0

    return {
        "standards": standards,
        "ims_name": mapping.get("name", "N/A") if mapping else "N/A",
        "total_clauses": total_clauses,
        "conformant": conformant,
        "partial": partial,
        "nc": nc,
        "not_reviewed": not_reviewed,
        "compliance_score": score,
        "clauses": results,
        "shared_docs": get_shared_docs(standards),
        "unique_requirements": get_unique_requirements(standards),
        "readiness": "ready" if score >= 80 else "gap_work_needed" if score >= 50 else "significant_gaps",
    }
