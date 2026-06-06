import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')

ISO_STANDARDS = {
    'iso_9001': 'ISO 9001:2015 — Quality Management Systems',
    'iso_14001': 'ISO 14001:2015 — Environmental Management Systems',
    'iso_45001': 'ISO 45001:2018 — Occupational Health & Safety',
    'iso_27001': 'ISO 27001:2022 — Information Security Management',
    'iso_50001': 'ISO 50001:2018 — Energy Management Systems',
    'iso_20000': 'ISO 20000-1:2018 — Service Management Systems',
    'iso_22301': 'ISO 22301:2019 — Business Continuity Management',
    'iso_37301': 'ISO 37301:2021 — Compliance Management',
    'iso_42001': 'ISO 42001:2023 — Artificial Intelligence Management',
    'iso_30401': 'ISO 30401:2018 — Knowledge Management',
    'iso_27701': 'ISO 27701:2025 — Privacy Information Management',
    'iso_31000': 'ISO 31000:2018 — Risk Management — Guidelines',
    'iso_10002': 'ISO 10002:2018 — Customer Satisfaction — Complaints Handling',
}

STANDARD_CATEGORIES = [
    {'id': 'core', 'label': 'Core Management Systems', 'standards': ['iso_9001', 'iso_14001', 'iso_45001', 'iso_50001']},
    {'id': 'security', 'label': 'Security, Continuity & Service', 'standards': ['iso_27001', 'iso_22301', 'iso_20000', 'iso_27701']},
    {'id': 'specialized', 'label': 'Specialized Standards', 'standards': ['iso_37301', 'iso_30401', 'iso_42001']},
    {'id': 'frameworks', 'label': 'Guidelines & Frameworks', 'standards': ['iso_31000', 'iso_10002']},
]

STANDARD_FAMILIES = {
    'iso_9001': {
        'main': 'ISO 9001:2015 — Quality Management Systems',
        'supporting': ['ISO 9000:2015', 'ISO 9004:2018', 'ISO 10018:2020', 'ISO 19011:2018'],
    },
    'iso_14001': {
        'main': 'ISO 14001:2015 — Environmental Management Systems',
        'supporting': ['ISO 14004:2016', 'ISO 14031:2021', 'ISO 14064-1:2018', 'ISO 19011:2018'],
    },
    'iso_45001': {
        'main': 'ISO 45001:2018 — Occupational Health & Safety',
        'supporting': ['ISO 45002:2023', 'ISO 45003:2021', 'ISO 45005:2021', 'ISO 19011:2018'],
    },
    'iso_27001': {
        'main': 'ISO 27001:2022 — Information Security Management',
        'supporting': ['ISO 27000:2018', 'ISO 27002:2022', 'ISO 27005:2022', 'ISO 27004:2016', 'ISO 27035:2023'],
    },
    'iso_50001': {
        'main': 'ISO 50001:2018 — Energy Management Systems',
        'supporting': ['ISO 50004:2020', 'ISO 50006:2023', 'ISO 50015:2019', 'ISO 50047:2016'],
    },
    'iso_20000': {
        'main': 'ISO 20000-1:2018 — Service Management Systems',
        'supporting': ['ISO 20000-2:2019', 'ISO 20000-3:2019', 'ISO 20000-10:2018', 'ISO 20000-13:2021'],
    },
    'iso_22301': {
        'main': 'ISO 22301:2019 — Business Continuity Management',
        'supporting': ['ISO 22313:2020', 'ISO 22317:2021', 'ISO 22320:2019', 'ISO 22330:2020', 'ISO 22316:2019'],
    },
    'iso_37301': {
        'main': 'ISO 37301:2021 — Compliance Management',
        'supporting': ['ISO 37001:2016', 'ISO 37002:2021', 'ISO 31000:2018', 'ISO 37000:2021'],
    },
    'iso_42001': {
        'main': 'ISO 42001:2023 — Artificial Intelligence Management',
        'supporting': ['ISO 42005:2024', 'ISO 42006:2024', 'ISO 23894:2024', 'ISO 5259-1:2024', 'ISO 38507:2022'],
    },
    'iso_30401': {
        'main': 'ISO 30401:2018 — Knowledge Management',
        'supporting': ['ISO 30400:2022', 'ISO 30405:2023', 'ISO 30403:2021', 'ISO 10018:2020'],
    },
    'iso_27701': {
        'main': 'ISO 27701:2025 — Privacy Information Management',
        'supporting': ['ISO 27001:2022', 'ISO 27002:2022', 'ISO 29100:2024', 'ISO 29134:2023', 'GDPR'],
    },
    'iso_31000': {
        'main': 'ISO 31000:2018 — Risk Management Guidelines',
        'supporting': ['ISO 31010:2019', 'ISO 31030:2021', 'ISO Guide 73:2009'],
    },
    'iso_10002': {
        'main': 'ISO 10002:2018 — Complaints Handling',
        'supporting': ['ISO 9001:2015', 'ISO 10001:2018', 'ISO 10003:2018', 'ISO 10004:2018'],
    },
}

OUTPUT_DOCUMENTS = [
    'Audit_Plan_Stage_1',
    'Audit_Plan_Stage_2',
    'Participation_List',
    'Audit_Report',
    'ISO_Checklist',
    'Certificate_Text',
    'TNL',
    'Certificate',
]

DOC_LABELS = {
    'Audit_Plan_Stage_1': 'Audit Plan Stage 1',
    'Audit_Plan_Stage_2': 'Audit Plan Stage 2',
    'Participation_List': 'Participation List',
    'Audit_Report': 'Audit Report',
    'ISO_Checklist': 'ISO Checklist',
    'Certificate_Text': 'Certificate Text',
    'TNL': 'Test / Nonconformity Log',
    'Certificate': 'Certificate',
}

DEFAULT_LOGO_PATH = os.path.join(BASE_DIR, 'static', 'tuv_logo.png')
