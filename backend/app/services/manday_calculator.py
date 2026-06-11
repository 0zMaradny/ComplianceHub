import re
import math

AUDIT_TYPE_MULTIPLIERS = {
    'initial': 1.0,
    'surveillance_1': 1.0 / 3.0,
    'surveillance_2': 1.0 / 3.0,
    'recertification': 2.0 / 3.0,
    'transfer': 2.0 / 3.0,
}

AUDIT_TYPE_KEYWORDS = {
    'surveillance 1': 'surveillance_1',
    'surveillance 2': 'surveillance_2',
    'surveillance': 'surveillance_1',
    'surv 1': 'surveillance_1',
    'surv 2': 'surveillance_2',
    'surv1': 'surveillance_1',
    'surv2': 'surveillance_2',
    'recertification': 'recertification',
    're-certification': 'recertification',
    're certification': 'recertification',
    'recert': 'recertification',
    'initial': 'initial',
    'certification': 'initial',
    'stage 1': 'initial',
    'stage 2': 'initial',
    'transfer': 'transfer',
}

STANDARD_DISPLAY_NAMES = {
    'iso_9001': 'ISO 9001:2015 \u2014 QMS',
    'iso_14001': 'ISO 14001:2015 \u2014 EMS',
    'iso_45001': 'ISO 45001:2018 \u2014 OH&S',
    'iso_27001': 'ISO 27001:2022 \u2014 ISMS',
    'iso_50001': 'ISO 50001:2018 \u2014 EnMS',
    'iso_20000': 'ISO 20000-1:2018 \u2014 ITSM',
    'iso_22301': 'ISO 22301:2019 \u2014 BCMS',
    'iso_37301': 'ISO 37301:2021 \u2014 Compliance',
    'iso_42001': 'ISO 42001:2023 \u2014 AIMS',
    'iso_30401': 'ISO 30401:2018 \u2014 KM',
    'iso_27701': 'ISO 27701:2025 \u2014 PIMS',
    'iso_31000': 'ISO 31000:2018 \u2014 Risk',
    'iso_13485': 'ISO 13485:2016 \u2014 MDQMS',
    'iso_10002': 'ISO 10002:2018 \u2014 Complaints',
}

STANDARD_KEY_FROM_TEXT = {}


def _build_standard_lookup():
    for key, display in STANDARD_DISPLAY_NAMES.items():
        short = key.replace('iso_', '')
        STANDARD_KEY_FROM_TEXT[short] = key
        STANDARD_KEY_FROM_TEXT[display.lower()] = key
        for ws in display.split():
            ws_clean = ws.strip('.,:;()\u2014')
            if len(ws_clean) >= 5 and not ws_clean.startswith('ISO'):
                STANDARD_KEY_FROM_TEXT[ws_clean.lower()] = key
    standard_nums = {
        '9001': 'iso_9001', '14001': 'iso_14001', '45001': 'iso_45001',
        '27001': 'iso_27001', '50001': 'iso_50001', '20000': 'iso_20000',
        '22301': 'iso_22301', '37301': 'iso_37301', '42001': 'iso_42001',
        '30401': 'iso_30401', '27701': 'iso_27701', '31000': 'iso_31000',
        '13485': 'iso_13485',
        '10002': 'iso_10002',
    }
    for num, key in standard_nums.items():
        STANDARD_KEY_FROM_TEXT[num] = key


_build_standard_lookup()


def _band_table(values):
    rows = []
    for entry in values:
        rows.append({
            'max_employees': entry[0],
            'low': entry[1],
            'medium': entry[2],
            'high': entry[3],
        })
    return rows


