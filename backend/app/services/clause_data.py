"""Clause database and helper functions for all supported ISO standards.
Provides HLS core clauses, standard-specific Clause 8 variants,
Annex A grouped controls, and framework section structures."""
import random
from datetime import datetime, timedelta


HLS_CORE = {
    '1': {
        'title': 'Scope',
        'sub_clauses': {},
        'evidence': [
            'Reviewed documented scope statement for applicability and exclusions',
            'Verified scope alignment with organizational context and interested party requirements',
            'Confirmed no unjustified exclusions that affect the organization\'s ability to achieve intended outcomes',
        ],
        'typical_findings': [
            'Scope exclusions not justified with documented rationale',
            'Scope statement missing reference to product/service categories',
        ],
    },
    '2': {
        'title': 'Normative References',
        'sub_clauses': {},
        'evidence': [
            'Verified availability of referenced normative documents',
            'Confirmed normative references are current applicable editions',
        ],
        'typical_findings': [
            'Outdated editions of referenced standards in use',
            'Referenced documents not accessible to relevant personnel',
        ],
    },
    '3': {
        'title': 'Terms and Definitions',
        'sub_clauses': {},
        'evidence': [
            'Verified organizational understanding of key terms as defined in the standard',
            'Confirmed terminology consistent across documented information',
            'Reviewed alignment of internal definitions with standard terminology',
        ],
        'typical_findings': [
            'Inconsistent use of terminology between different processes',
            'Organization-specific definitions not documented',
        ],
    },
    '4': {
        'title': 'Context of the Organization',
        'sub_clauses': {
            '4.1': {
                'title': 'Understanding the organization and its context',
                'audit_questions': [
                    'How does the organization determine external and internal issues relevant to its purpose?',
                    'How are interested parties identified and their requirements monitored?',
                ],
                'evidence_to_check': [
                    'Review of strategic planning documentation including PESTLE/SWOT analysis',
                    'Examination of interested party register with requirements traceability',
                ],
            },
            '4.2': {
                'title': 'Understanding the needs and expectations of interested parties',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '4.3': {
                'title': 'Determining the scope of the management system',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '4.4': {
                'title': 'Management system and its processes',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed external and internal issues register with PESTLE and SWOT analysis',
            'Examined interested party mapping with requirements traceability matrix',
            'Verified scope statement defining boundaries and applicability of the management system',
            'Assessed process interaction diagrams and sequence of processes',
            'Reviewed process KPIs and performance indicators for each identified process',
            'Confirmed criteria and methods for process operation and control are defined',
        ],
        'typical_findings': [
            'External issues identified but internal factors not systematically evaluated',
            'Interested party requirements not reviewed for changes periodically',
            'Process interactions not adequately documented leading to interface gaps',
        ],
    },
    '5': {
        'title': 'Leadership',
        'sub_clauses': {
            '5.1': {
                'title': 'Leadership and commitment',
                'audit_questions': [
                    'How does top management demonstrate leadership and commitment?',
                    'How is the quality/environmental/OH&S policy communicated and maintained?',
                ],
                'evidence_to_check': [
                    'Interview with top management on leadership involvement',
                    'Review of policy statements and communication records',
                ],
            },
            '5.1.1': {
                'title': 'General',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '5.2': {
                'title': 'Policy',
                'audit_questions': [
                    'How is the policy documented, approved, and communicated?',
                    'How is policy compliance monitored?',
                ],
                'evidence_to_check': [
                    'Review of approved policy document with version history',
                    'Examination of policy communication records',
                ],
            },
            '5.3': {
                'title': 'Roles, responsibilities and authorities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Interviewed top management on demonstrated leadership and commitment',
            'Reviewed policy statement for appropriateness to purpose and strategic direction',
            'Examined evidence of policy communication throughout the organization',
            'Verified defined roles and responsibilities with organization charts and job descriptions',
            'Reviewed management review minutes demonstrating active leadership involvement',
            'Confirmed resource allocation decisions documented and traceable to management',
            'Assessed accountability framework for management system performance',
        ],
        'typical_findings': [
            'Quality/Environmental/OH&S policy not communicated to all relevant parties',
            'Roles and responsibilities for management system not clearly defined',
            'Limited top management involvement evidenced in review records',
        ],
    },
    '6': {
        'title': 'Planning',
        'sub_clauses': {
            '6.1': {
                'title': 'Actions to address risks and opportunities',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            '6.2': {
                'title': 'Objectives and planning to achieve them',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '6.3': {
                'title': 'Planning of changes',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
        },
        'evidence': [
            'Reviewed risk and opportunity register with defined mitigation actions',
            'Examined objectives list with measurable KPIs and target dates',
            'Verified action plans for achieving objectives with assigned responsibilities',
            'Assessed change management process for planned changes to processes',
            'Reviewed emergency preparedness and response plans where applicable',
            'Confirmed integration of risk-based thinking into operational processes',
        ],
        'typical_findings': [
            'Risk assessment not updated following significant organizational changes',
            'Objectives not supported by detailed action plans with resource allocation',
            'Change management process not consistently applied for process modifications',
        ],
    },
    '7': {
        'title': 'Support',
        'sub_clauses': {
            '7.1': {
                'title': 'Resources',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '7.2': {
                'title': 'Competence',
                'audit_questions': [
                    'How is required competence determined for each role?',
                    'How is competence evaluated and records maintained?',
                ],
                'evidence_to_check': [
                    'Review of job descriptions and competence requirements',
                    'Examination of training records and effectiveness evaluation',
                ],
            },
            '7.3': {
                'title': 'Awareness',
                'audit_questions': [
                    'How does the organization ensure awareness of the policy?',
                    'How are employees made aware of their contribution to effectiveness?',
                ],
                'evidence_to_check': [
                    'Interview with personnel on policy awareness',
                    'Review of awareness training materials and attendance records',
                ],
            },
            '7.4': {
                'title': 'Communication',
                'audit_questions': [
                    'How is internal communication managed across levels?',
                    'How is external communication regulated?',
                ],
                'evidence_to_check': [
                    'Review of communication procedure and matrix',
                    'Examination of internal communication records and notice boards',
                ],
            },
            '7.5': {
                'title': 'Documented information',
                'audit_questions': [
                    'How is document control managed?',
                    'How are document changes approved and tracked?',
                ],
                'evidence_to_check': [
                    'Review of document control procedure',
                    'Examination of document approval and change records',
                ],
            },
        },
        'evidence': [
            'Reviewed resource allocation documentation including infrastructure and equipment',
            'Examined competence matrix with training records and qualification evidence',
            'Verified awareness programs demonstrating understanding of policy and objectives',
            'Assessed communication plan with defined channels and frequency',
            'Reviewed documented information control procedures including identification and storage',
            'Confirmed document approval and revision processes operating effectively',
            'Verified external document control including standards and regulatory documents',
        ],
        'typical_findings': [
            'Competence gaps identified but no training plan to address them',
            'Documented information retention periods not defined',
            'External communications not consistently logged or tracked',
        ],
    },
    '9': {
        'title': 'Performance Evaluation',
        'sub_clauses': {
            '9.1': {
                'title': 'Monitoring, measurement, analysis and evaluation',
                'audit_questions': [
                    'How does the organization monitor, measure, analyze, and evaluate performance?',
                    'How is the internal audit program planned and implemented?',
                ],
                'evidence_to_check': [
                    'Review of performance monitoring and measurement records',
                    'Examination of internal audit program and reports',
                ],
            },
            '9.1.1': {
                'title': 'General',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '9.2': {
                'title': 'Internal audit',
                'audit_questions': [
                    'How is the internal audit program planned?',
                    'How are auditors selected and their competence ensured?',
                ],
                'evidence_to_check': [
                    'Review of internal audit schedule and program',
                    'Examination of auditor qualification and selection records',
                ],
            },
            '9.3': {
                'title': 'Management review',
                'audit_questions': [
                    'How is the management review agenda determined?',
                    'What inputs and outputs are part of the management review?',
                ],
                'evidence_to_check': [
                    'Review of management review meeting minutes',
                    'Examination of action item tracking records',
                ],
            },
        },
        'evidence': [
            'Reviewed monitoring and measurement plan with defined performance indicators',
            'Examined internal audit program including schedule and completed audit reports',
            'Verified internal auditor competence and independence requirements',
            'Reviewed management review inputs including audit results and KPIs',
            'Assessed management review outputs for action items and resource decisions',
            'Confirmed data analysis methods used for evaluation of management system performance',
            'Verified compliance evaluation records for applicable legal and other requirements',
        ],
        'typical_findings': [
            'Internal audit findings not closed within defined timeframe',
            'Management review records lack detailed inputs on system performance',
            'Monitoring equipment calibration records not maintained',
        ],
    },
    '10': {
        'title': 'Improvement',
        'sub_clauses': {
            '10.1': {
                'title': 'Nonconformity and corrective action',
                'audit_questions': [
                    'How are nonconformities identified and documented?',
                    'How does the organization determine the root cause of nonconformities?',
                ],
                'evidence_to_check': [
                    'Review of nonconformity register and trend analysis',
                    'Examination of nonconformity investigation and root cause records',
                ],
            },
            '10.2': {
                'title': 'Continual improvement',
                'audit_questions': [
                    'How does the organization identify and act on nonconformities?',
                    'How is corrective action managed?',
                ],
                'evidence_to_check': [
                    'Review of nonconformity logs and corrective action records',
                    'Examination of continual improvement initiatives',
                ],
            },
        },
        'evidence': [
            'Reviewed nonconformity register with root cause analysis and corrective actions',
            'Examined corrective action effectiveness verification records',
            'Assessed continual improvement initiatives and their outcomes',
            'Reviewed trend analysis of nonconformities for systemic issues',
            'Verified lessons learned process contributing to management system improvement',
        ],
        'typical_findings': [
            'Root cause analysis not sufficiently deep for recurring nonconformities',
            'Corrective actions closed without evidence of effectiveness verification',
            'Continual improvement opportunities identified but not pursued',
        ],
    },
}


CLAUSE_8 = {
    'iso_9001': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Requirements for products and services',
                'sub_clauses': {
                    '8.2.1': {
                        'title': 'Customer communication',
                        'audit_questions': [
                            'How is internal communication managed across levels?',
                            'How is external communication regulated?',
                        ],
                        'evidence_to_check': [
                            'Review of communication procedure and matrix',
                            'Examination of internal communication records and notice boards',
                        ],
                    },
                    '8.2.2': {
                        'title': 'Determination of requirements for products and services',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                    '8.2.3': {
                        'title': 'Review of requirements for products and services',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                    '8.2.4': {
                        'title': 'Changes to requirements for products and services',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                },
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
            '8.3': {
                'title': 'Design and development of products and services',
                'sub_clauses': {
                    '8.3.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.3.2': {
                        'title': 'Design and development planning',
                        'audit_questions': [
                            'How does the organization identify risks and opportunities?',
                            'How are quality/environmental/OH&S objectives established and monitored?',
                        ],
                        'evidence_to_check': [
                            'Review of risk and opportunity register',
                            'Examination of objectives and plans to achieve them',
                        ],
                    },
                    '8.3.3': {
                        'title': 'Design and development inputs',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.3.4': {
                        'title': 'Design and development controls',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.3.5': {
                        'title': 'Design and development outputs',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.3.6': {
                        'title': 'Design and development changes',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                },
                'audit_questions': [
                    'How is the design and development process planned?',
                    'How are design inputs, outputs, and reviews managed?',
                ],
                'evidence_to_check': [
                    'Review of design and development procedure',
                    'Examination of design input/output/review/verification records',
                ],
            },
            '8.4': {
                'title': 'Control of externally provided processes, products and services',
                'sub_clauses': {
                    '8.4.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.4.2': {
                        'title': 'Type and extent of control',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.4.3': {
                        'title': 'Information for external providers',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
            '8.5': {
                'title': 'Production and service provision',
                'sub_clauses': {
                    '8.5.1': {
                        'title': 'Control of production and service provision',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                    '8.5.2': {
                        'title': 'Identification and traceability',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.3': {
                        'title': 'Property belonging to customers or external providers',
                        'audit_questions': [
                            'How are customer requirements determined and reviewed?',
                            'How is customer communication managed?',
                        ],
                        'evidence_to_check': [
                            'Review of customer requirement review procedure',
                            'Examination of customer communication records',
                        ],
                    },
                    '8.5.4': {
                        'title': 'Preservation',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.5': {
                        'title': 'Post-delivery activities',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.6': {
                        'title': 'Control of changes',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
            '8.6': {
                'title': 'Release of products and services',
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
            '8.7': {
                'title': 'Control of nonconforming outputs',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed production and service provision plans with defined control parameters',
            'Examined design and development records including design reviews and verification reports',
            'Assessed supplier evaluation and re-evaluation records for external providers',
            'Verified traceability system from raw material receipt through final product delivery',
            'Reviewed nonconforming output register with disposition decisions and approvals',
            'Examined customer communication records including inquiries, contracts, and feedback',
            'Verified post-delivery monitoring activities for applicable product categories',
        ],
        'typical_findings': [
            'Supplier re-evaluation not performed at defined intervals',
            'Design change records incomplete regarding authorization and impact assessment',
            'Customer property identification and protection not consistently applied',
        ],
    },
    'iso_14001': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Emergency preparedness and response',
                'audit_questions': [
                    'How does the organization identify potential emergency situations?',
                    'How are emergency response procedures tested and evaluated?',
                ],
                'evidence_to_check': [
                    'Review of emergency preparedness and response procedure',
                    'Examination of emergency drill records and lessons learned',
                ],
            },
        },
        'evidence': [
            'Reviewed operational control procedures for significant environmental aspects',
            'Examined emergency response plans and drill records for identified scenarios',
            'Verified waste management records including classification and disposal documentation',
            'Assessed emission monitoring data against regulatory limits',
            'Reviewed chemical management practices including storage and spill prevention',
            'Examined environmental operating criteria and process controls for key activities',
        ],
        'typical_findings': [
            'Emergency drill records lack evaluation of response effectiveness',
            'Operational controls not documented for outsourced processes with environmental impacts',
            'Waste disposal records missing for hazardous waste streams',
        ],
    },
    'iso_45001': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'sub_clauses': {
                    '8.1.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.1.2': {
                        'title': 'Eliminating hazards and reducing OH&S risks',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                    '8.1.3': {
                        'title': 'Management of change',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.1.4': {
                        'title': 'Procurement',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Emergency preparedness and response',
                'audit_questions': [
                    'How does the organization identify potential emergency situations?',
                    'How are emergency response procedures tested and evaluated?',
                ],
                'evidence_to_check': [
                    'Review of emergency preparedness and response procedure',
                    'Examination of emergency drill records and lessons learned',
                ],
            },
        },
        'evidence': [
            'Reviewed operational controls for OH&S risks including hierarchy of controls implementation',
            'Examined management of change process for facility and process modifications',
            'Verified contractor OH&S management requirements defined and monitored',
            'Assessed emergency response plans and exercise evaluation reports',
            'Reviewed procurement specifications including OH&S criteria for equipment and materials',
            'Examined workplace inspection records and hazard identification reports',
            'Verified personal protective equipment issuance and training records',
        ],
        'typical_findings': [
            'Hierarchy of controls not consistently applied in risk reduction measures',
            'Management of change assessments do not include OH&S impact evaluation',
            'Emergency equipment inspection records not maintained at required frequency',
        ],
    },
    'iso_50001': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
        },
        'evidence': [
            'Reviewed operational controls for significant energy uses and consumption drivers',
            'Examined energy performance indicators and baseline data management',
            'Verified operational criteria defined for processes affecting energy performance',
            'Assessed energy measurement and monitoring equipment calibration records',
            'Reviewed procurement specifications including energy efficiency criteria',
            'Examined maintenance schedules for energy-consuming equipment',
        ],
        'typical_findings': [
            'Energy baseline not re-established following significant operational changes',
            'Operational criteria for energy-consuming processes not documented',
            'Energy efficiency criteria not included in procurement specifications',
        ],
    },
    'iso_27001': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Information security risk assessment',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            '8.3': {
                'title': 'Information security risk treatment',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
        },
        'evidence': [
            'Reviewed information security risk assessment methodology and results',
            'Examined risk treatment plan with selected controls and implementation timeline',
            'Verified risk acceptance criteria and risk owner assignments',
            'Assessed statement of applicability for control selection justification',
            'Reviewed operational controls for information security processes',
            'Examined change management process for information security relevant changes',
            'Verified effectiveness monitoring of implemented security controls',
        ],
        'typical_findings': [
            'Risk assessment does not include all information assets and their classifications',
            'Risk treatment plan lacking target dates and responsible parties',
            'Statement of applicability not reviewed for continued relevance',
        ],
    },
    'iso_20000': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Service management system',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.3': {
                'title': 'Service portfolio management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.4': {
                'title': 'Relationship and agreement management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.5': {
                'title': 'Supply and demand management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.6': {
                'title': 'Service design, build and transition',
                'audit_questions': [
                    'How is the design and development process planned?',
                    'How are design inputs, outputs, and reviews managed?',
                ],
                'evidence_to_check': [
                    'Review of design and development procedure',
                    'Examination of design input/output/review/verification records',
                ],
            },
            '8.7': {
                'title': 'Resolution and fulfilment',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.8': {
                'title': 'Service assurance',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed service portfolio and service catalogue documentation',
            'Examined service level agreements and supporting agreements with external providers',
            'Verified capacity management reports against demand forecasts',
            'Assessed incident and service request management process records',
            'Reviewed change management documentation including CAB minutes and impact assessments',
            'Examined release and deployment management records for successful transitions',
            'Verified business relationship management activities and customer satisfaction data',
            'Assessed service continuity and availability management plans and test results',
        ],
        'typical_findings': [
            'Service level agreement performance not monitored against targets',
            'Change management records missing risk and impact assessments',
            'Capacity plans not aligned with forecast demand changes',
        ],
    },
    'iso_22301': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Business continuity analysis',
                'sub_clauses': {
                    '8.2.1': {
                        'title': 'Business impact analysis',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.2.2': {
                        'title': 'Risk assessment',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                },
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.3': {
                'title': 'Business continuity strategies and solutions',
                'sub_clauses': {
                    '8.3.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.3.2': {
                        'title': 'Identification of strategies and solutions',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.3.3': {
                        'title': 'Selection of strategies and solutions',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.4': {
                'title': 'Business continuity plans and procedures',
                'sub_clauses': {
                    '8.4.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.4.2': {
                        'title': 'Incident response structure',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.4.3': {
                        'title': 'Warning and communication',
                        'audit_questions': [
                            'How is internal communication managed across levels?',
                            'How is external communication regulated?',
                        ],
                        'evidence_to_check': [
                            'Review of communication procedure and matrix',
                            'Examination of internal communication records and notice boards',
                        ],
                    },
                    '8.4.4': {
                        'title': 'Business continuity plans',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.4.5': {
                        'title': 'Recovery procedures',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.5': {
                'title': 'Exercise and testing',
                'sub_clauses': {
                    '8.5.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.2': {
                        'title': 'Exercise programmes',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.3': {
                        'title': 'Testing of continuity solutions',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed business impact analysis with validated RTO and RPO for critical activities',
            'Examined risk assessment documentation for disruptive incident scenarios',
            'Verified business continuity strategies align with BIA findings and risk appetite',
            'Assessed business continuity plans for completeness and accessibility',
            'Reviewed exercise and test records including debrief reports and improvement actions',
            'Examined incident response structure and crisis team roles and responsibilities',
            'Verified communication procedures for internal and external stakeholders during incidents',
        ],
        'typical_findings': [
            'Business impact analysis not updated following organizational restructuring',
            'Exercise after-action reports do not include corrective action tracking',
            'Business continuity plans not tested at defined frequency',
        ],
    },
    'iso_37301': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Establishing controls and procedures',
                'sub_clauses': {
                    '8.2.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.2.2': {
                        'title': 'Controls and procedures for compliance obligations',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.2.3': {
                        'title': 'Controls and procedures for persons',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.2.4': {
                        'title': 'Controls and procedures for outsourced processes',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.3': {
                'title': 'Reporting concerns',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.4': {
                'title': 'Investigation process',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed compliance obligation register and control mapping documentation',
            'Examined whistleblowing and reporting concern mechanisms including confidentiality provisions',
            'Verified investigation process records including timelines and outcome documentation',
            'Assessed due diligence procedures for third parties and business partners',
            'Reviewed compliance training records and awareness programme effectiveness',
            'Examined delegation of authority framework and approval matrices',
            'Verified monitoring of outsourced processes for compliance with obligations',
        ],
        'typical_findings': [
            'Compliance obligation register not reviewed for changes in regulatory requirements',
            'Whistleblowing channel usage not monitored for trend analysis',
            'Investigation reports lack root cause analysis and preventive recommendations',
        ],
    },
    'iso_42001': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'AI risk assessment',
                'sub_clauses': {
                    '8.2.1': {
                        'title': 'AI risk assessment process',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                    '8.2.2': {
                        'title': 'AI risk assessment criteria',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                    '8.2.3': {
                        'title': 'AI risk acceptance',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                },
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            '8.3': {
                'title': 'AI risk treatment',
                'sub_clauses': {
                    '8.3.1': {
                        'title': 'AI risk treatment plan',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                    '8.3.2': {
                        'title': 'AI risk treatment implementation',
                        'audit_questions': [
                            'How does the organization conduct risk assessment?',
                            'How are risk treatment options evaluated and selected?',
                        ],
                        'evidence_to_check': [
                            'Review of risk assessment methodology and criteria',
                            'Examination of risk register and treatment plans',
                        ],
                    },
                },
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
        },
        'evidence': [
            'Reviewed AI risk assessment methodology including bias and transparency evaluation',
            'Examined AI system inventory with impact classification for each system',
            'Verified AI risk treatment plans with defined controls and residual risk acceptance',
            'Assessed AI system development lifecycle controls and testing records',
            'Reviewed AI training data governance including data quality and provenance documentation',
            'Examined AI output quality monitoring and performance metrics against defined thresholds',
            'Verified transparency and explainability measures for AI-driven decisions',
        ],
        'typical_findings': [
            'AI risk assessment does not address potential bias in training data',
            'AI system inventory incomplete regarding shadow AI deployments',
            'Transparency documentation lacking for AI decision-making processes',
        ],
    },
    'iso_30401': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Knowledge development',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.3': {
                'title': 'Knowledge transfer and conversion',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.4': {
                'title': 'Knowledge retention and preservation',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.5': {
                'title': 'Knowledge sharing and access',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed knowledge management strategy and alignment with organizational objectives',
            'Examined knowledge capture processes for tacit-to-explicit knowledge conversion',
            'Verified knowledge retention practices including departure and retirement processes',
            'Assessed knowledge sharing platforms and their accessibility to relevant personnel',
            'Reviewed communities of practice and lessons learned session records',
            'Examined knowledge mapping outputs and identified knowledge gaps',
            'Verified protection of critical organizational knowledge including IP and trade secrets',
        ],
        'typical_findings': [
            'Knowledge retention not addressed in employee exit processes',
            'Knowledge sharing culture not supported by adequate technology platforms',
            'Critical knowledge gaps identified but no action plan to address them',
        ],
    },
    'iso_27701': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Privacy risk assessment',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            '8.3': {
                'title': 'Privacy risk treatment',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            '8.4': {
                'title': 'Data subject rights management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.5': {
                'title': 'Data breach management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.6': {
                'title': 'Privacy by design and default',
                'audit_questions': [
                    'How is the design and development process planned?',
                    'How are design inputs, outputs, and reviews managed?',
                ],
                'evidence_to_check': [
                    'Review of design and development procedure',
                    'Examination of design input/output/review/verification records',
                ],
            },
        },
        'evidence': [
            'Reviewed privacy risk assessment including data protection impact assessments',
            'Examined data subject rights request handling process and response time records',
            'Verified data breach detection and notification procedures against regulatory timelines',
            'Assessed privacy by design controls integrated into system development lifecycle',
            'Reviewed consent management records and withdrawal mechanisms',
            'Examined records of processing activities (ROPA) for completeness and accuracy',
            'Verified cross-border data transfer mechanisms and adequacy decisions documentation',
        ],
        'typical_findings': [
            'Data subject rights request procedure does not cover all rights (e.g. erasure, portability)',
            'DPIAs not conducted for high-risk processing activities as required',
            'Data breach notification timeline not aligned with regulatory requirements',
        ],
    },
    'iso_13485': {
        'title': 'Operation',
        'sub_clauses': {
            '8.1': {
                'title': 'Operational planning and control',
                'sub_clauses': {
                    '8.1.1': {
                        'title': 'General',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.1.2': {
                        'title': 'Validation of processes for production and service provision',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                    '8.1.3': {
                        'title': 'Control of production and service provision',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                },
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '8.2': {
                'title': 'Design and development',
                'sub_clauses': {
                    '8.2.1': {
                        'title': 'Design and development planning',
                        'audit_questions': [
                            'How does the organization identify risks and opportunities?',
                            'How are quality/environmental/OH&S objectives established and monitored?',
                        ],
                        'evidence_to_check': [
                            'Review of risk and opportunity register',
                            'Examination of objectives and plans to achieve them',
                        ],
                    },
                    '8.2.2': {
                        'title': 'Design and development inputs',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.3': {
                        'title': 'Design and development outputs',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.4': {
                        'title': 'Design and development review',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.5': {
                        'title': 'Design and development verification',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.6': {
                        'title': 'Design and development validation',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.7': {
                        'title': 'Design and development transfer',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.8': {
                        'title': 'Control of design and development changes',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                    '8.2.9': {
                        'title': 'Design and development files',
                        'audit_questions': [
                            'How is the design and development process planned?',
                            'How are design inputs, outputs, and reviews managed?',
                        ],
                        'evidence_to_check': [
                            'Review of design and development procedure',
                            'Examination of design input/output/review/verification records',
                        ],
                    },
                },
                'audit_questions': [
                    'How is the design and development process planned?',
                    'How are design inputs, outputs, and reviews managed?',
                ],
                'evidence_to_check': [
                    'Review of design and development procedure',
                    'Examination of design input/output/review/verification records',
                ],
            },
            '8.3': {
                'title': 'Purchasing',
                'sub_clauses': {
                    '8.3.1': {
                        'title': 'Purchasing process',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.3.2': {
                        'title': 'Purchasing information',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.3.3': {
                        'title': 'Verification of purchased product',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                },
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '8.4': {
                'title': 'Customer communication',
                'audit_questions': [
                    'How is internal communication managed across levels?',
                    'How is external communication regulated?',
                ],
                'evidence_to_check': [
                    'Review of communication procedure and matrix',
                    'Examination of internal communication records and notice boards',
                ],
            },
            '8.5': {
                'title': 'Control of production and service provision',
                'sub_clauses': {
                    '8.5.1': {
                        'title': 'Control of production and service provision',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                    '8.5.2': {
                        'title': 'Cleanliness and contamination control',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.3': {
                        'title': 'Installation and servicing activities',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.4': {
                        'title': 'Sterilization process validation',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.5': {
                        'title': 'Identification and traceability',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                    '8.5.6': {
                        'title': 'Property belonging to customers or external providers',
                        'audit_questions': [
                            'How are customer requirements determined and reviewed?',
                            'How is customer communication managed?',
                        ],
                        'evidence_to_check': [
                            'Review of customer requirement review procedure',
                            'Examination of customer communication records',
                        ],
                    },
                    '8.5.7': {
                        'title': 'Preservation of product',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                },
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
            '8.6': {
                'title': 'Control of monitoring and measuring equipment',
                'audit_questions': [
                    'How are monitoring and measurement activities defined?',
                    'What monitoring equipment is used and how is it calibrated?',
                ],
                'evidence_to_check': [
                    'Review of monitoring and measurement equipment calibration records',
                    'Examination of monitoring plans and reports',
                ],
            },
            '8.7': {
                'title': 'Nonconforming product',
                'sub_clauses': {
                    '8.7.1': {
                        'title': 'Nonconforming product control',
                        'audit_questions': [
                            'How is product/service acceptance criteria defined?',
                            'How is product traceability managed?',
                        ],
                        'evidence_to_check': [
                            'Review of product acceptance criteria and inspection records',
                            'Examination of traceability records',
                        ],
                    },
                    '8.7.2': {
                        'title': 'Rework',
                        'audit_questions': [
                            'What evidence demonstrates compliance with this clause?',
                            'How does the organization address each requirement of this clause?',
                        ],
                        'evidence_to_check': [
                            'Review of documented evidence of compliance with contractual requirements',
                            'Examination of applicable regulatory permits and approvals',
                        ],
                    },
                },
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
        },
        'evidence': [
            'Reviewed design and development files for compliance with ISO 13485 requirements',
            'Examined validation records for production and sterilization processes',
            'Verified traceability system for medical device identification',
            'Assessed purchasing controls and supplier qualification records',
            'Reviewed monitoring and measuring equipment calibration records',
            'Examined nonconforming product disposition and rework authorization records',
            'Verified customer communication records including complaint handling',
        ],
        'typical_findings': [
            'Design validation records incomplete regarding clinical evaluation',
            'Sterilization process validation not revalidated after equipment change',
            'Supplier qualification records missing for critical component providers',
            'Customer complaint handling process does not meet regulatory reporting timelines',
        ],
    },
}


ANNEX_A_27001 = {
    'A.5': {
        'title': 'Organizational Controls (37 controls)',
        'sub_clauses': {
            'A.5.1': {
                'title': 'Information security policies and procedures',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.2': {
                'title': 'Information security roles and responsibilities',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.3': {
                'title': 'Segregation of duties',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.4': {
                'title': 'Management responsibilities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.5': {
                'title': 'Contact with authorities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.6': {
                'title': 'Contact with special interest groups',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.7': {
                'title': 'Threat intelligence',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.8': {
                'title': 'Information security in project management',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.9': {
                'title': 'Inventory of information and other associated assets',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.10': {
                'title': 'Acceptable use of information and other associated assets',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.11': {
                'title': 'Return of assets',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.12': {
                'title': 'Classification of information',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.13': {
                'title': 'Labelling of information',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.14': {
                'title': 'Information transfer',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.15': {
                'title': 'Access control',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.16': {
                'title': 'Identity management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.17': {
                'title': 'Authentication information',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.18': {
                'title': 'Access rights',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.19': {
                'title': 'Information security in supplier relationships',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.20': {
                'title': 'Addressing information security within supplier agreements',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.21': {
                'title': 'Managing information security in the ICT supply chain',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.22': {
                'title': 'Monitoring review and change management of supplier services',
                'audit_questions': [
                    'How are suppliers evaluated and selected?',
                    'How is supplier performance monitored?',
                ],
                'evidence_to_check': [
                    'Review of supplier evaluation and selection criteria',
                    'Examination of approved supplier list',
                ],
            },
            'A.5.23': {
                'title': 'Information security for use of cloud services',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.24': {
                'title': 'Information security incident management planning and preparation',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            'A.5.25': {
                'title': 'Assessment and decision on information security events',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.26': {
                'title': 'Response to information security incidents',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.27': {
                'title': 'Learning from information security incidents',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.28': {
                'title': 'Collection of evidence',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.29': {
                'title': 'Information security during disruption',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.30': {
                'title': 'ICT readiness for business continuity',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.31': {
                'title': 'Legal statutory regulatory and contractual requirements',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.32': {
                'title': 'Intellectual property rights',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.33': {
                'title': 'Protection of records',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.34': {
                'title': 'Privacy and protection of PII',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.35': {
                'title': 'Independent review of information security',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.5.36': {
                'title': 'Compliance with policies and standards',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.5.37': {
                'title': 'Documented operating procedures',
                'audit_questions': [
                    'How is document control managed?',
                    'How are document changes approved and tracked?',
                ],
                'evidence_to_check': [
                    'Review of document control procedure',
                    'Examination of document approval and change records',
                ],
            },
        },
        'evidence': [
            'Reviewed information security policy approvals and review cycles',
            'Examined RACI matrix for information security roles and responsibilities',
            'Verified supplier security assessments and cloud service security reviews',
            'Assessed incident response plans and lessons learned documentation',
            'Reviewed access control policy enforcement and recertification records',
        ],
    },
    'A.6': {
        'title': 'People Controls (8 controls)',
        'sub_clauses': {
            'A.6.1': {
                'title': 'Screening',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.6.2': {
                'title': 'Terms and conditions of employment',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.6.3': {
                'title': 'Information security awareness education and training',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
            'A.6.4': {
                'title': 'Disciplinary process',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.6.5': {
                'title': 'Responsibilities after termination or change of employment',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.6.6': {
                'title': 'Confidentiality or non-disclosure agreements',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.6.7': {
                'title': 'Remote working',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.6.8': {
                'title': 'Information security event reporting',
                'audit_questions': [
                    'How are information security policies established and reviewed?',
                    'How is information security risk assessment conducted?',
                ],
                'evidence_to_check': [
                    'Review of information security policy and procedures',
                    'Examination of risk assessment and treatment documentation',
                ],
            },
        },
        'evidence': [
            'Reviewed background screening policy and records for applicable roles',
            'Examined information security awareness programme content and completion records',
            'Verified non-disclosure agreement execution and tracking',
            'Assessed remote working security controls and end-user compliance',
        ],
    },
    'A.7': {
        'title': 'Physical Controls (14 controls)',
        'sub_clauses': {
            'A.7.1': {
                'title': 'Physical security perimeters',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.2': {
                'title': 'Physical entry controls',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.3': {
                'title': 'Securing offices rooms and facilities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.4': {
                'title': 'Physical security monitoring',
                'audit_questions': [
                    'How are monitoring and measurement activities defined?',
                    'What monitoring equipment is used and how is it calibrated?',
                ],
                'evidence_to_check': [
                    'Review of monitoring and measurement equipment calibration records',
                    'Examination of monitoring plans and reports',
                ],
            },
            'A.7.5': {
                'title': 'Protection against physical and environmental threats',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.6': {
                'title': 'Working in secure areas',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.7': {
                'title': 'Clear desk and clear screen',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.8': {
                'title': 'Equipment siting and protection',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.9': {
                'title': 'Security of assets off-premises',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.10': {
                'title': 'Storage media',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.11': {
                'title': 'Supporting utilities',
                'audit_questions': [
                    'How are resources needed for the management system determined and provided?',
                    'How is competence of personnel ensured?',
                ],
                'evidence_to_check': [
                    'Review of resource allocation documentation',
                    'Examination of training records and competence matrices',
                ],
            },
            'A.7.12': {
                'title': 'Cabling security',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.13': {
                'title': 'Equipment maintenance',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.7.14': {
                'title': 'Secure disposal or re-use of equipment',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed physical security perimeter controls including access control system logs',
            'Examined visitor management records and escort procedures',
            'Verified clear desk and clear screen compliance through periodic inspections',
            'Assessed media sanitization and secure disposal procedures and records',
        ],
    },
    'A.8': {
        'title': 'Technological Controls (34 controls)',
        'sub_clauses': {
            'A.8.1': {
                'title': 'User endpoint devices',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.2': {
                'title': 'Privileged access rights',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.3': {
                'title': 'Information access restriction',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.4': {
                'title': 'Access to source code',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.5': {
                'title': 'Secure authentication',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.6': {
                'title': 'Capacity management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.7': {
                'title': 'Protection against malware',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.8': {
                'title': 'Management of technical vulnerabilities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.9': {
                'title': 'Configuration management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.10': {
                'title': 'Information deletion',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.11': {
                'title': 'Data masking',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.12': {
                'title': 'Data leakage prevention',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.13': {
                'title': 'Information backup',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.14': {
                'title': 'Redundancy of information processing facilities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.15': {
                'title': 'Logging',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.16': {
                'title': 'Monitoring activities',
                'audit_questions': [
                    'How are monitoring and measurement activities defined?',
                    'What monitoring equipment is used and how is it calibrated?',
                ],
                'evidence_to_check': [
                    'Review of monitoring and measurement equipment calibration records',
                    'Examination of monitoring plans and reports',
                ],
            },
            'A.8.17': {
                'title': 'Clock synchronization',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.18': {
                'title': 'Use of privileged utility programs',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.19': {
                'title': 'Installation of software on operational systems',
                'audit_questions': [
                    'How are operational processes planned, implemented, and controlled?',
                    'What criteria are in place for accepting products and services?',
                ],
                'evidence_to_check': [
                    'Observation of operational processes in execution',
                    'Review of operational planning and control documentation',
                ],
            },
            'A.8.20': {
                'title': 'Networks security',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.21': {
                'title': 'Security of network services',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.22': {
                'title': 'Segregation of networks',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.23': {
                'title': 'Web filtering',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.24': {
                'title': 'Use of cryptography',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.25': {
                'title': 'Secure development lifecycle',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.26': {
                'title': 'Application security requirements',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.27': {
                'title': 'Secure system architecture and engineering principles',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.28': {
                'title': 'Secure coding',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.29': {
                'title': 'Security testing in development and acceptance',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.30': {
                'title': 'Outsourced development',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.31': {
                'title': 'Separation of development test and production environments',
                'audit_questions': [
                    'How is product/service acceptance criteria defined?',
                    'How is product traceability managed?',
                ],
                'evidence_to_check': [
                    'Review of product acceptance criteria and inspection records',
                    'Examination of traceability records',
                ],
            },
            'A.8.32': {
                'title': 'Change management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.33': {
                'title': 'Test information',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.8.34': {
                'title': 'Protection of information systems during audit testing',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed vulnerability management reports and patching compliance records',
            'Examined access control reviews including privileged account recertification',
            'Verified backup procedures including restoration test results',
            'Assessed network security controls including firewall rules and segmentation',
            'Reviewed secure coding standards and application security testing results',
            'Examined cryptographic controls including key management procedures',
        ],
    },
}


ANNEX_A_42001 = {
    'A.9.1': {
        'title': 'AI Policy (4 controls)',
        'sub_clauses': {
            'A.9.1.1': {
                'title': 'AI policy framework',
                'audit_questions': [
                    'How is the policy documented, approved, and communicated?',
                    'How is policy compliance monitored?',
                ],
                'evidence_to_check': [
                    'Review of approved policy document with version history',
                    'Examination of policy communication records',
                ],
            },
            'A.9.1.2': {
                'title': 'AI governance roles and responsibilities',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.1.3': {
                'title': 'AI policy communication',
                'audit_questions': [
                    'How is the policy documented, approved, and communicated?',
                    'How is policy compliance monitored?',
                ],
                'evidence_to_check': [
                    'Review of approved policy document with version history',
                    'Examination of policy communication records',
                ],
            },
            'A.9.1.4': {
                'title': 'AI resource allocation',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed AI policy framework covering ethical principles and governance requirements',
            'Examined AI governance structure with defined accountability for AI systems',
        ],
    },
    'A.9.2': {
        'title': 'AI System Lifecycle (8 controls)',
        'sub_clauses': {
            'A.9.2.1': {
                'title': 'AI system planning and design',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            'A.9.2.2': {
                'title': 'AI system development methodology',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.2.3': {
                'title': 'Data acquisition and preparation',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.2.4': {
                'title': 'Model training and validation',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.2.5': {
                'title': 'Model testing and evaluation',
                'audit_questions': [
                    'How does the organization monitor, measure, analyze, and evaluate performance?',
                    'How is the internal audit program planned and implemented?',
                ],
                'evidence_to_check': [
                    'Review of performance monitoring and measurement records',
                    'Examination of internal audit program and reports',
                ],
            },
            'A.9.2.6': {
                'title': 'AI system deployment',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.2.7': {
                'title': 'AI system operation and monitoring',
                'audit_questions': [
                    'How are operational processes planned, implemented, and controlled?',
                    'What criteria are in place for accepting products and services?',
                ],
                'evidence_to_check': [
                    'Observation of operational processes in execution',
                    'Review of operational planning and control documentation',
                ],
            },
            'A.9.2.8': {
                'title': 'AI system retirement',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed AI system lifecycle procedures covering development through retirement',
            'Examined model validation reports and test coverage for edge cases',
            'Verified monitoring dashboards for AI system performance drift detection',
        ],
    },
    'A.9.3': {
        'title': 'AI Risk Management (6 controls)',
        'sub_clauses': {
            'A.9.3.1': {
                'title': 'AI risk assessment process',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            'A.9.3.2': {
                'title': 'AI risk criteria and acceptance levels',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            'A.9.3.3': {
                'title': 'AI risk treatment planning',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            'A.9.3.4': {
                'title': 'AI risk monitoring and review',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            'A.9.3.5': {
                'title': 'AI residual risk acceptance',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            'A.9.3.6': {
                'title': 'AI risk register maintenance',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
        },
        'evidence': [
            'Reviewed AI risk register covering all operational AI systems',
            'Examined risk acceptance documentation for high-risk AI systems',
            'Verified risk monitoring frequency against defined risk review schedule',
        ],
    },
    'A.9.4': {
        'title': 'AI Data Management (5 controls)',
        'sub_clauses': {
            'A.9.4.1': {
                'title': 'Data quality management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.4.2': {
                'title': 'Data provenance and lineage',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.4.3': {
                'title': 'Training data governance',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.4.4': {
                'title': 'Data bias detection and mitigation',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.4.5': {
                'title': 'Data retention and disposal',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed data quality metrics and monitoring reports for training datasets',
            'Examined data lineage documentation from collection through model consumption',
            'Assessed bias detection methods and mitigation outcomes for sensitive attributes',
        ],
    },
    'A.9.5': {
        'title': 'AI Transparency and Explainability (4 controls)',
        'sub_clauses': {
            'A.9.5.1': {
                'title': 'AI system documentation',
                'audit_questions': [
                    'How is document control managed?',
                    'How are document changes approved and tracked?',
                ],
                'evidence_to_check': [
                    'Review of document control procedure',
                    'Examination of document approval and change records',
                ],
            },
            'A.9.5.2': {
                'title': 'Explainability requirements',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.5.3': {
                'title': 'AI system output labelling',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.5.4': {
                'title': 'Stakeholder communication',
                'audit_questions': [
                    'How is internal communication managed across levels?',
                    'How is external communication regulated?',
                ],
                'evidence_to_check': [
                    'Review of communication procedure and matrix',
                    'Examination of internal communication records and notice boards',
                ],
            },
        },
        'evidence': [
            'Reviewed AI system documentation including purpose scope and limitations',
            'Examined explainability methods applied to AI system decision-making processes',
            'Verified AI output labelling conforms to applicable regulatory requirements',
        ],
    },
    'A.9.6': {
        'title': 'AI Fairness and Non-Discrimination (3 controls)',
        'sub_clauses': {
            'A.9.6.1': {
                'title': 'Fairness assessment',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.6.2': {
                'title': 'Discrimination monitoring',
                'audit_questions': [
                    'How are monitoring and measurement activities defined?',
                    'What monitoring equipment is used and how is it calibrated?',
                ],
                'evidence_to_check': [
                    'Review of monitoring and measurement equipment calibration records',
                    'Examination of monitoring plans and reports',
                ],
            },
            'A.9.6.3': {
                'title': 'Remediation of unfair outcomes',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed fairness metrics and assessment results across demographic groups',
            'Examined discrimination monitoring reports including protected attribute analysis',
            'Verified remediation procedures for identified unfair AI outcomes',
        ],
    },
    'A.9.7': {
        'title': 'AI Security and Safety (4 controls)',
        'sub_clauses': {
            'A.9.7.1': {
                'title': 'AI system security controls',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.7.2': {
                'title': 'Adversarial attack protection',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.7.3': {
                'title': 'AI system safety testing',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.7.4': {
                'title': 'AI incident response',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed AI-specific security controls including model poisoning protections',
            'Examined adversarial robustness testing results and attack surface analysis',
            'Verified AI incident response procedures integrated with organizational IR plan',
        ],
    },
    'A.9.8': {
        'title': 'AI Impact Assessment (3 controls)',
        'sub_clauses': {
            'A.9.8.1': {
                'title': 'AI impact assessment process',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.8.2': {
                'title': 'Societal impact evaluation',
                'audit_questions': [
                    'How does the organization monitor, measure, analyze, and evaluate performance?',
                    'How is the internal audit program planned and implemented?',
                ],
                'evidence_to_check': [
                    'Review of performance monitoring and measurement records',
                    'Examination of internal audit program and reports',
                ],
            },
            'A.9.8.3': {
                'title': 'Environmental impact of AI systems',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed AI impact assessment reports for high-risk AI systems',
            'Examined societal impact assessments including stakeholder consultation records',
            'Verified environmental impact monitoring for compute-intensive AI workloads',
        ],
    },
    'A.9.9': {
        'title': 'AI Third-Party and Supply Chain (3 controls)',
        'sub_clauses': {
            'A.9.9.1': {
                'title': 'Third-party AI system oversight',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            'A.9.9.2': {
                'title': 'AI supply chain risk assessment',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            'A.9.9.3': {
                'title': 'Open-source AI component management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed third-party AI system assessment and approval documentation',
            'Examined AI supply chain risk assessments including dependency analysis',
            'Verified open-source AI component inventory and license compliance checks',
        ],
    },
}


PIMS_27701 = {
    '5': {
        'title': 'Leadership and Accountability',
        'sub_clauses': {
            '5.1': {
                'title': 'Privacy leadership and commitment',
                'audit_questions': [
                    'How does top management demonstrate leadership and commitment?',
                    'How is the quality/environmental/OH&S policy communicated and maintained?',
                ],
                'evidence_to_check': [
                    'Interview with top management on leadership involvement',
                    'Review of policy statements and communication records',
                ],
            },
            '5.2': {
                'title': 'Privacy policy',
                'audit_questions': [
                    'How is the policy documented, approved, and communicated?',
                    'How is policy compliance monitored?',
                ],
                'evidence_to_check': [
                    'Review of approved policy document with version history',
                    'Examination of policy communication records',
                ],
            },
            '5.3': {
                'title': 'Privacy roles and responsibilities including DPO',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Interviewed DPO on independence reporting line and resource adequacy',
            'Reviewed privacy policy approval and communication records',
            'Examined privacy RACI matrix covering all PII processing activities',
        ],
    },
    '6': {
        'title': 'Planning for the Privacy Information Management System',
        'sub_clauses': {
            '6.1': {
                'title': 'Actions to address privacy risks and opportunities',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            '6.2': {
                'title': 'Privacy objectives and planning',
                'audit_questions': [
                    'How does the organization identify risks and opportunities?',
                    'How are quality/environmental/OH&S objectives established and monitored?',
                ],
                'evidence_to_check': [
                    'Review of risk and opportunity register',
                    'Examination of objectives and plans to achieve them',
                ],
            },
            '6.3': {
                'title': 'Privacy risk assessment methodology',
                'audit_questions': [
                    'How does the organization conduct risk assessment?',
                    'How are risk treatment options evaluated and selected?',
                ],
                'evidence_to_check': [
                    'Review of risk assessment methodology and criteria',
                    'Examination of risk register and treatment plans',
                ],
            },
            '6.4': {
                'title': 'Legal and regulatory requirements register',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed privacy risk assessment methodology aligned with ISO 29134 guidelines',
            'Examined privacy objectives with measurable targets and tracking',
            'Verified legal register covering all applicable privacy regulations',
        ],
    },
    '7': {
        'title': 'Support for the Privacy Information Management System',
        'sub_clauses': {
            '7.1': {
                'title': 'Resources for privacy management',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
            '7.2': {
                'title': 'Privacy competence and training',
                'audit_questions': [
                    'How is required competence determined for each role?',
                    'How is competence evaluated and records maintained?',
                ],
                'evidence_to_check': [
                    'Review of job descriptions and competence requirements',
                    'Examination of training records and effectiveness evaluation',
                ],
            },
            '7.3': {
                'title': 'Privacy awareness',
                'audit_questions': [
                    'How does the organization ensure awareness of the policy?',
                    'How are employees made aware of their contribution to effectiveness?',
                ],
                'evidence_to_check': [
                    'Interview with personnel on policy awareness',
                    'Review of awareness training materials and attendance records',
                ],
            },
            '7.4': {
                'title': 'Privacy communication',
                'audit_questions': [
                    'How is internal communication managed across levels?',
                    'How is external communication regulated?',
                ],
                'evidence_to_check': [
                    'Review of communication procedure and matrix',
                    'Examination of internal communication records and notice boards',
                ],
            },
            '7.5': {
                'title': 'Documented information for privacy',
                'audit_questions': [
                    'How is document control managed?',
                    'How are document changes approved and tracked?',
                ],
                'evidence_to_check': [
                    'Review of document control procedure',
                    'Examination of document approval and change records',
                ],
            },
            '7.6': {
                'title': 'Records of processing activities (ROPA)',
                'audit_questions': [
                    'What evidence demonstrates compliance with this clause?',
                    'How does the organization address each requirement of this clause?',
                ],
                'evidence_to_check': [
                    'Review of documented evidence of compliance with contractual requirements',
                    'Examination of applicable regulatory permits and approvals',
                ],
            },
        },
        'evidence': [
            'Reviewed ROPA completeness across all business functions and systems',
            'Examined privacy training completion rates and competence assessments',
            'Verified privacy notice distribution and transparency documentation',
        ],
    },
    '9': {
        'title': 'Performance Evaluation of the PIMS',
        'sub_clauses': {
            '9.1': {
                'title': 'Privacy monitoring and measurement',
                'audit_questions': [
                    'How are monitoring and measurement activities defined?',
                    'What monitoring equipment is used and how is it calibrated?',
                ],
                'evidence_to_check': [
                    'Review of monitoring and measurement equipment calibration records',
                    'Examination of monitoring plans and reports',
                ],
            },
            '9.2': {
                'title': 'Internal audit of PIMS',
                'audit_questions': [
                    'How is the internal audit program planned?',
                    'How are auditors selected and their competence ensured?',
                ],
                'evidence_to_check': [
                    'Review of internal audit schedule and program',
                    'Examination of auditor qualification and selection records',
                ],
            },
            '9.3': {
                'title': 'Management review of PIMS',
                'audit_questions': [
                    'How is the management review agenda determined?',
                    'What inputs and outputs are part of the management review?',
                ],
                'evidence_to_check': [
                    'Review of management review meeting minutes',
                    'Examination of action item tracking records',
                ],
            },
        },
        'evidence': [
            'Reviewed privacy KPI reports including data subject request metrics',
            'Examined PIMS internal audit reports and findings closure records',
            'Verified management review minutes addressing privacy performance',
        ],
    },
    '10': {
        'title': 'Improvement of the PIMS',
        'sub_clauses': {
            '10.1': {
                'title': 'Privacy nonconformities and corrective actions',
                'audit_questions': [
                    'How does the organization initiate corrective action?',
                    'How is the effectiveness of corrective actions evaluated?',
                ],
                'evidence_to_check': [
                    'Review of corrective action procedure',
                    'Examination of corrective action records and effectiveness verification',
                ],
            },
            '10.2': {
                'title': 'Continual improvement of PIMS',
                'audit_questions': [
                    'How does the organization identify and act on nonconformities?',
                    'How is corrective action managed?',
                ],
                'evidence_to_check': [
                    'Review of nonconformity logs and corrective action records',
                    'Examination of continual improvement initiatives',
                ],
            },
        },
        'evidence': [
            'Reviewed privacy incident register and root cause analysis records',
            'Examined corrective action effectiveness verification for privacy findings',
            'Verified continual improvement initiatives for privacy controls',
        ],
    },
}


FRAMEWORK_31000 = {
    'title': {
    },
    'sections': {
    },
}


FRAMEWORK_10002 = {
    'title': {
    },
    'sections': {
    },
}

SUPPORTING_STANDARDS_EVIDENCE = {
    'iso_9001': {
        'ISO 9000:2015': 'Verified alignment of QMS terminology with ISO 9000 definitions',
        'ISO 9004:2018': 'Reviewed sustainable success initiatives referencing ISO 9004 guidance',
        'ISO 10018:2020': 'Examined people engagement and competence programs per ISO 10018',
        'ISO 19011:2018': 'Confirmed audit programme methodology aligned with ISO 19011',
    },
    'iso_14001': {
        'ISO 14004:2016': 'Reviewed EMS implementation framework referencing ISO 14004 guidance',
        'ISO 14031:2021': 'Examined environmental performance evaluation per ISO 14031',
        'ISO 14064-1:2018': 'Verified GHG inventory quantification and reporting per ISO 14064-1',
        'ISO 19011:2018': 'Confirmed environmental audit programme per ISO 19011',
    },
    'iso_45001': {
        'ISO 45002:2023': 'Reviewed OH&S management system implementation guidance alignment',
        'ISO 45003:2021': 'Examined psychological health and safety management per ISO 45003',
        'ISO 45005:2021': 'Verified safe working during pandemic measures per ISO 45005',
        'ISO 19011:2018': 'Confirmed OH&S audit programme methodology per ISO 19011',
    },
    'iso_27001': {
        'ISO 27000:2018': 'Verified ISMS terminology alignment with ISO 27000 definitions',
        'ISO 27002:2022': 'Examined control implementation referencing ISO 27002 guidance',
        'ISO 27005:2022': 'Reviewed information security risk management methodology per ISO 27005',
        'ISO 27004:2016': 'Verified ISMS performance metrics framework per ISO 27004',
        'ISO 27035:2023': 'Examined incident management process per ISO 27035',
    },
    'iso_50001': {
        'ISO 50004:2020': 'Reviewed EnMS implementation guidance alignment with ISO 50004',
        'ISO 50006:2023': 'Examined energy baseline and EnPI methodology per ISO 50006',
        'ISO 50015:2019': 'Verified energy performance measurement per ISO 50015',
        'ISO 50047:2016': 'Reviewed energy savings determination methodology per ISO 50047',
    },
    'iso_20000': {
        'ISO 20000-2:2019': 'Reviewed SMS implementation guidance per ISO 20000-2',
        'ISO 20000-3:2019': 'Examined scope definition and service context per ISO 20000-3',
        'ISO 20000-10:2018': 'Verified SMS terminology alignment with ISO 20000-10',
        'ISO 20000-13:2021': 'Reviewed multi-supplier service integration per ISO 20000-13',
    },
    'iso_22301': {
        'ISO 22313:2020': 'Reviewed BCMS implementation guidance per ISO 22313',
        'ISO 22317:2021': 'Examined business impact analysis methodology per ISO 22317',
        'ISO 22320:2019': 'Verified incident management structure per ISO 22320',
        'ISO 22330:2020': 'Reviewed people aspects of business continuity per ISO 22330',
        'ISO 22316:2019': 'Assessed organizational resilience alignment with ISO 22316',
    },
    'iso_37301': {
        'ISO 37001:2016': 'Reviewed anti-bribery management system controls per ISO 37001',
        'ISO 37002:2021': 'Examined whistleblowing management system alignment with ISO 37002',
        'ISO 31000:2018': 'Verified compliance risk management methodology per ISO 31000',
        'ISO 37000:2021': 'Reviewed governance of organizations alignment with ISO 37000',
    },
    'iso_42001': {
        'ISO 42005:2024': 'Reviewed AI impact assessment methodology per ISO 42005',
        'ISO 42006:2024': 'Examined AI management system audit requirements per ISO 42006',
        'ISO 23894:2024': 'Verified AI risk management alignment with ISO 23894',
        'ISO 5259-1:2024': 'Reviewed data quality for AI applications per ISO 5259-1',
        'ISO 38507:2022': 'Examined AI governance alignment with ISO 38507',
    },
    'iso_30401': {
        'ISO 30400:2022': 'Verified KM terminology alignment with ISO 30400 definitions',
        'ISO 30405:2023': 'Reviewed recruitment and workforce planning processes per ISO 30405',
        'ISO 30403:2021': 'Examined human capital reporting alignment with ISO 30403',
        'ISO 10018:2020': 'Reviewed people involvement and competence per ISO 10018',
    },
    'iso_27701': {
        'ISO 27001:2022': 'Verified integrated ISMS-PIMS controls alignment per ISO 27001',
        'ISO 27002:2022': 'Reviewed PII security control implementation per ISO 27002',
        'ISO 29100:2024': 'Examined privacy framework alignment with ISO 29100 principles',
        'ISO 29134:2023': 'Verified privacy impact assessment methodology per ISO 29134',
        'GDPR': 'Reviewed compliance with GDPR data subject rights and breach notification obligations',
    },
    'iso_31000': {
        'ISO 31010:2019': 'Reviewed risk assessment technique selection per ISO 31010',
        'ISO 31030:2021': 'Examined travel risk management alignment with ISO 31030',
        'ISO Guide 73:2009': 'Verified risk management terminology alignment with Guide 73',
    },
    'iso_10002': {
        'ISO 9001:2015': 'Verified complaints process integration with QMS per ISO 9001',
        'ISO 10001:2018': 'Reviewed codes of conduct for customer satisfaction per ISO 10001',
        'ISO 10003:2018': 'Examined external dispute resolution mechanisms per ISO 10003',
        'ISO 10004:2018': 'Verified customer satisfaction monitoring per ISO 10004',
    },
    'iso_13485': {
        'ISO 14971:2019': 'Reviewed risk management file alignment with ISO 14971 requirements',
        'ISO 13408:2024': 'Verified aseptic processing validation per ISO 13408',
        'ISO 11137:2015': 'Examined radiation sterilization validation per ISO 11137',
        'ISO 10993:2023': 'Reviewed biological evaluation of medical devices per ISO 10993',
        'ISO 19011:2018': 'Confirmed audit programme methodology aligned with ISO 19011',
    },
}


_COMPLIANCE_STATUSES = [
    'compliant',
    'partially_compliant',
    'non_compliant',
    'not_applicable',
    'not_audited',
]


def get_clause_data(standard_key: str) -> dict:
    """Return the full clause database for a given standard, merging
    HLS_CORE with the standard-specific Clause 8 and any Annex data."""

    standard_key = standard_key.lower()

    if standard_key in ('iso_31000',):
        return FRAMEWORK_31000

    if standard_key in ('iso_10002',):
        return FRAMEWORK_10002

    if standard_key in ('iso_27701',):
        clauses = {}

        for num in ('1', '2', '3'):
            if num in HLS_CORE:
                clauses[num] = dict(HLS_CORE[num])

        for num in ('4', '5', '6', '7', '9', '10'):
            hls = HLS_CORE.get(num, {})
            pims = PIMS_27701.get(num, {})
            merged = dict(hls)
            if pims:
                merged['title'] = pims.get('title', merged.get('title', ''))
                merged['sub_clauses'] = {
                    **hls.get('sub_clauses', {}),
                    **pims.get('sub_clauses', {}),
                }
            clauses[num] = merged

        c8_info = CLAUSE_8.get('iso_27701', {})
        if c8_info:
            clauses['8'] = dict(c8_info)

        return clauses

    clauses = {}
    for num in ('1', '2', '3'):
        if num in HLS_CORE:
            clauses[num] = dict(HLS_CORE[num])

    for num in ('4', '5', '6', '7', '9', '10'):
        clauses[num] = dict(HLS_CORE.get(num, {}))

    c8_info = CLAUSE_8.get(standard_key, {})
    if c8_info:
        clauses['8'] = dict(c8_info)
    else:
        hls_c8 = HLS_CORE.get('8')
        if hls_c8:
            clauses['8'] = dict(hls_c8)

    return clauses


def get_annex_a_data(standard_key: str) -> dict:
    """Return Annex A controls for standards that have them."""
    if standard_key == 'iso_27001':
        return ANNEX_A_27001
    if standard_key == 'iso_42001':
        return ANNEX_A_42001
    return {}


def get_supporting_evidence(standard_key: str) -> dict:
    """Return cross-references to supporting standards evidence."""
    return SUPPORTING_STANDARDS_EVIDENCE.get(standard_key, {})


def get_compliance_statuses() -> list:
    """Return the list of available compliance statuses."""
    return list(_COMPLIANCE_STATUSES)


def flatten_clauses(clause_dict: dict, parent_key: str = '') -> list:
    """Flatten the nested clause structure into a list of
    (clause_id, title, depth) tuples for easy iteration."""
    result = []
    for cid, info in sorted(clause_dict.items()):
        if isinstance(info, str):
            result.append((cid, info, 0))
            continue
        title = info.get('title', '') if isinstance(info, dict) else ''
        depth = parent_key.count('.') if parent_key else 0
        result.append((cid, title, depth))
        sub = info.get('sub_clauses', {}) if isinstance(info, dict) else {}
        if sub:
            full_parent = f'{parent_key}.{cid}' if parent_key else cid
            result.extend(flatten_clauses(sub, full_parent))
    return result


def _walk_clause_tree(clause_dict: dict, clause_id: str) -> dict | None:
    """Walk the clause tree to find a node by dot-notation ID.

    Handles both HLS keys (single digits like '4', '5') and dotted keys
    (Annex A like 'A.5', 'A.5.1') by trying all possible prefix lengths
    at each level and selecting the longest match.
    """
    parts = clause_id.split('.')
    current = clause_dict
    i = 0
    while i < len(parts):
        matched_j = None
        matched_key = None
        for j in range(i, len(parts)):
            prefix = '.'.join(parts[:j+1])
            if prefix in current:
                matched_j = j
                matched_key = prefix
        if matched_j is None:
            return None
        val = current[matched_key]
        if not isinstance(val, dict):
            return None
        if matched_j == len(parts) - 1:
            return val
        current = val.get('sub_clauses', {})
        i = matched_j + 1
    return None


def get_evidence_for_clause(clause_dict: dict, clause_id: str) -> list:
    """Walk the clause tree to find evidence items for a specific clause ID."""
    node = _walk_clause_tree(clause_dict, clause_id)
    return node.get('evidence', []) if node else []


def get_all_clause_items(standard_key: str) -> list:
    """Return a flat list of all clause items for a standard.
    Each item: {id, title, evidence: list, evidence_text: str, source}
    where source is 'hls' or 'annex_a'.
    evidence is a list of individual evidence suggestions.
    evidence_text is the joined version for backward compatibility.
    """
    items = []
    seen = set()

    clause_dict = get_clause_data(standard_key)
    annex = get_annex_a_data(standard_key)

    def _flatten(d, prefix=""):
        for cid, info in d.items():
            if isinstance(info, str):
                key = f"{prefix}{cid}"
                if key not in seen:
                    seen.add(key)
                    items.append({"id": key, "title": info, "evidence": [], "evidence_text": "", "source": "hls"})
                continue
            if not isinstance(info, dict):
                continue
            title = info.get("title", "")
            evidence_list = info.get("evidence", []) or []
            if isinstance(evidence_list, str):
                evidence_list = [evidence_list]
            evidence_text = "; ".join(evidence_list[:3]) if evidence_list else ""
            key = f"{prefix}{cid}"
            if key not in seen:
                seen.add(key)
                items.append({"id": key, "title": title, "evidence": evidence_list, "evidence_text": evidence_text, "source": "hls"})
            sub = info.get("sub_clauses", {})
            if sub:
                _flatten(sub, prefix=f"{key}.")

    _flatten(clause_dict)

    # Annex A controls
    if annex:
        for group_name, controls in annex.items():
            if isinstance(controls, dict):
                for ctrl_id, ctrl_info in controls.items():
                    if isinstance(ctrl_info, dict):
                        title = ctrl_info.get("title", ctrl_id)
                        ev = ctrl_info.get("evidence", ctrl_info.get("description", ""))
                        if isinstance(ev, list):
                            evidence_list = ev
                            evidence_text = "; ".join(ev[:3])
                        else:
                            evidence_list = [str(ev)] if ev else []
                            evidence_text = str(ev)
                    else:
                        title = str(ctrl_info)
                        evidence_list = []
                        evidence_text = ""
                    items.append({"id": ctrl_id, "title": title, "evidence": evidence_list, "evidence_text": evidence_text, "source": "annex_a"})

    return items


def get_gap_checklist_data(standard_key: str) -> list:
    """Build a complete gap analysis checklist from clause data.
    Returns list of {clause, title, requirement, status, gap_description,
    recommended_action, priority, target_date} for all clauses including Annex A."""
    today = datetime.now()
    items = get_all_clause_items(standard_key)
    statuses = ['Conformant', 'Partially Conformant', 'Non-Conformant', 'Not Reviewed']
    weights = [0.05, 0.15, 0.05, 0.75]
    results = []
    for item in items:
        status = random.choices(statuses, weights=weights, k=1)[0]
        gap = ''
        action = ''
        priority = 'Medium'
        if status == 'Non-Conformant':
            gap = f'No sufficient evidence found for {item["title"]} ({item["id"]}). Current implementation does not meet the standard requirement.'
            action = f'Develop and implement a process addressing the requirements of {item["id"]}. Document procedures, assign responsibilities, and provide training as needed.'
            priority = 'High'
        elif status == 'Partially Conformant':
            gap = f'Partial implementation observed for {item["title"]} ({item["id"]}). Some elements are in place but gaps remain in completeness or effectiveness.'
            action = f'Review current implementation against full requirements of {item["id"]}. Address identified gaps through corrective actions with assigned owners and target dates.'
            priority = 'High'
        elif status == 'Not Reviewed':
            gap = 'Not yet assessed during this gap analysis.'
            action = f'Schedule assessment for {item["id"]}. Review current practices against standard requirements and document compliance status.'
            priority = 'Medium'
        target = (today + timedelta(days=random.randint(30, 180))).strftime('%d/%m/%Y')
        results.append({
            'clause': item['id'],
            'title': item['title'],
            'requirement': f'{item["id"]}: {item["title"]}' if item['title'] else item['id'],
            'status': status,
            'gap_description': gap,
            'recommended_action': action,
            'priority': priority,
            'target_date': target,
        })
    return results
