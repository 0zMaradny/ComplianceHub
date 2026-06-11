import csv
import io
import logging
from datetime import datetime, timedelta

from app.services.pdf_generator import AuditPDF
from app.services.audit_workflow import _PROJECTS, _NCS, _CAPAS

logger = logging.getLogger(__name__)

STANDARD_LABELS = {
    'iso_9001': 'ISO 9001:2015 — Quality',
    'iso_14001': 'ISO 14001:2015 — Environmental',
    'iso_45001': 'ISO 45001:2018 — OH&S',
    'iso_50001': 'ISO 50001:2018 — Energy',
    'iso_13485': 'ISO 13485:2016 — Medical Devices',
    'iso_27001': 'ISO 27001:2022 — InfoSec',
    'iso_20000': 'ISO 20000-1:2018 — Service Mgmt',
    'iso_22301': 'ISO 22301:2019 — Business Continuity',
    'iso_37301': 'ISO 37301:2021 — Compliance',
    'iso_42001': 'ISO 42001:2023 — AI Management',
    'iso_30401': 'ISO 30401:2018 — Knowledge Mgmt',
    'iso_27701': 'ISO 27701:2025 — Privacy',
    'iso_31000': 'ISO 31000:2018 — Risk',
    'iso_10002': 'ISO 10002:2018 — Complaints',
}


def generate_compliance_summary() -> bytes:
    """Generate a PDF compliance summary report across all standards."""
    pdf = AuditPDF(doc_type_label='Compliance Summary', standard='All Standards')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.cover_page(
        title='Compliance Summary Report',
        client='ComplianceHub',
        date=datetime.now().strftime('%Y-%m-%d'),
        standard='Multi-Standard Overview',
        extra='Auto-generated dashboard export',
    )
    pdf.add_page()

    # Aggregate data
    projects = list(_PROJECTS.values())
    ncs = list(_NCS.values())
    capas = list(_CAPAS.values())

    # ── Key Stats ──
    pdf.section_title('Key Statistics')
    active_projects = [p for p in projects if p.status == 'active']
    completed_projects = [p for p in projects if p.status == 'completed']
    open_ncs = [n for n in ncs if n.status == 'open']
    pending_capas = [c for c in capas if c.status in ('draft', 'in_progress')]

    pdf.kv_row('Total Projects', str(len(projects)))
    pdf.kv_row('Active Projects', str(len(active_projects)))
    pdf.kv_row('Completed Projects', str(len(completed_projects)))
    pdf.kv_row('Open Nonconformities', str(len(open_ncs)))
    pdf.kv_row('Pending CAPAs', str(len(pending_capas)))
    pdf.ln(4)

    # ── Projects Table ──
    if projects:
        pdf.section_title('Project Overview')
        pdf.table_header([(60, 'Project'), (25, 'Status'), (15, 'Gate'), (40, 'Standards'), (25, 'Open NCs')])
        for p in sorted(projects, key=lambda x: x.created_at or '', reverse=True):
            stds = ', '.join(s.replace('iso_', 'ISO ').replace('_', ':') for s in (p.standards or []))
            nc_count = len([n for n in ncs if n.project_id == p.id and n.status == 'open'])
            pdf.table_row([
                (p.title[:30], 60),
                (p.status, 25),
                (str(p.current_gate), 15),
                (stds[:30], 40),
                (str(nc_count), 25),
            ])
        pdf.ln(6)

    # ── NC by Severity ──
    if ncs:
        pdf.section_title('Nonconformities by Severity')
        major = len([n for n in ncs if n.severity == 'Major'])
        minor = len([n for n in ncs if n.severity == 'Minor'])
        ofi = len([n for n in ncs if n.severity not in ('Major', 'Minor')])
        pdf.table_header([(50, 'Severity'), (40, 'Count')])
        pdf.table_row([('Major', 50), (str(major), 40)])
        pdf.table_row([('Minor', 50), (str(minor), 40)])
        pdf.table_row([('OFI / Other', 50), (str(ofi), 40)])
        pdf.ln(4)

    # ── CAPA Status ──
    if capas:
        pdf.section_title('CAPA Status')
        draft = len([c for c in capas if c.status == 'draft'])
        in_progress = len([c for c in capas if c.status == 'in_progress'])
        verified = len([c for c in capas if c.status == 'verified'])
        pdf.table_header([(80, 'Status'), (40, 'Count')])
        pdf.table_row([('Draft', 80), (str(draft), 40)])
        pdf.table_row([('In Progress', 80), (str(in_progress), 40)])
        pdf.table_row([('Verified / Closed', 80), (str(verified), 40)])
        pdf.ln(4)

    # ── Standards Coverage ──
    pdf.section_title('Standards Coverage')
    used_standards = set()
    for p in projects:
        for s in (p.standards or []):
            used_standards.add(s)
    for std in sorted(used_standards):
        label = STANDARD_LABELS.get(std, std)
        pdf.bullet(label)

    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
    return pdf_bytes