QMS_TABLE = _band_table([
    (5, 1.5, 2.0, 2.5),
    (10, 2.0, 2.5, 3.5),
    (15, 2.5, 3.5, 4.5),
    (25, 3.0, 4.5, 5.5),
    (45, 4.0, 5.5, 7.0),
    (65, 5.0, 6.5, 8.0),
    (85, 6.0, 7.5, 9.0),
    (125, 7.0, 8.5, 11.0),
    (175, 8.0, 10.0, 12.0),
    (275, 9.0, 11.0, 13.0),
    (425, 10.0, 12.0, 15.0),
    (625, 11.0, 13.0, 16.0),
    (875, 12.0, 14.0, 17.0),
    (1175, 13.0, 15.0, 19.0),
    (1550, 14.0, 16.0, 20.0),
    (2025, 15.0, 17.0, 21.0),
    (2675, 16.0, 18.0, 23.0),
    (999999, 17.0, 19.0, 25.0),
])

EMS_TABLE = _band_table([
    (5, 2.0, 2.5, 3.0),
    (10, 2.5, 3.0, 4.0),
    (15, 3.0, 4.0, 5.0),
    (25, 3.5, 5.0, 6.0),
    (45, 4.5, 6.0, 7.5),
    (65, 5.5, 7.0, 8.5),
    (85, 6.5, 8.0, 9.5),
    (125, 7.5, 9.0, 11.5),
    (175, 8.5, 10.5, 13.0),
    (275, 9.5, 11.5, 14.0),
    (425, 10.5, 13.0, 16.0),
    (625, 11.5, 14.0, 17.0),
    (875, 12.5, 15.0, 18.0),
    (1175, 14.0, 16.0, 20.0),
    (1550, 15.0, 17.0, 21.0),
    (2025, 16.0, 18.0, 22.0),
    (2675, 17.0, 19.0, 24.0),
    (999999, 18.0, 20.0, 26.0),
])

OHS_TABLE = _band_table([
    (5, 2.5, 2.5, 3.0),
    (10, 3.0, 3.0, 3.5),
    (15, 3.0, 3.5, 4.5),
    (25, 3.5, 4.5, 5.5),
    (45, 4.0, 5.5, 7.0),
    (65, 4.5, 6.0, 8.0),
    (85, 5.0, 7.0, 9.0),
    (125, 5.5, 8.0, 11.0),
    (175, 6.0, 9.0, 12.0),
    (275, 7.0, 10.0, 13.0),
    (425, 8.0, 11.0, 15.0),
    (625, 9.0, 12.0, 16.0),
    (875, 10.0, 13.0, 17.0),
    (1175, 11.0, 15.0, 19.0),
    (1550, 12.0, 16.0, 20.0),
    (2025, 13.0, 17.0, 21.0),
    (2675, 14.0, 18.0, 23.0),
    (999999, 15.0, 19.0, 25.0),
])

ISMS_TABLE = _band_table([
    (5, 2.0, 2.5, 3.5),
    (10, 2.5, 3.0, 4.5),
    (15, 3.0, 4.0, 5.5),
    (25, 3.5, 5.0, 6.5),
    (45, 4.5, 6.0, 8.0),
    (65, 5.5, 7.0, 9.0),
    (85, 6.5, 8.0, 10.0),
    (125, 7.5, 9.5, 12.0),
    (175, 8.5, 11.0, 13.5),
    (275, 9.5, 12.0, 15.0),
    (425, 10.5, 13.5, 17.0),
    (625, 11.5, 15.0, 18.5),
    (875, 12.5, 16.0, 20.0),
    (1175, 14.0, 17.5, 22.0),
    (1550, 15.0, 19.0, 23.5),
    (2025, 16.0, 20.0, 25.0),
    (2675, 17.0, 21.0, 26.5),
    (999999, 18.0, 22.0, 28.0),
])

