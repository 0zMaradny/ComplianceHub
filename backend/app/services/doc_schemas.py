"""Unified data contracts for all 8 document output types.
Both offline_generator and ai_pipeline must produce these exact shapes.
The document_generator consumes them without assumptions about missing fields."""

DOCUMENT_CONTRACTS = {

    # ── Audit Plan (shared by Stage 1 & Stage 2) ─────────────────────────
    'Audit_Plan': {
        'client_name': 'str — legal entity name',
        'audit_date': 'str DD/MM/YYYY — start date of audit',
        'standard': 'str — full standard name with year, e.g. ISO 9001:2015',
        'stage': 'str — "Stage 1 - Readiness Review" or "Stage 2 - Certification Audit"',
        'audit_team': [
            {'name': 'str', 'role': 'str', 'days': 'int'},
        ],
        'audit_objectives': ['str — 4-6 specific objectives'],
        'audit_scope': 'str — 2-3 sentence scope description',
        'audit_criteria': ['str — ISO clauses, regulatory reqs, documented procedures'],
        'daily_schedule': [
            {
                'day': 'int',
                'date': 'str DD/MM/YYYY',
                'time': 'str e.g. 09:00-10:30',
                'activity': 'str — specific audit activity',
                'auditee': 'str — person/role interviewed',
                'auditor': 'str — auditor name from team',
                'clause': 'str — ISO clause reference',
            },
        ],
        'confidentiality': 'str — confidentiality statement',
        'language': 'str e.g. English',
        'report_date': 'str DD/MM/YYYY — 30 days after audit',
    },

    # ── Participation List ──────────────────────────────────────────────
    'Participation_List': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'participants': [
            {
                'name': 'str',
                'company': 'str',
                'department': 'str',
                'closing_meeting': 'str — Yes/No',
                'signature': 'str — always empty string',
            },
        ],
        'notes': 'str — attendance notes',
    },

    # ── Audit Report ────────────────────────────────────────────────────
    'Audit_Report': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'report_number': 'str — format TUV-AR-YYYY-NNN',
        'scope': 'str',
        'lead_auditor': 'str',
        'audit_team': [
            {'name': 'str', 'role': 'str', 'days': 'int'},
        ],
        'findings_summary': 'str — 3-5 paragraphs: overall assessment, strengths, concerns, effectiveness',
        'positive_findings': ['str — 3-8 specific strengths observed'],
        'opportunities_for_improvement': ['str — 2-6 specific OFIs with clause references'],
        'nonconformities': [
            {
                'clause': 'str',
                'severity': 'str — Major/Minor',
                'description': 'str — detailed finding description',
                'due_date': 'str DD/MM/YYYY',
            },
        ],
        'conclusion': 'str — 2-3 paragraphs: recommendation, conditions, next surveillance',
        'report_date': 'str DD/MM/YYYY',
        'methodology': {
            'approach': 'str — process-based approach description',
            'sampling': 'str — sampling methodology per ISO 19011',
            'criteria': 'str — audit criteria reference',
            'methods': 'str — specific methods employed',
        },
    },

    # ── ISO Checklist ───────────────────────────────────────────────────
    'ISO_Checklist': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'auditor': 'str',
        'sections': [
            {
                'clause': 'str — e.g. 4.1',
                'title': 'str — clause title',
                'requirement': 'str — full clause requirement text',
                'status': 'str — Conformant/Partially Conformant/Non-Conformant/Not Reviewed',
                'evidence': 'str — 2-3 professional sentences with specific observations',
                'notes': 'str — additional context or observations',
                'reference': 'str — standard document reference',
            },
        ],
        'overall_assessment': 'str — 2-3 paragraphs summarizing compliance level',
    },

    # ── Certificate Text ────────────────────────────────────────────────
    'Certificate_Text': {
        'client_name': 'str',
        'certificate_number': 'str — format TUV-YYYY-NNN',
        'standard': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'scope': 'str',
        'lead_auditor': 'str',
        'certification_body': 'str — TÜV AUSTRIA',
        'certification_decision': 'str — Certified/Conditional/Not Certified',
        'issue_date': 'str DD/MM/YYYY',
        'expiry_date': 'str DD/MM/YYYY — 3 years from issue',
        'authorized_signatory': 'str',
    },

    # ── TNL (Test/Nonconformity Log) ────────────────────────────────────
    'TNL': {
        'client_name': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'entries': [
            {
                'tnl_number': 'str — e.g. TNL-001',
                'clause': 'str — ISO clause reference',
                'type': 'str — NC/OFI/OBS',
                'description': 'str — detailed finding description',
                'severity': 'str — Major/Minor/N/A',
                'auditee': 'str — responsible person',
                'due_date': 'str DD/MM/YYYY',
                'status': 'str — Open/Closed/In Progress',
            },
        ],
        'summary': {
            'total_nc': 'int',
            'major': 'int',
            'minor': 'int',
            'ofi': 'int',
            'observations': 'int',
        },
    },

    # ── Certificate ─────────────────────────────────────────────────────
    'Certificate': {
        'client_name': 'str',
        'certificate_number': 'str',
        'standard': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'scope': 'str',
        'lead_auditor': 'str',
        'certification_body': 'str — TÜV AUSTRIA',
        'certification_decision': 'str — Certified/Conditional/Not Certified',
        'issue_date': 'str DD/MM/YYYY',
        'expiry_date': 'str DD/MM/YYYY — 3 years from issue',
        'authorized_signatory': 'str',
        'conditions': ['str — conditions of certification (empty if none)'],
    },

    # ── Management Review Minutes (ISO Clause 9.3) ─────────────────────────
    'Management_Review_Minutes': {
        'client_name': 'str',
        'review_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'chairperson': 'str',
        'attendees': [
            {'name': 'str', 'role': 'str', 'department': 'str'},
        ],
        'agenda_items': [
            {'item': 'str', 'presented_by': 'str', 'discussion': 'str'},
        ],
        'decisions': [
            {'decision': 'str', 'rationale': 'str', 'owner': 'str'},
        ],
        'action_items': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str', 'status': 'str'},
        ],
        'review_inputs': 'str — 2-3 paragraphs: performance data, audit results, feedback, NC status, risk review',
        'review_outputs': 'str — 2-3 paragraphs: resource needs, improvement opportunities, policy/objective changes',
        'next_review_date': 'str DD/MM/YYYY — typically 12 months from review_date',
        'report_date': 'str DD/MM/YYYY',
    },

    # ── Corrective Action Report (ISO Clause 10.1) ────────────────────────
    'Corrective_Action_Report': {
        'client_name': 'str',
        'car_number': 'str — format TUV-CAR-YYYY-NNN',
        'standard': 'str',
        'audit_date': 'str DD/MM/YYYY',
        'nc_reference': 'str — TNL reference number',
        'clause': 'str — ISO clause reference',
        'severity': 'str — Major/Minor',
        'problem_description': 'str — detailed NC description',
        'root_cause': 'str — root cause analysis (5 Whys, fishbone, etc.)',
        'containment_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'corrective_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'preventive_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'verification_method': 'str — follow-up audit, document review, on-site verification',
        'status': 'str — Open/In Progress/Closed/Verified',
        'reviewed_by': 'str',
        'closure_date': 'str DD/MM/YYYY',
    },

    # ── Gap Analysis Report (Pre-Audit Assessment) ────────────────────────
    'Gap_Analysis_Report': {
        'client_name': 'str',
        'assessment_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'assessor': 'str',
        'methodology': 'str — gap assessment methodology description',
        'sections': [
            {
                'clause': 'str — e.g. 4.1',
                'title': 'str — clause title',
                'requirement': 'str — full clause requirement text',
                'status': 'str — Conformant/Partially Conformant/Non-Conformant/Not Reviewed',
                'gap_description': 'str — description of identified gap',
                'recommended_action': 'str — action to close the gap',
                'priority': 'str — High/Medium/Low',
                'target_date': 'str DD/MM/YYYY',
            },
        ],
        'summary': {
            'total_clauses': 'int',
            'conformant': 'int',
            'partially_conformant': 'int',
            'non_conformant': 'int',
            'not_reviewed': 'int',
            'overall_readiness': 'str — percentage or readiness level',
        },
        'overall_assessment': 'str — 2-3 paragraphs summarizing gap findings and readiness recommendation',
    },

    # ── Statement of Applicability (ISO 27001 / Annex A) ──────────────────
    'Statement_of_Applicability': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'based_on_risk_assessment': 'str — reference to risk assessment report or methodology',
        'controls': [
            {
                'control_ref': 'str — e.g. A.5.1',
                'control_title': 'str — control title from Annex A',
                'applicability': 'str — Applicable/Not Applicable',
                'justification': 'str — rationale for applicability decision including risk context',
                'selected_control': 'str — control description from ISO 27002 or equivalent',
                'implementation_status': 'str — Planned/In Progress/Implemented/Not Implemented',
                'responsible': 'str — responsible person or role',
            },
        ],
        'summary': {
            'total_controls': 'int',
            'applicable': 'int',
            'not_applicable': 'int',
            'implemented': 'int',
            'not_implemented': 'int',
        },
    },

    # ── Business Impact Analysis (ISO 22301 Clause 8.2.1) ────────────────────
    'Business_Impact_Analysis': {
        'client_name': 'str',
        'assessment_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'methodology': 'str — BIA methodology description',
        'critical_activities': [
            {
                'activity': 'str — business process name',
                'rto': 'str — Recovery Time Objective (e.g. 4 hours)',
                'rpo': 'str — Recovery Point Objective (e.g. 1 hour)',
                'mtd': 'str — Maximum Tolerable Downtime (e.g. 8 hours)',
                'impact_criteria': 'str — financial, reputational, regulatory, operational impact',
                'dependencies': 'str — internal and external dependencies',
                'recovery_strategy': 'str — recovery approach for the activity',
                'priority': 'str — Critical/High/Medium/Low',
            },
        ],
        'summary': {
            'total_activities': 'int',
            'critical': 'int',
            'high': 'int',
            'medium': 'int',
            'low': 'int',
        },
        'overall_findings': 'str — 2-3 paragraphs summarizing BIA outcomes',
    },

    # ── Records of Processing Activities (ISO 27701 Clause 7.6 / GDPR Art 30)
    'Records_of_Processing_Activities': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'data_controller': 'str — legal entity name and address',
        'data_protection_officer': 'str — DPO name and contact',
        'processing_activities': [
            {
                'activity_id': 'str — e.g. ROPA-001',
                'activity_name': 'str — processing activity description',
                'purpose': 'str — lawful basis and purpose of processing',
                'data_subjects': 'str — categories of data subjects',
                'personal_data_categories': 'str — categories of personal data processed',
                'retention_period': 'str — retention schedule',
                'cross_border_transfer': 'str — transfer details or "None"',
                'security_measures': 'str — technical and organizational measures',
            },
        ],
        'summary': {
            'total_activities': 'int',
            'has_cross_border_transfers': 'str — Yes/No',
        },
    },

    # ── Risk Treatment Plan (ISO 27001 Clause 8.3 / ISO 31000) ─────────────
    'Risk_Treatment_Plan': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'risk_assessment_reference': 'str — reference to risk assessment report',
        'risks': [
            {
                'risk_id': 'str — e.g. RISK-001',
                'risk_description': 'str — description of the risk',
                'source': 'str — risk source or threat',
                'likelihood': 'str — Very Low/Low/Medium/High/Very High',
                'impact': 'str — Very Low/Low/Medium/High/Very High',
                'risk_level': 'str — Low/Medium/High/Critical',
                'treatment_option': 'str — Avoid/Reduce/Transfer/Accept',
                'treatment_details': 'str — detailed treatment plan description',
                'selected_controls': 'str — Annex A or other controls selected',
                'risk_owner': 'str — responsible person',
                'target_date': 'str DD/MM/YYYY',
                'status': 'str — Open/In Progress/Implemented/Closed',
            },
        ],
        'summary': {
            'total_risks': 'int',
            'critical': 'int',
            'high': 'int',
            'medium': 'int',
            'low': 'int',
        },
    },

    # ── Incident Investigation Report (ISO 45001 Clause 10.2) ──────────────
    'Incident_Investigation_Report': {
        'client_name': 'str',
        'incident_date': 'str DD/MM/YYYY',
        'report_date': 'str DD/MM/YYYY',
        'standard': 'str',
        'incident_description': 'str — detailed incident description',
        'location': 'str — incident location',
        'incident_type': 'str — Near Miss/First Aid/Medical Treatment/Lost Time/Fatality/Property Damage',
        'severity': 'str — Low/Medium/High/Critical',
        'investigation_team': [
            {'name': 'str', 'role': 'str'},
        ],
        'root_cause': 'str — root cause analysis findings (2-3 paragraphs)',
        'immediate_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'corrective_actions': [
            {'action': 'str', 'owner': 'str', 'due_date': 'str'},
        ],
        'lessons_learned': ['str — lessons identified from the incident'],
        'recommendations': ['str — recommendations to prevent recurrence'],
        'status': 'str — Open/In Progress/Closed',
        'reviewed_by': 'str',
    },

    # ── Internal Audit Program (ISO Clause 9.2) ────────────────────────────
    'Internal_Audit_Program': {
        'client_name': 'str',
        'program_year': 'str — e.g. 2026',
        'standard': 'str',
        'audit_manager': 'str',
        'audits': [
            {
                'audit_id': 'str — e.g. IA-2026-001',
                'scope': 'str — audit scope description',
                'audit_type': 'str — Full/Partial/Follow-up/Special',
                'planned_date': 'str DD/MM/YYYY',
                'auditor': 'str',
                'auditee_department': 'str',
                'status': 'str — Planned/In Progress/Completed/Cancelled',
                'findings_count': 'int',
            },
        ],
        'summary': {
            'total_audits': 'int',
            'planned': 'int',
            'in_progress': 'int',
            'completed': 'int',
            'cancelled': 'int',
        },
    },

    # ── Environmental Aspect Register (ISO 14001 Clause 6.1.2) ──────────────
    'Environmental_Aspect_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'methodology': 'str — aspect identification methodology',
        'aspects': [
            {
                'aspect_id': 'str — e.g. EAR-001',
                'activity': 'str — activity, product, or service',
                'aspect': 'str — environmental aspect description',
                'environmental_impact': 'str — actual or potential impact',
                'impact_type': 'str — Positive/Negative',
                'significance': 'str — Low/Medium/High/Critical',
                'control_measures': 'str — existing controls',
                'legal_requirement': 'str — applicable legal or other requirement',
                'evaluation': 'str — significance evaluation criteria and result',
            },
        ],
        'summary': {
            'total_aspects': 'int',
            'critical': 'int',
            'high': 'int',
            'medium': 'int',
            'low': 'int',
        },
    },

    # ── Hazard Identification Register (ISO 45001 Clause 6.1.2) ────────────
    'Hazard_Identification_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'methodology': 'str — hazard identification methodology',
        'hazards': [
            {
                'hazard_id': 'str — e.g. HIR-001',
                'activity': 'str — work activity or area',
                'hazard': 'str — hazard description',  'associated_risk': 'str — risk description including who may be harmed',
                'existing_controls': 'str — current control measures',
                'risk_level': 'str — Low/Medium/High/Critical',
                'additional_controls': 'str — further controls required',
                'hierarchy_of_control': 'str — Elimination/Substitution/Engineering/Administrative/PPE',
            },
        ],
        'summary': {
            'total_hazards': 'int',
            'critical': 'int',
            'high': 'int',
            'medium': 'int',
            'low': 'int',
        },
    },

    # ── Energy Review + EnB + EnPI (ISO 50001 Clause 6.3) ──────────────────
    'Energy_Review': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'review_period': 'str — e.g. January 2026 – December 2026',
        'methodology': 'str — energy review methodology',
        'energy_sources': [
            {
                'source': 'str — energy type (electricity, natural gas, diesel, etc.)',
                'consumption': 'str — annual consumption with unit',
                'cost': 'str — annual cost',
                'trend': 'str — Increasing/Stable/Decreasing',
                'notes': 'str — additional observations',
            },
        ],
        'significant_uses': [
            {
                'use_id': 'str — e.g. SEU-001',
                'equipment': 'str — equipment or process name',
                'energy_source': 'str — primary energy source',
                'consumption': 'str — consumption value and unit',
                'variables': 'str — relevant variables affecting consumption',
                'enpi': 'str — Energy Performance Indicator',
                'baseline': 'str — Energy Baseline (EnB) reference period and value',
                'current_performance': 'str — current performance vs baseline',
            },
        ],
        'summary': {
            'total_energy_sources': 'int',
            'total_seus': 'int',
            'total_energy_cost': 'str — total annual energy cost',
        },
    },

    # ── Compliance Obligations Register (ISO 37301 / ISO 14001) ────────────
    'Compliance_Obligations_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'methodology': 'str — compliance identification methodology',
        'obligations': [
            {
                'obligation_id': 'str — e.g. COR-001',
                'obligation_type': 'str — Legal/Regulatory/Contractual/Other',
                'source': 'str — source of obligation (law, regulation, contract, standard)',
                'requirement': 'str — specific requirement text',
                'applicability': 'str — Full/Partial/Not Applicable',
                'compliance_status': 'str — Compliant/Partially Compliant/Non-Compliant/Not Assessed',
                'evidence': 'str — evidence of compliance',
                'due_date': 'str DD/MM/YYYY or "Ongoing"',
                'responsible': 'str — responsible person or role',
            },
        ],
        'summary': {
            'total_obligations': 'int',
            'compliant': 'int',
            'partially_compliant': 'int',
            'non_compliant': 'int',
            'not_assessed': 'int',
        },
    },

    # ── Service Portfolio & SLAs (ISO 20000-1 Clause 7.2) ─────────────────
    'Service_Portfolio': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'portfolio_manager': 'str',
        'services': [
            {
                'service_id': 'str — e.g. SVC-001',
                'service_name': 'str — service name',
                'description': 'str — service description',
                'category': 'str — Core/Support/Enabling',
                'status': 'str — Active/In Development/Retired/Planned',
                'sla_uptime': 'str — SLA uptime percentage target',
                'sla_response_time': 'str — SLA response time target',
                'sla_resolution_time': 'str — SLA resolution time target',
                'service_owner': 'str',
            },
        ],
        'summary': {
            'total_services': 'int',
            'active': 'int',
            'in_development': 'int',
            'retired': 'int',
            'planned': 'int',
        },
    },

    # ── Service Catalogue (ISO 20000-1 Clause 7.2) ─────────────────────
    'Service_Catalogue': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'catalogue_owner': 'str',
        'catalogue_version': 'str',
        'services': [
            {
                'service_id': 'str — e.g. CAT-001',
                'service_name': 'str',
                'description': 'str — brief description',
                'service_type': 'str — Business/Customer/Infrastructure',
                'status': 'str — Live/Deprecated/Under Review',
                'features': 'str — key features of the service',
                'contact': 'str — service owner or support contact',
                'service_hours': 'str — e.g. 24x7 or Business Hours',
            },
        ],
        'summary': {
            'total_services': 'int',
            'live': 'int',
            'deprecated': 'int',
            'under_review': 'int',
        },
    },

    # ── Supplier Agreement Register (ISO 20000-1 Clause 8.4.2) ─────────
    'Supplier_Agreement_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'register_owner': 'str',
        'agreements': [
            {
                'agreement_id': 'str — e.g. SAR-001',
                'supplier_name': 'str',
                'service_provided': 'str',
                'agreement_type': 'str — Contract/SLA/Partnership/Letter of Agreement',
                'start_date': 'str DD/MM/YYYY',
                'renewal_date': 'str DD/MM/YYYY',
                'status': 'str — Active/Expired/Under Negotiation/Terminated',
                'performance_rating': 'str — Excellent/Satisfactory/Needs Improvement',
                'key_contacts': 'str',
            },
        ],
        'summary': {
            'total_agreements': 'int',
            'active': 'int',
            'expired': 'int',
            'under_negotiation': 'int',
            'terminated': 'int',
        },
    },

    # ── Business Relationship Register (ISO 20000-1 Clause 8.4.3) ──────
    'Business_Relationship_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'relationship_manager': 'str',
        'customers': [
            {
                'customer_id': 'str — e.g. BRR-001',
                'customer_name': 'str',
                'account_manager': 'str',
                'services_used': 'str — summary of services consumed',
                'satisfaction_score': 'str — e.g. 8.5/10',
                'complaints': 'int',
                'last_review': 'str DD/MM/YYYY',
                'next_review': 'str DD/MM/YYYY',
                'status': 'str — Active/On Hold/At Risk/Inactive',
            },
        ],
        'summary': {
            'total_customers': 'int',
            'active': 'int',
            'on_hold': 'int',
            'at_risk': 'int',
            'inactive': 'int',
            'avg_satisfaction': 'str',
        },
    },

    # ── Capacity Management Plan (ISO 20000-1 Clause 8.5.2) ────────────
    'Capacity_Management_Plan': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'capacity_manager': 'str',
        'review_period': 'str',
        'scope': 'str',
        'components': [
            {
                'component_id': 'str — e.g. CMP-001',
                'component': 'str — server, network, storage, etc.',
                'current_capacity': 'str',
                'current_demand': 'str',
                'utilization': 'str — percentage',
                'threshold': 'str — e.g. 80%',
                'forecast_demand': 'str',
                'planned_upgrade': 'str — upgrade plan or timeline',
                'status': 'str — Green/Amber/Red',
            },
        ],
        'summary': {
            'total_components': 'int',
            'green': 'int',
            'amber': 'int',
            'red': 'int',
        },
    },

    # ── Change Management Register (ISO 20000-1 Clause 8.6.2) ──────────
    'Change_Management_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'change_manager': 'str',
        'changes': [
            {
                'change_id': 'str — e.g. CHG-001',
                'title': 'str',
                'description': 'str',
                'change_type': 'str — Standard/Normal/Emergency',
                'priority': 'str — Low/Medium/High/Critical',
                'risk_level': 'str — Low/Medium/High',
                'impact_assessment': 'str',
                'rollback_plan': 'str',
                'cab_date': 'str DD/MM/YYYY or N/A',
                'scheduled_date': 'str DD/MM/YYYY',
                'requestor': 'str',
                'status': 'str — Requested/Approved/In Progress/Implemented/Closed/Rolled Back',
            },
        ],
        'summary': {
            'total_changes': 'int',
            'requested': 'int',
            'approved': 'int',
            'in_progress': 'int',
            'implemented': 'int',
            'closed': 'int',
            'rolled_back': 'int',
        },
    },

    # ── Release & Deployment Plan (ISO 20000-1 Clause 8.6.4) ───────────
    'Release_Deployment_Plan': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'release_manager': 'str',
        'releases': [
            {
                'release_id': 'str — e.g. REL-001',
                'release_name': 'str',
                'scope': 'str',
                'release_type': 'str — Major/Minor/Patches/Emergency',
                'planned_date': 'str DD/MM/YYYY',
                'deployment_window': 'str — e.g. 22:00-06:00',
                'rollback_procedure': 'str',
                'status': 'str — Planned/In Progress/Deployed/Rolled Back/Cancelled',
            },
        ],
        'summary': {
            'total_releases': 'int',
            'planned': 'int',
            'in_progress': 'int',
            'deployed': 'int',
            'rolled_back': 'int',
            'cancelled': 'int',
        },
    },

    # ── Incident Management Log (ISO 20000-1 Clause 8.7.2) ──────────────
    'Incident_Management_Log': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'incident_manager': 'str',
        'incidents': [
            {
                'incident_id': 'str — e.g. INC-001',
                'incident_summary': 'str',
                'severity': 'str — P1 Critical/P2 High/P3 Medium/P4 Low',
                'reported_date': 'str DD/MM/YYYY HH:MM',
                'resolved_date': 'str DD/MM/YYYY HH:MM or Open',
                'affected_service': 'str',
                'resolution': 'str',
                'status': 'str — New/In Progress/Resolved/Closed/Escalated',
            },
        ],
        'summary': {
            'total_incidents': 'int',
            'critical': 'int',
            'high': 'int',
            'medium': 'int',
            'low': 'int',
            'open': 'int',
            'resolved': 'int',
            'avg_resolution_time': 'str',
        },
    },

    # ── Problem Management Register (ISO 20000-1 Clause 8.7.3) ─────────
    'Problem_Management_Register': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'problem_manager': 'str',
        'problems': [
            {
                'problem_id': 'str — e.g. PRB-001',
                'incident_refs': 'str — related incident IDs',
                'problem_summary': 'str',
                'root_cause': 'str',
                'workaround': 'str or None',
                'permanent_fix': 'str or None',
                'category': 'str — Infrastructure/Application/Process/Security/Third-Party',
                'priority': 'str — Low/Medium/High/Critical',
                'status': 'str — Identified/Under Investigation/Known Error/Resolved/Closed',
            },
        ],
        'summary': {
            'total_problems': 'int',
            'critical': 'int',
            'high': 'int',
            'medium': 'int',
            'low': 'int',
            'identified': 'int',
            'resolved': 'int',
        },
    },

    # ── Service Continuity Plan (ISO 20000-1 Clause 8.8.2) ──────────────
    'Service_Continuity_Plan': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'plan_owner': 'str',
        'last_review_date': 'str DD/MM/YYYY',
        'next_review_date': 'str DD/MM/YYYY',
        'services': [
            {
                'service_id': 'str — e.g. SCP-001',
                'service_name': 'str',
                'criticality': 'str — Critical/High/Medium/Low',
                'rto': 'str',
                'rpo': 'str',
                'recovery_strategy': 'str',
                'alternative_arrangements': 'str',
                'last_test_date': 'str DD/MM/YYYY',
                'test_result': 'str — Pass/Fail/Partial',
                'status': 'str — Ready/Needs Review/Remediation Required',
            },
        ],
        'summary': {
            'total_services': 'int',
            'ready': 'int',
            'needs_review': 'int',
            'remediation': 'int',
        },
    },

    # ── Availability Management Report (ISO 20000-1 Clause 8.8.3) ──────
    'Availability_Management_Report': {
        'client_name': 'str',
        'date': 'str DD/MM/YYYY',
        'standard': 'str',
        'report_owner': 'str',
        'reporting_period': 'str',
        'services': [
            {
                'service_id': 'str — e.g. AMR-001',
                'service_name': 'str',
                'target_availability': 'str — e.g. 99.9%',
                'actual_availability': 'str — e.g. 99.85%',
                'downtime_hours': 'str',
                'number_of_outages': 'int',
                'mtbf': 'str — Mean Time Between Failures',
                'mttr': 'str — Mean Time To Recover',
                'sla_breached': 'str — Yes/No',
                'notes': 'str',
            },
        ],
        'summary': {
            'total_services': 'int',
            'sla_met': 'int',
            'sla_breached': 'int',
            'overall_availability': 'str',
        },
    },
}


def build_document_data(doc_type: str, overrides: dict) -> dict:
    """Build a data dict for a document type with defaults filled in,
    merged with any overrides provided. Raises ValueError on unknown doc type."""
    contract = DOCUMENT_CONTRACTS.get(doc_type) or DOCUMENT_CONTRACTS.get({
        'Audit_Plan_Stage_1': 'Audit_Plan',
        'Audit_Plan_Stage_2': 'Audit_Plan',
    }.get(doc_type))

    if not contract:
        raise ValueError(f'Unknown document type: {doc_type}')

    result = {}
    for key, spec in contract.items():
        if key in overrides:
            result[key] = overrides[key]
        elif isinstance(spec, list) and spec:
            result[key] = []
        elif isinstance(spec, dict) and spec:
            inner = {}
            for k, v in spec.items():
                inner[k] = '' if isinstance(v, str) else ([] if isinstance(v, list) else {})
            result[key] = inner
        else:
            result[key] = ''
    result.update(overrides)
    return result
