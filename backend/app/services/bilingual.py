"""Bilingual text constants for document generators.

All user-facing text is defined here in both English and Arabic.
Generators pull from this module based on client language setting.
"""

# ── Section headings ──────────────────────────────────────────────────────

HEADINGS = {
    "en": {
        "audit_objectives": "1. Audit Objectives",
        "audit_scope": "2. Audit Scope",
        "audit_criteria": "3. Audit Criteria",
        "audit_team": "4. Audit Team",
        "daily_schedule": "5. Daily Schedule",
        "confidentiality": "6. Confidentiality",
        "language_report": "7. Language & Report Date",
        "general_info": "1. General Information",
        "executive_summary": "3. Executive Summary",
        "key_strengths": "3.1 Key Strengths",
        "audit_methodology": "4. Audit Methodology",
        "approach": "4.1 Audit Approach",
        "sampling": "4.2 Sampling Methodology",
        "criteria": "4.3 Audit Criteria",
        "methods": "4.4 Audit Methods",
        "detailed_findings": "5. Detailed Findings",
        "positive_findings": "5.1 Positive Findings",
        "ofi": "5.2 Opportunities for Improvement",
        "nonconformities": "5.3 Nonconformities",
        "conclusion": "6. Conclusion",
        "checklist_results": "Checklist Results",
        "overall_assessment": "Overall Assessment",
        "certificate_details": "Certificate Details",
        "attendance_record": "Attendance Record",
        "nc_observation_log": "Nonconformity & Observation Log",
        "summary": "Summary",
        "notes": "Notes",
        "table_of_contents": "Table of Contents",
    },
    "ar": {
        "audit_objectives": "1. أهداف المراجعة",
        "audit_scope": "2. نطاق المراجعة",
        "audit_criteria": "3. معايير المراجعة",
        "audit_team": "4. فريق المراجعة",
        "daily_schedule": "5. الجدول اليومي",
        "confidentiality": "6. السرية",
        "language_report": "7. اللغة وتاريخ التقرير",
        "general_info": "1. معلومات عامة",
        "executive_summary": "3. ملخص تنفيذي",
        "key_strengths": "3.1 نقاط القوة",
        "audit_methodology": "4. منهجية المراجعة",
        "approach": "4.1 أسلوب المراجعة",
        "sampling": "4.2 منهجية أخذ العينات",
        "criteria": "4.3 معايير المراجعة",
        "methods": "4.4 أساليب المراجعة",
        "detailed_findings": "5. النتائج التفصيلية",
        "positive_findings": "5.1 النتائج الإيجابية",
        "ofi": "5.2 فرص التحسين",
        "nonconformities": "5.3 حالات عدم المطابقة",
        "conclusion": "6. الخلاصة",
        "checklist_results": "نتائج قائمة الفحص",
        "overall_assessment": "التقييم العام",
        "certificate_details": "تفاصيل الشهادة",
        "attendance_record": "سجل الحضور",
        "nc_observation_log": "سجل عدم المطابقة والملاحظات",
        "summary": "الملخص",
        "notes": "ملاحظات",
        "table_of_contents": "جدول المحتويات",
    },
}

# ── Table column headers ──────────────────────────────────────────────────