ENERGY_TABLE = _band_table([
    (5, 2.0, 3.0, 4.0),
    (10, 2.5, 3.5, 5.0),
    (15, 3.0, 4.0, 5.5),
    (25, 3.5, 4.5, 6.5),
    (45, 4.0, 5.5, 7.5),
    (65, 5.0, 6.5, 8.5),
    (85, 5.5, 7.5, 9.5),
    (125, 6.5, 8.5, 11.0),
    (175, 7.5, 9.5, 12.0),
    (275, 8.5, 11.0, 13.5),
    (425, 9.5, 12.0, 15.0),
    (625, 10.5, 13.0, 16.0),
    (875, 11.5, 14.0, 17.5),
    (1175, 12.5, 15.5, 19.0),
    (1550, 13.5, 16.5, 20.5),
    (2025, 14.5, 18.0, 22.0),
    (2675, 15.5, 19.0, 23.5),
    (999999, 16.5, 20.0, 25.0),
])

SERVICE_TABLE = _band_table([
    (5, 2.0, 2.5, 3.0),
    (10, 2.5, 3.0, 4.0),
    (15, 3.0, 3.5, 4.5),
    (25, 3.5, 4.5, 5.5),
    (45, 4.0, 5.5, 7.0),
    (65, 5.0, 6.5, 8.0),
    (85, 5.5, 7.5, 9.0),
    (125, 6.5, 8.5, 11.0),
    (175, 7.5, 9.5, 12.0),
    (275, 8.5, 10.5, 13.0),
    (425, 9.5, 12.0, 15.0),
    (625, 10.5, 13.0, 16.0),
    (875, 11.5, 14.0, 17.0),
    (1175, 12.5, 15.5, 19.0),
    (1550, 13.5, 16.5, 20.0),
    (2025, 14.5, 18.0, 21.0),
    (2675, 15.5, 19.0, 22.0),
    (999999, 16.5, 20.0, 23.0),
])

BCMS_TABLE = _band_table([
    (5, 2.0, 2.5, 3.5),
    (10, 2.5, 3.5, 4.5),
    (15, 3.0, 4.0, 5.0),
    (25, 3.5, 4.5, 6.0),
    (45, 4.5, 5.5, 7.5),
    (65, 5.5, 6.5, 8.5),
    (85, 6.0, 7.5, 9.5),
    (125, 7.0, 8.5, 11.5),
    (175, 8.0, 9.5, 12.5),
    (275, 9.0, 11.0, 14.0),
    (425, 10.0, 12.5, 15.5),
    (625, 11.0, 13.5, 17.0),
    (875, 12.0, 14.5, 18.5),
    (1175, 13.5, 16.0, 20.0),
    (1550, 14.5, 17.5, 21.5),
    (2025, 15.5, 19.0, 23.0),
    (2675, 16.5, 20.0, 24.5),
    (999999, 17.5, 21.0, 26.0),
])

COMPLIANCE_TABLE = _band_table([
    (5, 1.5, 2.0, 3.0),
    (10, 2.0, 2.5, 3.5),
    (15, 2.5, 3.0, 4.5),
    (25, 3.0, 4.0, 5.5),
    (45, 3.5, 5.0, 6.5),
    (65, 4.5, 6.0, 7.5),
    (85, 5.0, 6.5, 8.5),
    (125, 6.0, 7.5, 10.0),
    (175, 7.0, 8.5, 11.0),
    (275, 8.0, 10.0, 12.5),
    (425, 9.0, 11.0, 14.0),
    (625, 10.0, 12.0, 15.0),
    (875, 11.0, 13.0, 16.0),
    (1175, 12.0, 14.5, 17.5),
    (1550, 13.0, 15.5, 19.0),
    (2025, 14.0, 16.5, 20.0),
    (2675, 15.0, 17.5, 21.5),
    (999999, 16.0, 18.5, 23.0),
])

