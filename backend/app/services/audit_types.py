"""Audit Type Module - initial / surveillance / recertification doc sets and hard rules."""

AUDIT_TYPES = ["initial", "surveillance", "recertification"]

AUDIT_TYPE_LABELS = {
    "initial": "Initial Certification",
    "surveillance": "Surveillance",
    "recertification": "Recertification",
}

SURVEILLANCE_DOCS = [
    "Surveillance_Plan",
    "Participation_List",
    "Surveillance_Report",
    "ISO_Checklist",
    "Surveillance_Findings_Summary",
]

FULL_CERTIFICATION_DOCS = [
    "Audit_Plan_Stage_1",
    "Audit_Plan_Stage_2",
    "Participation_List",
    "Audit_Report",
    "ISO_Checklist",
    "Certificate_Text",
    "TNL",
    "Certificate",
]

AUDIT_TYPE_DOCS = {
    "initial": FULL_CERTIFICATION_DOCS,
    "recertification": FULL_CERTIFICATION_DOCS,
    "surveillance": SURVEILLANCE_DOCS,
}

SURVEILLANCE_HARD_RULES = [
    "NO Certificate text or Certificate document is ever generated for a surveillance audit.",
    "NO Stage 1 / Stage 2 split. Use a single combined Surveillance Audit Plan covering clauses 4-10.",
    "SAAC accreditation must appear on all surveillance documents.",
    "Mandatory 'Review of Open Nonconformities' section in the plan and report.",
    "Mandatory 'Review of Changes' section in the plan and report (organizational changes since initial certification).",
    "CB Recommendation must default to 'Continued Certification' unless major NCs are found.",
    "Findings in the plan must be 'To be verified on-site' placeholders.",
    "Mandatory 'Previously Raised Nonconformities' review section in the Surveillance Report.",
    "Mandatory 'Changes Since Initial Certification' section in the Surveillance Report.",
    "Surveillance mandays are reduced by 30% from the initial certification mandays.",
]

RECERTIFICATION_HARD_RULES = [
    "Full scope audit - no clause reduction applies.",
    "Mandatory '3-Year Performance Review' section in the Audit Report.",
    "Mandatory 'Changes Since Initial Certification' section in the Audit Report.",
    "Certificate renewal with new certificate number TUV-YYYY-NNN and new 3-year validity.",
    "CB Recommendation reflects continued certification based on 3-year performance.",
]

INITIAL_HARD_RULES = [
    "Stage 1 (Readiness Review) and Stage 2 (Certification Audit) plans are both generated.",
    "Stage 2 plan covers full clause assessment including all shifts and sites.",
    "Certificate issuance follows only after successful Stage 2 completion.",
]

HARD_RULES = {
    "initial": INITIAL_HARD_RULES,
    "surveillance": SURVEILLANCE_HARD_RULES,
    "recertification": RECERTIFICATION_HARD_RULES,
}


def get_docs_for_audit_type(audit_type: str) -> list:
    """Return the list of document types to generate for an audit type."""
    return list(AUDIT_TYPE_DOCS.get(audit_type, FULL_CERTIFICATION_DOCS))


def get_hard_rules(audit_type: str) -> str:
    """Return the hard rules for an audit type as a prompt block (or empty string)."""
    rules = HARD_RULES.get(audit_type)
    if not rules:
        return ""
    return "\n".join(f"- {rule}" for rule in rules)


def get_audit_type_label(audit_type: str) -> str:
    """Human-readable label for UI display."""
    return AUDIT_TYPE_LABELS.get(audit_type, audit_type)