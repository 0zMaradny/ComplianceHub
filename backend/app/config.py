import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')

ISO_STANDARDS = {
    'iso_9001': 'ISO 9001:2015 — Quality Management Systems',
    'iso_14001': 'ISO 14001:2015 — Environmental Management Systems',
    'iso_45001': 'ISO 45001:2018 — Occupational Health & Safety',
    'iso_27001': 'ISO 27001:2022 — Information Security Management',
    'iso_22301': 'ISO 22301:2019 — Business Continuity Management',
    'iso_20000': 'ISO 20000:2018 — Service Management Systems',
    'iso_50001': 'ISO 50001:2018 — Energy Management Systems',
    'iso_37301': 'ISO 37301:2021 — Compliance Management',
    'iso_31000': 'ISO 31000:2018 — Risk Management',
    'iso_42001': 'ISO 42001:2023 — Artificial Intelligence Management',
    'iso_30401': 'ISO 30401:2018 — Knowledge Management',
}

STANDARD_CATEGORIES = [
    {'id': 'core', 'label': 'Core Management Systems', 'standards': ['iso_9001', 'iso_14001', 'iso_45001', 'iso_50001']},
    {'id': 'security', 'label': 'Security, Continuity & Service', 'standards': ['iso_27001', 'iso_22301', 'iso_20000']},
    {'id': 'specialized', 'label': 'Specialized Standards', 'standards': ['iso_37301', 'iso_31000', 'iso_30401', 'iso_42001']},
]

OUTPUT_DOCUMENTS = [
    'Audit_Plan_Stage_1',
    'Audit_Plan_Stage_2',
    'Participation_List',
    'Audit_Report',
    'ISO_Checklist',
    'Certificate_Text',
]

DOC_LABELS = {
    'Audit_Plan_Stage_1': 'Audit Plan Stage 1',
    'Audit_Plan_Stage_2': 'Audit Plan Stage 2',
    'Participation_List': 'Participation List',
    'Audit_Report': 'Audit Report',
    'ISO_Checklist': 'ISO Checklist',
    'Certificate_Text': 'Certificate Text',
}

DEFAULT_LOGO_PATH = os.path.join(BASE_DIR, 'static', 'tuv_logo.png')