AIMS_TABLE = _band_table([
    (5, 2.5, 3.0, 4.0),
    (10, 3.0, 3.5, 5.0),
    (15, 3.5, 4.5, 5.5),
    (25, 4.0, 5.0, 6.5),
    (45, 5.0, 6.0, 8.0),
    (65, 5.5, 7.0, 9.0),
    (85, 6.5, 8.0, 10.0),
    (125, 7.5, 9.0, 12.0),
    (175, 8.5, 10.0, 13.0),
    (275, 9.5, 11.5, 14.5),
    (425, 10.5, 13.0, 16.0),
    (625, 11.5, 14.0, 17.5),
    (875, 12.5, 15.0, 19.0),
    (1175, 14.0, 16.5, 20.5),
    (1550, 15.0, 18.0, 22.0),
    (2025, 16.0, 19.0, 23.5),
    (2675, 17.0, 20.0, 25.0),
    (999999, 18.0, 21.0, 26.5),
])

KM_TABLE = _band_table([
    (5, 1.5, 2.0, 2.5),
    (10, 2.0, 2.5, 3.0),
    (15, 2.5, 3.0, 4.0),
    (25, 3.0, 3.5, 4.5),
    (45, 3.5, 4.5, 5.5),
    (65, 4.0, 5.5, 6.5),
    (85, 4.5, 6.0, 7.5),
    (125, 5.5, 7.0, 8.5),
    (175, 6.5, 8.0, 9.5),
    (275, 7.5, 9.0, 11.0),
    (425, 8.5, 10.0, 12.5),
    (625, 9.5, 11.0, 13.5),
    (875, 10.5, 12.0, 14.5),
    (1175, 11.5, 13.5, 16.0),
    (1550, 12.5, 14.5, 17.5),
    (2025, 13.5, 15.5, 19.0),
    (2675, 14.5, 16.5, 20.0),
    (999999, 15.5, 17.5, 21.0),
])

MDQMS_TABLE = _band_table([
    (5, 1.5, 2.0, 2.5),
    (10, 2.0, 2.5, 3.5),
    (15, 2.5, 3.5, 4.5),
    (25, 3.0, 4.5, 5.5),
    (45, 4.0, 5.5, 7.0),
    (65, 5.0, 6.5, 8.0),
    (85, 6.0, 7.5, 9.0),
    (125, 7.0, 8.5, 11.0),
    (175, 8.0, 10.0, 12.0),
    (275, 9.0, 11.0, 13.0),
    (425, 10.0, 12.0, 15.0),
    (625, 11.0, 13.0, 16.0),
    (875, 12.0, 14.0, 17.0),
    (1175, 13.0, 15.0, 19.0),
    (1550, 14.0, 16.0, 20.0),
    (2025, 15.0, 17.0, 21.0),
    (2675, 16.0, 18.0, 23.0),
    (999999, 17.0, 19.0, 25.0),
])

PIMS_TABLE = _band_table([
    (5, 2.0, 2.5, 3.5),
    (10, 2.5, 3.5, 4.5),
    (15, 3.0, 4.0, 5.0),
    (25, 3.5, 4.5, 6.0),
    (45, 4.5, 5.5, 7.5),
    (65, 5.0, 6.5, 8.5),
    (85, 6.0, 7.5, 9.5),
    (125, 7.0, 8.5, 11.0),
    (175, 8.0, 9.5, 12.0),
    (275, 9.0, 11.0, 13.5),
    (425, 10.0, 12.5, 15.0),
    (625, 11.0, 13.5, 16.5),
    (875, 12.0, 14.5, 18.0),
    (1175, 13.0, 16.0, 19.5),
    (1550, 14.0, 17.5, 21.0),
    (2025, 15.0, 19.0, 22.5),
    (2675, 16.0, 20.0, 24.0),
    (999999, 17.0, 21.0, 25.5),
])

STANDARD_TABLE_MAP = {
    'iso_9001': ('QMS', QMS_TABLE),
    'iso_14001': ('EMS', EMS_TABLE),
    'iso_45001': ('OH&S', OHS_TABLE),
    'iso_27001': ('ISMS', ISMS_TABLE),
    'iso_50001': ('EnMS', ENERGY_TABLE),
    'iso_20000': ('ITSM', SERVICE_TABLE),
    'iso_22301': ('BCMS', BCMS_TABLE),
    'iso_37301': ('CMS', COMPLIANCE_TABLE),
    'iso_42001': ('AIMS', AIMS_TABLE),
    'iso_30401': ('KMS', KM_TABLE),
    'iso_27701': ('PIMS', PIMS_TABLE),
    'iso_13485': ('MDQMS', MDQMS_TABLE),
    'iso_31000': ('Framework', None),
    'iso_10002': ('Framework', None),
}

