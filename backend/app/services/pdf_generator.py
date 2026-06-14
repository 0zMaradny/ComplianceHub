import logging
import os
import re
import shutil
import subprocess

logger = logging.getLogger(__name__)

import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

FONT_DIR = '/usr/share/fonts/truetype/liberation'
ARABIC_FONT_DIR = '/usr/share/fonts/truetype/noto'
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'tuv_logo.png')

FONT_REGULAR = os.path.join(FONT_DIR, 'LiberationSans-Regular.ttf')
FONT_BOLD = os.path.join(FONT_DIR, 'LiberationSans-Bold.ttf')
FONT_ITALIC = os.path.join(FONT_DIR, 'LiberationSans-Italic.ttf')
FONT_BI = os.path.join(FONT_DIR, 'LiberationSans-BoldItalic.ttf')

ARABIC_FONT_REGULAR = os.path.join(ARABIC_FONT_DIR, 'NotoNaskhArabic-Regular.ttf')
ARABIC_FONT_BOLD = os.path.join(ARABIC_FONT_DIR, 'NotoNaskhArabic-Bold.ttf')

ARABIC_RANGE = set(range(0x0600, 0x06FF + 1)) | set(range(0x0750, 0x077F + 1)) | set(range(0x08A0, 0x08FF + 1)) | set(range(0xFE70, 0xFEFF + 1)) | set(range(0xFB50, 0xFDFF + 1))


def _has_arabic(text: str) -> bool:
    return any(ord(c) in ARABIC_RANGE for c in text)

TUV_BLUE = (0, 61, 122)
TUV_RED = (183, 18, 52)
DARK_GRAY = (51, 51, 51)
LIGHT_GRAY = (240, 240, 240)
MEDIUM_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)