def generate_project_overview(project_id: str = '') -> bytes:
    """Generate a PDF project-overview report for one or all projects."""
    pdf = AuditPDF(doc_type_label='Project Overview', standard='Multi-Standard')
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.cover_page(
        title='Project Overview Report',
        client='ComplianceHub',
        date=datetime.now().strftime('%Y-%m-%d'),
        standard='Multi-Standard',
        extra='Project status and health summary',
    )
    pdf.add_page()

    ncs = list(_NCS.values())
    capas = list(_CAPAS.values())
    projects = list(_PROJECTS.values())
    if project_id:
        projects = [p for p in projects if p.id == project_id]

    for p in projects:
        p_ncs = [n for n in ncs if n.project_id == p.id]
        p_capas = [c for c in capas if c.project_id == p.id]
        open_major = len([n for n in p_ncs if n.status == 'open' and n.severity == 'Major'])
        open_minor = len([n for n in p_ncs if n.status == 'open' and n.severity == 'Minor'])
        pending_capa = len([c for c in p_capas if c.status in ('draft', 'in_progress')])

        health_score = 100 - open_major * 15 - open_minor * 5 - pending_capa * 3
        health_score = max(0, min(100, health_score))

        pdf.section_title(p.title[:50])
        pdf.kv_row('Status', p.status)
        pdf.kv_row('Standards', ', '.join(s.replace('iso_', 'ISO ').replace('_', ':') for s in (p.standards or [])))
        pdf.kv_row('Current Gate', f'{p.current_gate}/6')
        pdf.kv_row('Health Score', f'{health_score}%')
        pdf.kv_row('Open Major NCs', str(open_major))
        pdf.kv_row('Open Minor NCs', str(open_minor))
        pdf.kv_row('Pending CAPAs', str(pending_capa))
        if p.target_date:
            pdf.kv_row('Target Date', p.target_date)
        if p.lead_auditor:
            pdf.kv_row('Lead Auditor', p.lead_auditor)
        pdf.ln(4)

    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
    return pdf_bytes


def generate_csv(dataset: str, months: int = 6, project_id: str = '') -> str:
    """Generate CSV text for a given dataset."""
    ncs = list(_NCS.values())
    capas = list(_CAPAS.values())
    projects = list(_PROJECTS.values())

    if dataset == 'nc_trends':
        return _nc_trends_csv(ncs, months, project_id)
    elif dataset == 'project_health':
        return _project_health_csv(projects, ncs, capas)
    elif dataset == 'capa_metrics':
        return _capa_metrics_csv(capas)
    elif dataset == 'ai_usage':
        return _ai_usage_csv()
    return 'Dataset not found'


def _nc_trends_csv(ncs, months, project_id):
    now = datetime.now()
    month_labels = []
    for i in range(months - 1, -1, -1):
        d = now - timedelta(days=i * 30)
        month_labels.append(d.strftime('%Y-%m'))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Month', 'Major NC', 'Minor NC', 'OFI', 'Closed'])

    major = [0] * months
    minor = [0] * months
    ofi = [0] * months
    closed = [0] * months

    for nc in ncs:
        if project_id and nc.project_id != project_id:
            continue
        if not nc.created_at:
            continue
        try:
            created = datetime.fromisoformat(nc.created_at)
            cm = created.strftime('%Y-%m')
        except (ValueError, TypeError):
            continue
        if cm not in month_labels:
            continue
        idx = month_labels.index(cm)
        if nc.severity == 'Major':
            major[idx] += 1
        elif nc.severity == 'Minor':
            minor[idx] += 1
        else:
            ofi[idx] += 1
        if nc.status == 'closed' and nc.closed_at:
            try:
                closed_dt = datetime.fromisoformat(nc.closed_at)
                clm = closed_dt.strftime('%Y-%m')
                if clm in month_labels:
                    closed[month_labels.index(clm)] += 1
            except (ValueError, TypeError):
                pass

    for i, m in enumerate(month_labels):
        writer.writerow([m, major[i], minor[i], ofi[i], closed[i]])

    return output.getvalue()


def _project_health_csv(projects, ncs, capas):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Project', 'Status', 'Gate', 'Health Score', 'Open Major NCs', 'Open Minor NCs', 'Pending CAPAs'])
    for p in projects:
        p_ncs = [n for n in ncs if n.project_id == p.id]
        p_capas = [c for c in capas if c.project_id == p.id]
        open_major = len([n for n in p_ncs if n.status == 'open' and n.severity == 'Major'])
        open_minor = len([n for n in p_ncs if n.status == 'open' and n.severity == 'Minor'])
        pending = len([c for c in p_capas if c.status in ('draft', 'in_progress')])
        score = max(0, min(100, 100 - open_major * 15 - open_minor * 5 - pending * 3))
        writer.writerow([p.title, p.status, p.current_gate, score, open_major, open_minor, pending])
    return output.getvalue()


def _capa_metrics_csv(capas):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['CAPA ID', 'Project ID', 'Status', 'Owner', 'Due Date', 'Created'])
    for c in capas:
        writer.writerow([c.id, c.project_id, c.status, c.owner, c.due_date, c.created_at])
    return output.getvalue()


def _ai_usage_csv():
    from app.services.ai.router import get_model_performance
    perf = get_model_performance()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Model', 'Total Uses', 'Failures', 'Failure Rate %', 'Avg Quality', 'Avg Response (ms)'])
    for name, p in perf.items():
        writer.writerow([
            name,
            p.get('total_uses', 0),
            p.get('total_failures', 0),
            p.get('failure_rate_pct', 0),
            p.get('avg_quality_score', 0),
            p.get('avg_response_time_ms', 0),
        ])
    return output.getvalue()