TABLE_HEADERS = {
    "en": {
        "tnl": ["TNL #", "Clause", "Type", "Description", "Severity", "Auditee", "Due Date", "Status"],
        "audit_team": ["Name", "Role", "Audit Days"],
        "daily_schedule": ["Day", "Date", "Time", "Activity", "Auditee", "Auditor", "Clause"],
        "participants": ["Name", "Company", "Function / Department", "Closing Meeting", "Signature"],
        "nc_table": ["Clause", "Severity", "Description", "Due Date"],
        "certificate_fields": [
            "Certificate Number", "Client", "Standard", "Audit Date", "Scope",
            "Lead Auditor", "Certification Body", "Certification Decision",
            "Issue Date", "Expiry Date", "Authorized Signatory",
        ],
    },
    "ar": {
        "tnl": ["رقم سجل المراجعة", "البند", "النوع", "الوصف", "الخطورة", "المراجَع", "تاريخ الاستحقاق", "الحالة"],
        "audit_team": ["الاسم", "الدور", "أيام المراجعة"],
        "daily_schedule": ["اليوم", "التاريخ", "الوقت", "النشاط", "المراجَع", "المراجع", "البند"],
        "participants": ["الاسم", "الشركة", "الوظيفة / القسم", "اجتماع الإغلاق", "التوقيع"],
        "nc_table": ["البند", "الخطورة", "الوصف", "تاريخ الاستحقاق"],
        "certificate_fields": [
            "رقم الشهادة", "العميل", "المواصفة", "تاريخ المراجعة", "النطاق",
            "المراجع الرئيسي", "جهة الاعتماد", "قرار الاعتماد",
            "تاريخ الإصدار", "تاريخ الانتهاء", "المفوض بالتوقيع",
        ],
    },
    "checklist_qa": [
        "English Clause Reference",
        "Audit Questions & Evidence to Check",
        "Arabic Clause Reference",
        "أسئلة المراجعة والأدلة",
    ],
    "checklist_findings": [
        "Clause Reference",
        "Findings / Observations",
        "Status",
        "Reference",
    ],
}

# ── Section headers for two‑section checklist layout ──────────────────────

SECTION_HEADERS = {
    "checklist_qa": "Checklist — Questions & Evidence",
    "checklist_findings": "Checklist — Findings & Status",
    "checklist_qa_ar": "قائمة الفحص — أسئلة وأدلة",
    "checklist_findings_ar": "قائمة الفحص — النتائج والحالة",
}

# ── Cover page labels ─────────────────────────────────────────────────────

COVER_LABELS = {
    "en": {
        "client": "Client",
        "standard": "Standard",
        "date": "Date",
        "lead_auditor": "Lead Auditor",
        "confidential": "This document is confidential and intended solely for the use of the client.",
        "of_audit": "of Audit",
        "certified_at": "at the premises of:",
        "audit_date": "Audit Date",
        "scope": "Scope",
        "certification_body": "Certification Body",
        "certification_decision": "Certification Decision",
        "issue_date": "Issue Date",
        "expiry_date": "Expiry Date",
        "conditions": "Conditions",
        "certified": "Certified",
        "conditional": "Conditional",
        "not_certified": "Not Certified",
    },
    "ar": {
        "client": "العميل",
        "standard": "المواصفة",
        "date": "التاريخ",
        "lead_auditor": "المراجع الرئيسي",
        "confidential": "هذه الوثيقة سرية ومخصصة لاستخدام العميل فقط",
        "of_audit": "للمراجعة",
        "certified_at": "في مقر:",
        "audit_date": "تاريخ المراجعة",
        "scope": "النطاق",
        "certification_body": "جهة الاعتماد",
        "certification_decision": "قرار الاعتماد",
        "issue_date": "تاريخ الإصدار",
        "expiry_date": "تاريخ الانتهاء",
        "conditions": "الشروط",
        "certified": "معتمد",
        "conditional": "مشروط",
        "not_certified": "غير معتمد",
    },
}

# ── Methodology text ──────────────────────────────────────────────────────

