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
            '4.1': 'Understanding the organization and its context',
            '4.2': 'Understanding the needs and expectations of interested parties',
            '4.3': 'Determining the scope of the management system',
            '4.4': 'Management system and its processes',
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
            '5.1': 'Leadership and commitment',
            '5.1.1': 'General',
            '5.2': 'Policy',
            '5.3': 'Roles, responsibilities and authorities',
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
            '6.1': 'Actions to address risks and opportunities',
            '6.2': 'Objectives and planning to achieve them',
            '6.3': 'Planning of changes',
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
            '7.1': 'Resources',
            '7.2': 'Competence',
            '7.3': 'Awareness',
            '7.4': 'Communication',
            '7.5': 'Documented information',
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
            '9.1': 'Monitoring, measurement, analysis and evaluation',
            '9.1.1': 'General',
            '9.2': 'Internal audit',
            '9.3': 'Management review',
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
            '10.1': 'Nonconformity and corrective action',
            '10.2': 'Continual improvement',
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
            '8.1': 'Operational planning and control',
            '8.2': {
                'title': 'Requirements for products and services',
                'sub_clauses': {
                    '8.2.1': 'Customer communication',
                    '8.2.2': 'Determination of requirements for products and services',
                    '8.2.3': 'Review of requirements for products and services',
                    '8.2.4': 'Changes to requirements for products and services',
                },
            },
            '8.3': {
                'title': 'Design and development of products and services',
                'sub_clauses': {
                    '8.3.1': 'General',
                    '8.3.2': 'Design and development planning',
                    '8.3.3': 'Design and development inputs',
                    '8.3.4': 'Design and development controls',
                    '8.3.5': 'Design and development outputs',
                    '8.3.6': 'Design and development changes',
                },
            },
            '8.4': {
                'title': 'Control of externally provided processes, products and services',
                'sub_clauses': {
                    '8.4.1': 'General',
                    '8.4.2': 'Type and extent of control',
                    '8.4.3': 'Information for external providers',
                },
            },
            '8.5': {
                'title': 'Production and service provision',
                'sub_clauses': {
                    '8.5.1': 'Control of production and service provision',
                    '8.5.2': 'Identification and traceability',
                    '8.5.3': 'Property belonging to customers or external providers',
                    '8.5.4': 'Preservation',
                    '8.5.5': 'Post-delivery activities',
                    '8.5.6': 'Control of changes',
                },
            },
            '8.6': 'Release of products and services',
            '8.7': 'Control of nonconforming outputs',
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
            '8.1': 'Operational planning and control',
            '8.2': 'Emergency preparedness and response',
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
                    '8.1.1': 'General',
                    '8.1.2': 'Eliminating hazards and reducing OH&S risks',
                    '8.1.3': 'Management of change',
                    '8.1.4': 'Procurement',
                },
            },
            '8.2': 'Emergency preparedness and response',
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
            '8.1': 'Operational planning and control',
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
            '8.1': 'Operational planning and control',
            '8.2': 'Information security risk assessment',
            '8.3': 'Information security risk treatment',
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
            '8.1': 'Operational planning and control',
            '8.2': 'Service management system',
            '8.3': 'Service portfolio management',
            '8.4': 'Relationship and agreement management',
            '8.5': 'Supply and demand management',
            '8.6': 'Service design, build and transition',
            '8.7': 'Resolution and fulfilment',
            '8.8': 'Service assurance',
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
            '8.1': 'Operational planning and control',
            '8.2': {
                'title': 'Business continuity analysis',
                'sub_clauses': {
                    '8.2.1': 'Business impact analysis',
                    '8.2.2': 'Risk assessment',
                },
            },
            '8.3': {
                'title': 'Business continuity strategies and solutions',
                'sub_clauses': {
                    '8.3.1': 'General',
                    '8.3.2': 'Identification of strategies and solutions',
                    '8.3.3': 'Selection of strategies and solutions',
                },
            },
            '8.4': {
                'title': 'Business continuity plans and procedures',
                'sub_clauses': {
                    '8.4.1': 'General',
                    '8.4.2': 'Incident response structure',
                    '8.4.3': 'Warning and communication',
                    '8.4.4': 'Business continuity plans',
                    '8.4.5': 'Recovery procedures',
                },
            },
            '8.5': {
                'title': 'Exercise and testing',
                'sub_clauses': {
                    '8.5.1': 'General',
                    '8.5.2': 'Exercise programmes',
                    '8.5.3': 'Testing of continuity solutions',
                },
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
            '8.1': 'Operational planning and control',
            '8.2': {
                'title': 'Establishing controls and procedures',
                'sub_clauses': {
                    '8.2.1': 'General',
                    '8.2.2': 'Controls and procedures for compliance obligations',
                    '8.2.3': 'Controls and procedures for persons',
                    '8.2.4': 'Controls and procedures for outsourced processes',
                },
            },
            '8.3': 'Reporting concerns',
            '8.4': 'Investigation process',
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
            '8.1': 'Operational planning and control',
            '8.2': {
                'title': 'AI risk assessment',
                'sub_clauses': {
                    '8.2.1': 'AI risk assessment process',
                    '8.2.2': 'AI risk assessment criteria',
                    '8.2.3': 'AI risk acceptance',
                },
            },
            '8.3': {
                'title': 'AI risk treatment',
                'sub_clauses': {
                    '8.3.1': 'AI risk treatment plan',
                    '8.3.2': 'AI risk treatment implementation',
                },
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
            '8.1': 'Operational planning and control',
            '8.2': 'Knowledge development',
            '8.3': 'Knowledge transfer and conversion',
            '8.4': 'Knowledge retention and preservation',
            '8.5': 'Knowledge sharing and access',
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
            '8.1': 'Operational planning and control',
            '8.2': 'Privacy risk assessment',
            '8.3': 'Privacy risk treatment',
            '8.4': 'Data subject rights management',
            '8.5': 'Data breach management',
            '8.6': 'Privacy by design and default',
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
}


ANNEX_A_27001 = {
    'A.5': {
        'title': 'Organizational Controls (37 controls)',
        'sub_clauses': {
            'A.5.1': 'Information security policies and procedures',
            'A.5.2': 'Information security roles and responsibilities',
            'A.5.3': 'Segregation of duties',
            'A.5.4': 'Management responsibilities',
            'A.5.5': 'Contact with authorities',
            'A.5.6': 'Contact with special interest groups',
            'A.5.7': 'Threat intelligence',
            'A.5.8': 'Information security in project management',
            'A.5.9': 'Inventory of information and other associated assets',
            'A.5.10': 'Acceptable use of information and other associated assets',
            'A.5.11': 'Return of assets',
            'A.5.12': 'Classification of information',
            'A.5.13': 'Labelling of information',
            'A.5.14': 'Information transfer',
            'A.5.15': 'Access control',
            'A.5.16': 'Identity management',
            'A.5.17': 'Authentication information',
            'A.5.18': 'Access rights',
            'A.5.19': 'Information security in supplier relationships',
            'A.5.20': 'Addressing information security within supplier agreements',
            'A.5.21': 'Managing information security in the ICT supply chain',
            'A.5.22': 'Monitoring review and change management of supplier services',
            'A.5.23': 'Information security for use of cloud services',
            'A.5.24': 'Information security incident management planning and preparation',
            'A.5.25': 'Assessment and decision on information security events',
            'A.5.26': 'Response to information security incidents',
            'A.5.27': 'Learning from information security incidents',
            'A.5.28': 'Collection of evidence',
            'A.5.29': 'Information security during disruption',
            'A.5.30': 'ICT readiness for business continuity',
            'A.5.31': 'Legal statutory regulatory and contractual requirements',
            'A.5.32': 'Intellectual property rights',
            'A.5.33': 'Protection of records',
            'A.5.34': 'Privacy and protection of PII',
            'A.5.35': 'Independent review of information security',
            'A.5.36': 'Compliance with policies and standards',
            'A.5.37': 'Documented operating procedures',
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
            'A.6.1': 'Screening',
            'A.6.2': 'Terms and conditions of employment',
            'A.6.3': 'Information security awareness education and training',
            'A.6.4': 'Disciplinary process',
            'A.6.5': 'Responsibilities after termination or change of employment',
            'A.6.6': 'Confidentiality or non-disclosure agreements',
            'A.6.7': 'Remote working',
            'A.6.8': 'Information security event reporting',
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
            'A.7.1': 'Physical security perimeters',
            'A.7.2': 'Physical entry controls',
            'A.7.3': 'Securing offices rooms and facilities',
            'A.7.4': 'Physical security monitoring',
            'A.7.5': 'Protection against physical and environmental threats',
            'A.7.6': 'Working in secure areas',
            'A.7.7': 'Clear desk and clear screen',
            'A.7.8': 'Equipment siting and protection',
            'A.7.9': 'Security of assets off-premises',
            'A.7.10': 'Storage media',
            'A.7.11': 'Supporting utilities',
            'A.7.12': 'Cabling security',
            'A.7.13': 'Equipment maintenance',
            'A.7.14': 'Secure disposal or re-use of equipment',
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
            'A.8.1': 'User endpoint devices',
            'A.8.2': 'Privileged access rights',
            'A.8.3': 'Information access restriction',
            'A.8.4': 'Access to source code',
            'A.8.5': 'Secure authentication',
            'A.8.6': 'Capacity management',
            'A.8.7': 'Protection against malware',
            'A.8.8': 'Management of technical vulnerabilities',
            'A.8.9': 'Configuration management',
            'A.8.10': 'Information deletion',
            'A.8.11': 'Data masking',
            'A.8.12': 'Data leakage prevention',
            'A.8.13': 'Information backup',
            'A.8.14': 'Redundancy of information processing facilities',
            'A.8.15': 'Logging',
            'A.8.16': 'Monitoring activities',
            'A.8.17': 'Clock synchronization',
            'A.8.18': 'Use of privileged utility programs',
            'A.8.19': 'Installation of software on operational systems',
            'A.8.20': 'Networks security',
            'A.8.21': 'Security of network services',
            'A.8.22': 'Segregation of networks',
            'A.8.23': 'Web filtering',
            'A.8.24': 'Use of cryptography',
            'A.8.25': 'Secure development lifecycle',
            'A.8.26': 'Application security requirements',
            'A.8.27': 'Secure system architecture and engineering principles',
            'A.8.28': 'Secure coding',
            'A.8.29': 'Security testing in development and acceptance',
            'A.8.30': 'Outsourced development',
            'A.8.31': 'Separation of development test and production environments',
            'A.8.32': 'Change management',
            'A.8.33': 'Test information',
            'A.8.34': 'Protection of information systems during audit testing',
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
            'A.9.1.1': 'AI policy framework',
            'A.9.1.2': 'AI governance roles and responsibilities',
            'A.9.1.3': 'AI policy communication',
            'A.9.1.4': 'AI resource allocation',
        },
        'evidence': [
            'Reviewed AI policy framework covering ethical principles and governance requirements',
            'Examined AI governance structure with defined accountability for AI systems',
        ],
    },
    'A.9.2': {
        'title': 'AI System Lifecycle (8 controls)',
        'sub_clauses': {
            'A.9.2.1': 'AI system planning and design',
            'A.9.2.2': 'AI system development methodology',
            'A.9.2.3': 'Data acquisition and preparation',
            'A.9.2.4': 'Model training and validation',
            'A.9.2.5': 'Model testing and evaluation',
            'A.9.2.6': 'AI system deployment',
            'A.9.2.7': 'AI system operation and monitoring',
            'A.9.2.8': 'AI system retirement',
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
            'A.9.3.1': 'AI risk assessment process',
            'A.9.3.2': 'AI risk criteria and acceptance levels',
            'A.9.3.3': 'AI risk treatment planning',
            'A.9.3.4': 'AI risk monitoring and review',
            'A.9.3.5': 'AI residual risk acceptance',
            'A.9.3.6': 'AI risk register maintenance',
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
            'A.9.4.1': 'Data quality management',
            'A.9.4.2': 'Data provenance and lineage',
            'A.9.4.3': 'Training data governance',
            'A.9.4.4': 'Data bias detection and mitigation',
            'A.9.4.5': 'Data retention and disposal',
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
            'A.9.5.1': 'AI system documentation',
            'A.9.5.2': 'Explainability requirements',
            'A.9.5.3': 'AI system output labelling',
            'A.9.5.4': 'Stakeholder communication',
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
            'A.9.6.1': 'Fairness assessment',
            'A.9.6.2': 'Discrimination monitoring',
            'A.9.6.3': 'Remediation of unfair outcomes',
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
            'A.9.7.1': 'AI system security controls',
            'A.9.7.2': 'Adversarial attack protection',
            'A.9.7.3': 'AI system safety testing',
            'A.9.7.4': 'AI incident response',
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
            'A.9.8.1': 'AI impact assessment process',
            'A.9.8.2': 'Societal impact evaluation',
            'A.9.8.3': 'Environmental impact of AI systems',
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
            'A.9.9.1': 'Third-party AI system oversight',
            'A.9.9.2': 'AI supply chain risk assessment',
            'A.9.9.3': 'Open-source AI component management',
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
            '5.1': 'Privacy leadership and commitment',
            '5.2': 'Privacy policy',
            '5.3': 'Privacy roles and responsibilities including DPO',
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
            '6.1': 'Actions to address privacy risks and opportunities',
            '6.2': 'Privacy objectives and planning',
            '6.3': 'Privacy risk assessment methodology',
            '6.4': 'Legal and regulatory requirements register',
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
            '7.1': 'Resources for privacy management',
            '7.2': 'Privacy competence and training',
            '7.3': 'Privacy awareness',
            '7.4': 'Privacy communication',
            '7.5': 'Documented information for privacy',
            '7.6': 'Records of processing activities (ROPA)',
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
            '9.1': 'Privacy monitoring and measurement',
            '9.2': 'Internal audit of PIMS',
            '9.3': 'Management review of PIMS',
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
            '10.1': 'Privacy nonconformities and corrective actions',
            '10.2': 'Continual improvement of PIMS',
        },
        'evidence': [
            'Reviewed privacy incident register and root cause analysis records',
            'Examined corrective action effectiveness verification for privacy findings',
            'Verified continual improvement initiatives for privacy controls',
        ],
    },
}


FRAMEWORK_31000 = {
    'title': 'ISO 31000:2018 — Risk Management Framework',
    'sections': {
        '1': {
            'title': 'Principles of Risk Management',
            'sub_sections': {
                '1.1': 'Integrated',
                '1.2': 'Structured and comprehensive',
                '1.3': 'Customized',
                '1.4': 'Inclusive',
                '1.5': 'Dynamic',
                '1.6': 'Best available information',
                '1.7': 'Human and cultural factors',
                '1.8': 'Continual improvement',
            },
            'evidence': [
                'Reviewed risk management principles integration into organizational processes',
                'Examined how risk management is customized to organizational context',
                'Assessed inclusiveness of stakeholder participation in risk processes',
            ],
        },
        '2': {
            'title': 'Framework Leadership and Commitment',
            'sub_sections': {
                '2.1': 'Integration',
                '2.2': 'Design',
                '2.3': 'Implementation',
                '2.4': 'Evaluation',
                '2.5': 'Improvement',
            },
            'evidence': [
                'Reviewed risk management framework mandate and sponsorship from top management',
                'Examined framework integration across organizational governance structures',
                'Verified framework evaluation and improvement cycle documentation',
            ],
        },
        '3': {
            'title': 'Risk Management Process',
            'sub_sections': {
                '3.1': 'Communication and consultation',
                '3.2': {
                    'title': 'Scope context and criteria',
                    'sub_sections': {
                        '3.2.1': 'Defining scope',
                        '3.2.2': 'External and internal context',
                        '3.2.3': 'Defining risk criteria',
                    },
                },
                '3.3': {
                    'title': 'Risk assessment',
                    'sub_sections': {
                        '3.3.1': 'Risk identification',
                        '3.3.2': 'Risk analysis',
                        '3.3.3': 'Risk evaluation',
                    },
                },
                '3.4': 'Risk treatment',
                '3.5': 'Monitoring and review',
                '3.6': 'Recording and reporting',
            },
            'evidence': [
                'Reviewed risk assessment documentation including identification analysis and evaluation',
                'Examined risk treatment plans with residual risk acceptance',
                'Verified communication and consultation records with stakeholder engagement',
                'Assessed risk criteria alignment with organizational risk appetite',
                'Reviewed monitoring and review schedules for risk treatment effectiveness',
            ],
        },
    },
}

FRAMEWORK_10002 = {
    'title': 'ISO 10002:2018 — Complaints Handling Framework',
    'sections': {
        '1': {
            'title': 'Guiding Principles for Complaints Handling',
            'sub_sections': {
                '1.1': 'Visibility',
                '1.2': 'Accessibility',
                '1.3': 'Responsiveness',
                '1.4': 'Objectivity',
                '1.5': 'Charges',
                '1.6': 'Confidentiality',
                '1.7': 'Customer-focused approach',
                '1.8': 'Accountability',
                '1.9': 'Continual improvement',
            },
            'evidence': [
                'Reviewed complaints policy visibility on website and customer-facing materials',
                'Examined accessibility of complaints channels for diverse customer groups',
                'Assessed responsiveness metrics against defined service level targets',
            ],
        },
        '2': {
            'title': 'Complaints Handling Framework',
            'sub_sections': {
                '2.1': 'Policy commitment',
                '2.2': 'Objectives and targets',
                '2.3': 'Responsibilities and authorities',
                '2.4': 'Resource allocation',
                '2.5': 'Competence and training',
                '2.6': 'Documentation and records',
            },
            'evidence': [
                'Reviewed complaints handling policy endorsed by top management',
                'Examined complaints handling process documentation and procedures',
                'Verified resource allocation for complaints handling function adequacy',
            ],
        },
        '3': {
            'title': 'Complaints Handling Process',
            'sub_sections': {
                '3.1': 'Receipt of complaint',
                '3.2': 'Tracking of complaint',
                '3.3': 'Acknowledgement of complaint',
                '3.4': 'Initial assessment of complaint',
                '3.5': 'Investigation of complaint',
                '3.6': 'Response to complaint',
                '3.7': 'Communication of decision',
                '3.8': 'Closure of complaint',
            },
            'evidence': [
                'Reviewed complaints register with tracking and status management',
                'Examined investigation reports including root cause analysis findings',
                'Verified response timelines and customer satisfaction with outcomes',
                'Assessed escalation process for unresolved complaints handling',
            ],
        },
        '4': {
            'title': 'Monitoring and Analysis',
            'sub_sections': {
                '4.1': 'Complaint monitoring and measurement',
                '4.2': 'Customer satisfaction measurement',
                '4.3': 'Complaint data analysis',
                '4.4': 'Internal audit of complaints process',
                '4.5': 'Management review of complaints data',
            },
            'evidence': [
                'Reviewed complaint trend analysis and root cause patterns',
                'Examined customer satisfaction survey results and improvement actions',
                'Verified management review inputs including complaint performance data',
            ],
        },
        '5': {
            'title': 'Improvement of Complaints Handling',
            'sub_sections': {
                '5.1': 'Corrective actions',
                '5.2': 'Preventive actions',
                '5.3': 'Continual improvement of complaints process',
                '5.4': 'Complaints handling process audit',
            },
            'evidence': [
                'Reviewed corrective action records from complaint investigations',
                'Examined preventive actions identified through complaint trend analysis',
                'Verified effectiveness of implemented improvements to complaints process',
            ],
        },
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


def get_evidence_for_clause(clause_dict: dict, clause_id: str) -> list:
    """Walk the clause tree to find evidence items for a specific clause ID."""
    parts = clause_id.split('.')
    current = clause_dict
    for i, part in enumerate(parts):
        if part in current:
            val = current[part]
            if isinstance(val, dict):
                if i == len(parts) - 1:
                    return val.get('evidence', [])
                current = val.get('sub_clauses', {})
            else:
                return []
        else:
            return []
    return []


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