class AuditPDF(FPDF):
    def __init__(self, doc_type_label='Document', standard=''):
        super().__init__('P', 'mm', 'A4')
        self.doc_type_label = doc_type_label
        self.standard = standard
        if os.path.exists(FONT_REGULAR):
            self.add_font('Sans', '', FONT_REGULAR)
            self.add_font('Sans', 'B', FONT_BOLD)
            self.add_font('Sans', 'I', FONT_ITALIC)
            self.add_font('Sans', 'BI', FONT_BI)
        if os.path.exists(ARABIC_FONT_REGULAR):
            self.add_font('Arabic', '', ARABIC_FONT_REGULAR)
            self.add_font('Arabic', 'B', ARABIC_FONT_BOLD)
        self._arabic_mode = False

    def _switch_font_ar(self, style='', size=10):
        self.set_font('Arabic', style, size)
        self._arabic_mode = True

    def _font_for(self, text, style='', size=10):
        if _has_arabic(str(text)):
            self._switch_font_ar(style, size)
        else:
            self.set_font('Sans', style, size)
            self._arabic_mode = False

    def _prepare_text(self, text):
        s = str(text)
        if _has_arabic(s):
            return get_display(arabic_reshaper.reshape(s))
        return s

    def multi_cell(self, w, h, text, *a, **kw):
        self._font_for(text)
        super().multi_cell(w, h, self._prepare_text(text), *a, **kw)

    def cell(self, w, h=0, text='', *a, **kw):
        self._font_for(text)
        super().cell(w, h, self._prepare_text(text), *a, **kw)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Sans', 'I', 8)
        self.set_text_color(*MEDIUM_GRAY)
        self.cell(0, 5, f'{self.doc_type_label}  |  {self.standard}', align='L')
        self.ln(8)
        self.set_draw_color(*TUV_BLUE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font('Sans', 'I', 8)
        self.set_text_color(*MEDIUM_GRAY)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def cover_page(self, title, client_name, audit_date, standard, extra=None):
        self.add_page()
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 155, 12, 35)
        self.set_font('Sans', 'B', 24)
        self.set_text_color(*TUV_BLUE)
        self.ln(55)
        self.multi_cell(0, 12, title, align='C')
        self.ln(4)
        self.set_draw_color(*TUV_BLUE)
        self.set_line_width(0.5)
        self.line(50, self.get_y(), 160, self.get_y())
        self.ln(10)
        self.set_font('Sans', '', 13)
        self.set_text_color(*DARK_GRAY)
        for label, value in [('Client', client_name), ('Standard', standard), ('Date', audit_date)]:
            self.cell(0, 8, f'{label}:  {value}', align='C', new_x='LMARGIN', new_y='NEXT')
        if extra:
            self.ln(4)
            self.set_font('Sans', '', 11)
            for k, v in extra:
                self.cell(0, 7, f'{k}:  {v}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(20)
        self.set_font('Sans', 'I', 10)
        self.set_text_color(*MEDIUM_GRAY)
        self.multi_cell(0, 5, 'TUV AUSTRIA  |  Audit & Compliance Document', align='C')

    def section_title(self, text):
        self.set_font('Sans', 'B', 13)
        self.set_text_color(*TUV_BLUE)
        self.ln(4)
        self.cell(0, 8, text, new_x='LMARGIN', new_y='NEXT')
        self.set_draw_color(*TUV_BLUE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def sub_title(self, text):
        self.set_font('Sans', 'B', 11)
        self.set_text_color(*DARK_GRAY)
        self.cell(0, 7, text, new_x='LMARGIN', new_y='NEXT')
        self.ln(1)

    def body_text(self, text):
        self.set_font('Sans', '', 10)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font('Sans', '', 10)
        self.set_text_color(*DARK_GRAY)
        bullet_char = chr(8226)
        self.cell(5, 5, bullet_char)
        self.multi_cell(0, 5, text)
        self.ln(1)

    def kv_row(self, key, value, indent=0):
        self.set_x(self.l_margin + indent)
        self.set_font('Sans', 'B', 10)
        self.set_text_color(*TUV_BLUE)
        kw = self.get_string_width(f'{key}: ') + 2
        self.cell(kw, 6, f'{key}: ')
        self.set_font('Sans', '', 10)
        self.set_text_color(*DARK_GRAY)
        self.multi_cell(0, 6, str(value))
        self.ln(1)

    def table_header(self, cols):
        self.set_font('Sans', 'B', 9)
        self.set_fill_color(*TUV_BLUE)
        self.set_text_color(*WHITE)
        for w, label in cols:
            self.cell(w, 8, label, border=1, fill=True, align='C')
        self.ln()

    def table_row(self, cols, fill=False):
        self.set_font('Sans', '', 8)
        if fill:
            self.set_fill_color(*LIGHT_GRAY)
        self.set_text_color(*DARK_GRAY)
        for w, val in cols:
            self.cell(w, 7, str(val)[:40], border=1, fill=fill, align='C' if w < 30 else 'L')
        self.ln()

    def table_cell(self, w, h, text, bold=False, fill=False, align='L'):
        self.set_font('Sans', 'B' if bold else '', 8)
        if fill:
            self.set_fill_color(*LIGHT_GRAY)
        self.set_text_color(*DARK_GRAY)
        self.cell(w, h, str(text)[:60], border=1, fill=fill, align=align)
        return self

    def info_block(self, data, keys):
        for k in keys:
            v = data.get(k)
            if v:
                self.kv_row(k.replace('_', ' ').title(), v)

    def status_badge(self, status):
        colors = {
            'Conformant': (0, 128, 0), 'Partially Conformant': (200, 160, 0),
            'Non-Conformant': (200, 0, 0), 'Not Reviewed': (128, 128, 128),
            'Major': (200, 0, 0), 'Minor': (200, 160, 0), 'N/A': (128, 128, 128),
            'Open': (200, 0, 0), 'Closed': (0, 128, 0), 'In Progress': (200, 160, 0),
            'Certified': (0, 128, 0), 'Conditional': (200, 160, 0), 'Not Certified': (200, 0, 0),
        }
        c = colors.get(status, DARK_GRAY)
        self.set_font('Sans', 'B', 8)
        self.set_text_color(*c)
        self.cell(30, 6, status, align='C')
        self.set_text_color(*DARK_GRAY)


def safe_str(v):
    return str(v) if v is not None else ''


def _generate_audit_plan(data, output_path, stage_label):
    pdf = AuditPDF(f'Audit Plan - {stage_label}', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    pdf.cover_page(
        f'AUDIT PLAN\n{stage_label}',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', '')),
        [('Report Date', safe_str(data.get('report_date', ''))),
         ('Language', safe_str(data.get('language', '')))]
    )

    pdf.add_page()
    pdf.section_title('Audit Information')
    pdf.info_block(data, ['client_name', 'audit_date', 'standard', 'stage', 'language', 'report_date'])
    pdf.ln(2)

    scope = data.get('audit_scope')
    if scope:
        pdf.section_title('Audit Scope')
        pdf.body_text(scope)

    pdf.ln(2)
    pdf.section_title('Audit Team')
    team = data.get('audit_team') or []
    if team:
        pdf.table_header([(50, 'Name'), (80, 'Role'), (20, 'Days')])
        for m in team:
            pdf.table_row([(50, safe_str(m.get('name', ''))),
                           (80, safe_str(m.get('role', ''))),
                           (20, str(m.get('days', '')))])
        pdf.ln(2)

    objectives = data.get('audit_objectives') or []
    if objectives:
        pdf.section_title('Audit Objectives')
        for o in objectives:
            pdf.bullet(o)

    criteria = data.get('audit_criteria') or []
    if criteria:
        pdf.section_title('Audit Criteria')
        for c in criteria:
            pdf.bullet(c)

    confidentiality = data.get('confidentiality')
    if confidentiality:
        pdf.section_title('Confidentiality')
        pdf.body_text(confidentiality)

    schedule = data.get('daily_schedule') or []
    if schedule:
        pdf.add_page()
        pdf.section_title('Daily Schedule')
        pdf.table_header([(10, 'Day'), (22, 'Date'), (22, 'Time'), (60, 'Activity'), (40, 'Auditee'), (30, 'Auditor'), (16, 'Clause')])
        for s in schedule:
            pdf.table_row([(10, str(s.get('day', ''))),
                           (22, safe_str(s.get('date', ''))),
                           (22, safe_str(s.get('time', ''))),
                           (60, safe_str(s.get('activity', ''))),
                           (40, safe_str(s.get('auditee', ''))),
                           (30, safe_str(s.get('auditor', ''))),
                           (16, safe_str(s.get('clause', '')))],
                          fill=s.get('day', 0) % 2 == 0)

    pdf.output(output_path)
    return output_path


def generate_audit_plan_stage_1(data, output_path):
    return _generate_audit_plan(data, output_path, 'Stage 1 - Readiness Review')


def generate_audit_plan_stage_2(data, output_path):
    return _generate_audit_plan(data, output_path, 'Stage 2 - Certification Audit')


def generate_participation_list(data, output_path):
    pdf = AuditPDF('Participation List', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    pdf.cover_page(
        'PARTICIPATION LIST',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', ''))
    )
    pdf.add_page()
    pdf.section_title('Participants')
    pdf.info_block(data, ['client_name', 'audit_date', 'standard'])

    pdf.ln(2)
    participants = data.get('participants') or []
    pdf.table_header([(40, 'Name'), (50, 'Company'), (40, 'Department'), (30, 'Closing'), (30, 'Signature')])
    for p in participants:
        pdf.table_row([(40, safe_str(p.get('name', ''))),
                       (50, safe_str(p.get('company', ''))),
                       (40, safe_str(p.get('department', ''))),
                       (30, safe_str(p.get('closing_meeting', ''))),
                       (30, safe_str(p.get('signature', '')))])
    notes = data.get('notes')
    if notes:
        pdf.ln(4)
        pdf.section_title('Notes')
        pdf.body_text(notes)
    pdf.output(output_path)
    return output_path


def generate_audit_report(data, output_path):
    pdf = AuditPDF('Audit Report', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    extra = [('Report #', safe_str(data.get('report_number', ''))),
             ('Lead Auditor', safe_str(data.get('lead_auditor', ''))),
             ('Report Date', safe_str(data.get('report_date', '')))]
    pdf.cover_page(
        'AUDIT REPORT',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', '')),
        extra
    )

    pdf.add_page()
    pdf.section_title('Scope')
    scope = data.get('scope')
    if scope:
        pdf.body_text(scope)
    pdf.info_block(data, ['client_name', 'audit_date', 'standard', 'report_number', 'lead_auditor'])

    methodology = data.get('methodology') or {}
    pdf.ln(2)
    pdf.section_title('Methodology')
    for k in ('approach', 'sampling', 'criteria', 'methods'):
        v = methodology.get(k)
        if v:
            pdf.kv_row(k.replace('_', ' ').title(), v)

    findings = data.get('findings_summary')
    if findings:
        pdf.ln(2)
        pdf.section_title('Findings Summary')
        pdf.body_text(findings)

    positive = data.get('positive_findings') or []
    if positive:
        pdf.section_title('Positive Findings')
        for p in positive:
            pdf.bullet(p)

    ofi = data.get('opportunities_for_improvement') or []
    if ofi:
        pdf.section_title('Opportunities for Improvement')
        for o in ofi:
            pdf.bullet(o)

    ncs = data.get('nonconformities') or []
    if ncs:
        pdf.add_page()
        pdf.section_title('Nonconformities')
        pdf.table_header([(50, 'Clause'), (20, 'Severity'), (80, 'Description'), (30, 'Due Date')])
        for nc in ncs:
            pdf.table_row([(50, safe_str(nc.get('clause', ''))),
                           (20, safe_str(nc.get('severity', ''))),
                           (80, safe_str(nc.get('description', ''))[:80]),
                           (30, safe_str(nc.get('due_date', '')))],
                          fill=nc.get('severity') == 'Major')

    conclusion = data.get('conclusion')
    if conclusion:
        pdf.section_title('Conclusion')
        pdf.body_text(conclusion)

    team = data.get('audit_team') or []
    if team:
        pdf.ln(2)
        pdf.section_title('Audit Team')
        pdf.table_header([(50, 'Name'), (80, 'Role'), (20, 'Days')])
        for m in team:
            pdf.table_row([(50, safe_str(m.get('name', ''))),
                           (80, safe_str(m.get('role', ''))),
                           (20, str(m.get('days', '')))])

    pdf.output(output_path)
    return output_path


def generate_iso_checklist(data, output_path):
    pdf = AuditPDF('ISO Checklist', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    pdf.cover_page(
        'ISO CHECKLIST',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', '')),
        [('Auditor', safe_str(data.get('auditor', '')))]
    )

    sections = data.get('sections') or []
    if sections:
        pdf.add_page()
        pdf.section_title('Checklist — Questions & Evidence')
        pdf.table_header([(14, 'Clause'), (86, 'Audit Questions'), (86, 'Evidence to Check')])
        for sec in sections:
            y_before = pdf.get_y()
            if y_before > 250:
                pdf.add_page()
                pdf.table_header([(14, 'Clause'), (86, 'Audit Questions'), (86, 'Evidence to Check')])
            aq = safe_str(sec.get('audit_questions', ''))[:80]
            ec = safe_str(sec.get('evidence_to_check', ''))[:80]
            pdf.table_row([(14, safe_str(sec.get('clause', ''))[:14]),
                           (86, aq), (86, ec)])

        pdf.add_page()
        pdf.section_title('Checklist — Findings & Status')
        pdf.table_header([(14, 'Clause'), (100, 'Findings / Observations'), (36, 'Status'), (36, 'Reference')])
        for sec in sections:
            y_before = pdf.get_y()
            if y_before > 250:
                pdf.add_page()
                pdf.table_header([(14, 'Clause'), (100, 'Findings / Observations'), (36, 'Status'), (36, 'Reference')])
            findings_text = safe_str(sec.get('evidence', ''))
            notes = sec.get('notes', '')
            if notes:
                findings_text += ' | Notes: ' + safe_str(notes)
            pdf.table_row([(14, safe_str(sec.get('clause', ''))[:14]),
                           (100, findings_text[:100]),
                           (36, safe_str(sec.get('status', ''))),
                           (36, safe_str(sec.get('reference', ''))[:36])])
    overall = data.get('overall_assessment')
    if overall:
        pdf.ln(4)
        pdf.section_title('Overall Assessment')
        pdf.body_text(overall)

    pdf.output(output_path)
    return output_path


def generate_certificate_text(data, output_path):
    pdf = AuditPDF('Certificate Text', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    pdf.cover_page(
        'CERTIFICATE TEXT',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', '')),
        [('Certificate #', safe_str(data.get('certificate_number', ''))),
         ('Lead Auditor', safe_str(data.get('lead_auditor', '')))]
    )

    pdf.add_page()
    pdf.section_title('Certificate Information')
    pdf.info_block(data, ['client_name', 'certificate_number', 'standard', 'audit_date',
                          'scope', 'lead_auditor', 'certification_body',
                          'issue_date', 'expiry_date', 'authorized_signatory'])
    decision = data.get('certification_decision')
    if decision:
        pdf.ln(2)
        pdf.section_title('Certification Decision')
        pdf.set_font('Sans', 'B', 12)
        pdf.status_badge(decision)
        pdf.ln(8)

    pdf.output(output_path)
    return output_path


def generate_tnl(data, output_path):
    pdf = AuditPDF('Test & Nonconformity Log', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    pdf.cover_page(
        'TEST & NONCONFORMITY LOG',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', ''))
    )

    entries = data.get('entries') or []
    summary = data.get('summary') or {}

    pdf.add_page()
    if summary:
        pdf.section_title('Summary')
        pdf.kv_row('Total NCs', str(summary.get('total_nc', 0)))
        pdf.kv_row('Major', str(summary.get('major', 0)))
        pdf.kv_row('Minor', str(summary.get('minor', 0)))
        pdf.kv_row('OFIs', str(summary.get('ofi', 0)))
        pdf.kv_row('Observations', str(summary.get('observations', 0)))

    if entries:
        pdf.ln(2)
        pdf.section_title('Entries')
        pdf.table_header([(20, '#'), (18, 'Clause'), (18, 'Type'), (60, 'Description'),
                          (18, 'Severity'), (28, 'Auditee'), (22, 'Due'), (16, 'Status')])
        for e in entries:
            pdf.table_row([(20, safe_str(e.get('tnl_number', ''))),
                           (18, safe_str(e.get('clause', ''))[:12]),
                           (18, safe_str(e.get('type', ''))),
                           (60, safe_str(e.get('description', ''))[:60]),
                           (18, safe_str(e.get('severity', ''))),
                           (28, safe_str(e.get('auditee', ''))),
                           (22, safe_str(e.get('due_date', ''))),
                           (16, safe_str(e.get('status', '')))])

    pdf.output(output_path)
    return output_path


def generate_certificate(data, output_path):
    pdf = AuditPDF('Certificate', safe_str(data.get('standard', '')))
    pdf.alias_nb_pages()
    pdf.cover_page(
        'CERTIFICATE',
        safe_str(data.get('client_name', '')),
        safe_str(data.get('audit_date', '')),
        safe_str(data.get('standard', '')),
        [('Certificate #', safe_str(data.get('certificate_number', '')))]
    )

    pdf.add_page()
    pdf.section_title('Certification Details')
    pdf.info_block(data, ['client_name', 'certificate_number', 'standard', 'audit_date',
                          'scope', 'lead_auditor', 'certification_body',
                          'issue_date', 'expiry_date', 'authorized_signatory'])

    decision = data.get('certification_decision')
    if decision:
        pdf.ln(2)
        pdf.section_title('Decision')
        pdf.set_font('Sans', 'B', 14)
        pdf.status_badge(decision)
        pdf.ln(8)

    conditions = data.get('conditions') or []
    if conditions:
        pdf.section_title('Conditions')
        for c in conditions:
            pdf.bullet(c)

    pdf.output(output_path)
    return output_path


GENERATORS = {
    'Audit_Plan_Stage_1': generate_audit_plan_stage_1,
    'Audit_Plan_Stage_2': generate_audit_plan_stage_2,
    'Participation_List': generate_participation_list,
    'Audit_Report': generate_audit_report,
    'ISO_Checklist': generate_iso_checklist,
    'Certificate_Text': generate_certificate_text,
    'TNL': generate_tnl,
    'Certificate': generate_certificate,
}


def generate_pdf_file(doc_type, data, output_dir, standard_key=None):
    os.makedirs(output_dir, exist_ok=True)
    raw = data.get('client_name', 'Client')
    safe_name = re.sub(r'[^\w\s-]', '', raw).strip().replace(' ', '_')[:60] or 'Client'
    filename = f'{doc_type}_{safe_name}.pdf'
    output_path = os.path.join(output_dir, filename)
    generator = GENERATORS.get(doc_type)
    if generator:
        result = generator(data, output_path)
        if result and os.path.exists(result):
            return result
    return None


# ── DOCX → PDF Converter ────────────────────────────────────────────────────

PDF_AVAILABLE = False
PDF_ENGINE = None

if shutil.which('libreoffice') or shutil.which('soffice'):
    PDF_AVAILABLE = True
    PDF_ENGINE = 'libreoffice'
elif shutil.which('docx2pdf'):
    try:
        __import__('docx2pdf')
        PDF_AVAILABLE = True
        PDF_ENGINE = 'docx2pdf'
    except ImportError:
        pass


def convert_to_pdf(docx_path: str) -> str | None:
    if not PDF_AVAILABLE:
        return None
    pdf_path = docx_path.rsplit('.', 1)[0] + '.pdf'
    out_dir = os.path.dirname(docx_path)
    try:
        if PDF_ENGINE == 'libreoffice':
            subprocess.run(
                ['libreoffice', '--headless', '--convert-to', 'pdf',
                 '--outdir', out_dir, docx_path],
                capture_output=True, timeout=60, check=True,
                env={**os.environ, 'HOME': os.environ.get('TMPDIR', '/tmp')},
            )
        elif PDF_ENGINE == 'docx2pdf':
            from docx2pdf import convert as _convert
            _convert(docx_path, pdf_path)
        if os.path.exists(pdf_path):
            return pdf_path
    except Exception as e:
        logger.warning("convert_to_pdf failed: %s", e)
    return None