METHODOLOGY = {
    "en": {
        "approach": (
            "The audit was conducted in accordance with ISO 19011:2018 guidelines for auditing management systems. "
            "A process-based approach was employed, following the Plan-Do-Check-Act (PDCA) cycle across all relevant "
            "clauses of {standard}. The audit examined the sequence and interaction of processes, "
            "their performance indicators, and the allocation of resources to achieve planned results."
        ),
        "sampling": (
            "Audit evidence was gathered through interviews with personnel at all relevant levels of the organization, "
            "observation of operational processes and work practices, and comprehensive review of documented information "
            "including policies, procedures, operational records, and performance reports. Sampling techniques were applied "
            "in accordance with ISO 19011:2018 guidelines, taking into account the complexity, risk profile, and "
            "significance of each process."
        ),
        "criteria": (
            "The audit criteria consisted of the requirements of {standard}, the organization's own "
            "management system documentation (including policies, procedures, and work instructions), "
            "applicable statutory and regulatory requirements, and relevant standards referenced in the standard family."
        ),
        "methods": (
            "Methods employed included: (1) document review and records analysis of policies, procedures, "
            "and operational documentation; (2) observation of operational activities and work practices "
            "at the organization's premises; (3) interviews with top management, process owners, "
            "and operational personnel at various levels; (4) verification of resources, infrastructure, "
            "and work environment; (5) traceability audits from records back to source documentation; "
            "and (6) verification of corrective and preventive actions from previous audits."
        ),
    },
    "ar": {
        "approach": (
            "تم إجراء المراجعة وفقًا لإرشادات ISO 19011:2018 لمراجعة أنظمة الإدارة. "
            "تم اعتماد نهج قائم على العمليات، باتباع دورة التخطيط-التنفيذ-الفحص-التصرف (PDCA) "
            "عبر جميع البنود ذات الصلة في {standard}. فحصت المراجعة تسلسل العمليات وتفاعلها، "
            "ومؤشرات أدائها، وتخصيص الموارد لتحقيق النتائج المخطط لها."
        ),
        "sampling": (
            "تم جمع أدلة المراجعة من خلال مقابلات مع الموظفين على جميع المستويات ذات الصلة في المنظمة، "
            "وملاحظة العمليات التشغيلية وممارسات العمل، ومراجعة شاملة للمعلومات الموثقة "
            "بما في ذلك السياسات والإجراءات والسجلات التشغيلية وتقارير الأداء. "
            "تم تطبيق تقنيات أخذ العينات وفقًا لإرشادات ISO 19011:2018، مع مراعاة التعقيد "
            "وملف المخاطر وأهمية كل عملية."
        ),
        "criteria": (
            "تكونت معايير المراجعة من متطلبات {standard}، وتوثيق نظام الإدارة الخاص بالمنظمة "
            "(بما في ذلك السياسات والإجراءات وتعليمات العمل)، والمتطلبات القانونية والتنظيمية المعمول بها، "
            "والمعايير ذات الصلة المشار إليها في عائلة المعايير."
        ),
        "methods": (
            "شملت الأساليب المستخدمة: (1) مراجعة الوثائق وتحليل السجلات للسياسات والإجراءات "
            "والتوثيق التشغيلي؛ (2) ملاحظة الأنشطة التشغيلية وممارسات العمل في مقر المنظمة؛ "
            "(3) مقابلات مع الإدارة العليا وأصحاب العمليات والموظفين التشغيليين على مختلف المستويات؛ "
            "(4) التحقق من الموارد والبنية التحتية وبيئة العمل؛ (5) مراجعات التتبع من السجلات "
            "إلى الوثائق المصدر؛ (6) التحقق من الإجراءات التصحيحة والوقائية من المراجعات السابقة."
        ),
    },
}

# ── Confidentiality statements ─────────────────────────────────────────────

CONFIDENTIALITY = {
    "en": "All information obtained during this audit shall be treated as strictly confidential and used solely for the purpose of certification.",
    "ar": "يجب التعامل مع جميع المعلومات التي تم الحصول عليها خلال هذه المراجعة على أنها سرية للغاية وتستخدم فقط لأغراض الاعتماد.",
}

# ── Helper to get text ────────────────────────────────────────────────────

def t(key: str, lang: str = "en", category: str = "HEADINGS") -> str:
    """Look up a text string by key and language.
    
    Usage: t("audit_objectives", "ar") → "1. أهداف المراجعة"
    """
    cat = globals().get(category, HEADINGS)
    lang_dict = cat.get(lang, cat.get("en", {}))
    return lang_dict.get(key, key)