IAF_MD_11_REDUCTION_PCT = {
    ('iso_9001', 'iso_14001'): 0.20,
    ('iso_9001', 'iso_45001'): 0.20,
    ('iso_14001', 'iso_45001'): 0.20,
    ('iso_9001', 'iso_27001'): 0.15,
    ('iso_14001', 'iso_27001'): 0.15,
    ('iso_45001', 'iso_27001'): 0.15,
    ('iso_9001', 'iso_50001'): 0.15,
    ('iso_14001', 'iso_50001'): 0.15,
    ('iso_45001', 'iso_50001'): 0.15,
    ('iso_27001', 'iso_27701'): 0.20,
    ('iso_27001', 'iso_22301'): 0.15,
    ('iso_9001', 'iso_20000'): 0.15,
    ('iso_9001', 'iso_22301'): 0.15,
    ('iso_14001', 'iso_22301'): 0.10,
    ('iso_45001', 'iso_22301'): 0.10,
    ('iso_9001', 'iso_13485'): 0.20,
    ('iso_13485', 'iso_14001'): 0.10,
    ('iso_13485', 'iso_45001'): 0.10,
}

MAX_IMS_REDUCTION = 0.20


def lookup_base_mandays(standard_key, employee_count, complexity='medium'):
    table_info = STANDARD_TABLE_MAP.get(standard_key)
    if table_info is None:
        return None
    name, table = table_info
    if table is None:
        return None
    complexity = complexity.lower()
    if complexity not in ('low', 'medium', 'high'):
        complexity = 'medium'
    for band in table:
        if employee_count <= band['max_employees']:
            return int(math.ceil(band[complexity] * 2.0) / 2.0)
    return None


def detect_audit_type(text):
    text_lower = text.lower()
    scores = {}
    for keyword, atype in AUDIT_TYPE_KEYWORDS.items():
        if keyword in text_lower:
            scores[atype] = scores.get(atype, 0) + 1
    if scores:
        return max(scores, key=scores.get)
    return 'initial'


def compute_ims_reduction(standards, override_pct=None):
    if override_pct is not None:
        return min(override_pct, MAX_IMS_REDUCTION)
    if len(standards) < 2:
        return 0.0
    total_reduction = 0.0
    pairs = 0
    for i in range(len(standards)):
        for j in range(i + 1, len(standards)):
            pair = (standards[i], standards[j])
            reverse_pair = (standards[j], standards[i])
            reduction = IAF_MD_11_REDUCTION_PCT.get(pair, IAF_MD_11_REDUCTION_PCT.get(reverse_pair, 0.0))
            total_reduction += reduction
            pairs += 1
    if pairs == 0:
        return 0.0
    avg = total_reduction / pairs
    return min(avg, MAX_IMS_REDUCTION)


def round_mandays(value):
    return int(math.ceil(value * 2.0)) / 2.0


def compute_audit_team(total_mandays, audit_type):
    if total_mandays <= 0:
        return []
    if total_mandays <= 1.5:
        return [{'role': 'Lead Auditor', 'count': 1, 'days': total_mandays}]
    if total_mandays <= 4:
        return [
            {'role': 'Lead Auditor', 'count': 1, 'days': round_mandays(total_mandays * 0.6)},
            {'role': 'Auditor', 'count': 1, 'days': round_mandays(total_mandays * 0.4)},
        ]
    if total_mandays <= 8:
        return [
            {'role': 'Lead Auditor', 'count': 1, 'days': round_mandays(total_mandays * 0.4)},
            {'role': 'Auditor', 'count': 2, 'days': round_mandays(total_mandays * 0.3)},
        ]
    return [
        {'role': 'Lead Auditor', 'count': 1, 'days': round_mandays(total_mandays * 0.3)},
        {'role': 'Auditor', 'count': 2, 'days': round_mandays(total_mandays * 0.35)},
    ]


def resolve_standard_key(text):
    text_lower = text.strip().lower()
    if text_lower in STANDARD_KEY_FROM_TEXT:
        return STANDARD_KEY_FROM_TEXT[text_lower]
    m = re.search(r'ISO\s*(\d{4,5}(?:-\d+)?)', text, re.I)
    if m:
        num = m.group(1).replace('-', '')
        key = 'iso_' + num
        if key in STANDARD_DISPLAY_NAMES:
            return key
    return None


def compute_mandays(
    standards,
    audit_type='initial',
    employee_count=None,
    risk_categories=None,
    site_count=1,
    base_mandays_from_docx=None,
    ims_reduction_override=None,
    manday_docx_text=None,
):
    if isinstance(standards, str):
        standards = [standards]
    if risk_categories is None:
        risk_categories = {}
    if base_mandays_from_docx is None:
        base_mandays_from_docx = {}
    if audit_type not in AUDIT_TYPE_MULTIPLIERS:
        audit_type = 'initial'
    type_mul = AUDIT_TYPE_MULTIPLIERS[audit_type]

    if manday_docx_text and not employee_count:
        em = re.search(r'(?:employee|personnel|staff|headcount).{0,20}?(\d+)', manday_docx_text, re.I)
        if em:
            employee_count = int(em.group(1))

    if not employee_count:
        employee_count = 50

    base_per_standard = {}
    for std in standards:
        if std in base_mandays_from_docx and base_mandays_from_docx[std] > 0:
            base_per_standard[std] = base_mandays_from_docx[std]
        else:
            risk = risk_categories.get(std, 'medium')
            md = lookup_base_mandays(std, employee_count, risk)
            if md is not None:
                base_per_standard[std] = md
            else:
                base_per_standard[std] = 4

    if not base_per_standard:
        base_per_standard[standards[0]] = 4

    total_base = sum(base_per_standard.values())
    ims_reduction = 0.0
    if len(standards) >= 2:
        ims_reduction = compute_ims_reduction(standards, ims_reduction_override)

    total_after_ims = total_base * (1.0 - ims_reduction)
    total_final = total_after_ims * type_mul
    total_final = max(total_final, 1.0)
    total_final = round_mandays(total_final) if site_count <= 1 else round_mandays(total_final * site_count)
    total_final = max(total_final, 1.0)

    total_per_standard = {}
    if base_per_standard:
        total_base_safe = max(total_base, 0.1)
        for std, base in base_per_standard.items():
            ratio = base / total_base_safe
            total_per_standard[std] = round_mandays(ratio * total_final)

    team = compute_audit_team(total_final, audit_type)

    notes = []
    if len(standards) >= 2:
        notes.append(f'IAF MD 11 IMS reduction: {ims_reduction * 100:.0f}%')
    if audit_type != 'initial':
        notes.append(f'Multiplier for {audit_type.replace("_", " ")}: {type_mul:.2f}')
    if site_count > 1:
        notes.append(f'Site multiplier: {site_count} sites')

    return {
        'standards': standards,
        'audit_type': audit_type,
        'audit_type_label': audit_type.replace('_', ' ').title(),
        'base_per_standard': base_per_standard,
        'total_base_mandays': total_base,
        'ims_reduction_pct': round(ims_reduction * 100, 1),
        'total_mandays': total_final,
        'mandays_per_standard': total_per_standard,
        'employee_count': employee_count,
        'site_count': site_count,
        'audit_type_multiplier': type_mul,
        'team_composition': team,
        'notes': notes,
    }
