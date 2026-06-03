import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

from app.config import DEFAULT_LOGO_PATH

TUV_BLUE = RGBColor(0x00, 0x3D, 0x7A)
TUV_RED = RGBColor(0xC0, 0x00, 0x00)
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY = RGBColor(0xF2, 0xF2, 0xF2)


def set_cell_shading(cell, color):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)


def add_page_number(doc):
    sect = doc.sections[0]
    footer = sect.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('Page ')
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    fld_char1 = OxmlElement('w:fldChar')
    fld_char1.set(qn('w:fldCharType'), 'begin')
    p.runs[-1]._r.addnext(fld_char1)
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' PAGE '
    fld_char1.addnext(instr)
    fld_char2 = OxmlElement('w:fldChar')
    fld_char2.set(qn('w:fldCharType'), 'end')
    instr.addnext(fld_char2)


def set_col_widths(table, widths_pct, available_inches=6.5):
    available = Inches(available_inches)
    table.autofit = False
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            if i < len(widths_pct):
                cell.width = int(available * widths_pct[i] / 100)


def set_landscape(doc):
    sect = doc.sections[0]
    sect.orientation = WD_ORIENT.LANDSCAPE
    sect.page_width, sect.page_height = sect.page_height, sect.page_width


def setup_document(doc, landscape=False):
    if landscape:
        set_landscape(doc)
    sect = doc.sections[0]
    sect.top_margin = Cm(2.0)
    sect.bottom_margin = Cm(2.0)
    sect.left_margin = Cm(2.5)
    sect.right_margin = Cm(2.5)

    header = sect.header
    header.is_linked_to_previous = False
    hp = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    hp.text = ''
    run = hp.add_run('TÜV AUSTRIA')
    run.bold = True
    run.font.size = Pt(8)
    run.font.color.rgb = TUV_BLUE
    run2 = hp.add_run('  |  Audit Documentation')
    run2.font.size = Pt(8)
    run2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    add_page_number(doc)


def add_header_row(table, headers):
    row = table.rows[0]
    for i, h in enumerate(headers):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = WHITE
        set_cell_shading(cell, '003D7A')


def add_data_row(table, data, bold=False, color=None):
    row = table.add_row()
    for i, val in enumerate(data):
        cell = row.cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(str(val))
        run.font.size = Pt(9)
        run.bold = bold
        if color:
            run.font.color.rgb = color
        if i % 2 == 0:
            set_cell_shading(cell, 'F2F2F2')
    return row


def add_cover_page(doc, title, client_name, standard, date, lead_auditor=''):
    if os.path.exists(DEFAULT_LOGO_PATH):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(DEFAULT_LOGO_PATH, width=Inches(3.0))

    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.font.size = Pt(24)
    run.bold = True
    run.font.color.rgb = TUV_BLUE

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('TÜV AUSTRIA')
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    doc.add_paragraph()

    info_items = [
        ('Client', client_name),
        ('Standard', standard),
        ('Date', date),
    ]
    if lead_auditor:
        info_items.append(('Lead Auditor', lead_auditor))

    for label, value in info_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f'{label}: ')
        run.font.size = Pt(11)
        run.bold = True
        run.font.color.rgb = TUV_BLUE
        run = p.add_run(value)
        run.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('_' * 40)
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('This document is confidential and intended solely for the use of the client.')
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    run.italic = True

    doc.add_page_break()


def add_toc(doc):
    p = doc.add_paragraph()
    run = p.add_run('Table of Contents')
    run.font.size = Pt(16)
    run.bold = True
    run.font.color.rgb = TUV_BLUE
    p.space_after = Pt(12)

    fld_char_begin = OxmlElement('w:fldChar')
    fld_char_begin.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = r' TOC \o "1-3" \h \z \u '
    fld_char_separate = OxmlElement('w:fldChar')
    fld_char_separate.set(qn('w:fldCharType'), 'separate')
    fld_char_end = OxmlElement('w:fldChar')
    fld_char_end.set(qn('w:fldCharType'), 'end')

    p2 = doc.add_paragraph()
    p2.space_after = Pt(4)
    for el in [fld_char_begin, instr, fld_char_separate, fld_char_end]:
        p2._p.append(el)

    doc.add_paragraph()


def add_section_heading(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(14)
    run.bold = True
    run.font.color.rgb = TUV_BLUE
    p.space_after = Pt(6)
    p.space_before = Pt(12)
    return p


def add_sub_heading(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.bold = True
    p.space_after = Pt(4)
    return p


def add_body_text(doc, text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.bold = bold
    p.space_after = Pt(4)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet')
    p.clear()
    run = p.add_run(text)
    run.font.size = Pt(10)
    return p


def add_border_box(doc):
    sect = doc.sections[0]
    sect.left_margin = Cm(1.5)
    sect.right_margin = Cm(1.5)
    sect.top_margin = Cm(1.5)
    sect.bottom_margin = Cm(1.5)
    pg = sect._sectPr
    pgBorders = OxmlElement('w:pgBorders')
    pgBorders.set(qn('w:offsetFrom'), 'page')
    for side, sz, color, space in [
        ('top', '24', '003D7A', '24'),
        ('left', '24', '003D7A', '24'),
        ('bottom', '24', '003D7A', '24'),
        ('right', '24', '003D7A', '24'),
    ]:
        border = OxmlElement(f'w:{side}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), sz)
        border.set(qn('w:color'), color)
        border.set(qn('w:space'), space)
        pgBorders.append(border)
    pg.append(pgBorders)


def generate_audit_plan_stage(data, output_path, stage_label):
    doc = Document()
    setup_document(doc)
    stage = data.get('stage', stage_label)
    add_cover_page(doc, f'Audit Plan - {stage}',
                   data.get('client_name', 'N/A'),
                   data.get('standard', 'N/A'), data.get('audit_date', 'N/A'))

    add_toc(doc)

    add_section_heading(doc, '1. Audit Objectives')
    for obj in data.get('audit_objectives', []):
        add_bullet(doc, obj)

    add_section_heading(doc, '2. Audit Scope')
    add_body_text(doc, data.get('audit_scope', 'N/A'))

    add_section_heading(doc, '3. Audit Criteria')
    for c in data.get('audit_criteria', []):
        add_bullet(doc, c)

    add_section_heading(doc, '4. Audit Team')
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_row(table, ['Name', 'Role', 'Audit Days'])
    for member in data.get('audit_team', []):
        add_data_row(table, [member.get('name', ''), member.get('role', ''), str(member.get('days', ''))])

    add_section_heading(doc, '5. Daily Schedule')
    table = doc.add_table(rows=1, cols=7)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_row(table, ['Day', 'Date', 'Time', 'Activity', 'Auditee', 'Auditor', 'Clause'])
    for entry in data.get('daily_schedule', []):
        add_data_row(table, [
            str(entry.get('day', '')),
            entry.get('date', ''),
            entry.get('time', ''),
            entry.get('activity', ''),
            entry.get('auditee', ''),
            entry.get('auditor', ''),
            entry.get('clause', ''),
        ])

    add_section_heading(doc, '6. Confidentiality')
    add_body_text(doc, data.get('confidentiality', 'All information obtained during this audit shall be treated as confidential.'))

    add_section_heading(doc, '7. Language & Report Date')
    add_body_text(doc, f"Language: {data.get('language', 'English')}")
    add_body_text(doc, f"Report Due: {data.get('report_date', 'N/A')}")

    doc.save(output_path)
    return output_path


def generate_audit_plan_stage_1(data, output_path):
    return generate_audit_plan_stage(data, output_path, 'Stage 1 - Readiness Review')


def generate_audit_plan_stage_2(data, output_path):
    return generate_audit_plan_stage(data, output_path, 'Stage 2 - Certification Audit')


def generate_participation_list(data, output_path):
    doc = Document()
    setup_document(doc)
    add_cover_page(doc, 'Participation List',
                   data.get('client_name', 'N/A'),
                   data.get('standard', 'N/A'),
                   data.get('audit_date', 'N/A'))

    add_section_heading(doc, 'Attendance Record')

    table = doc.add_table(rows=1, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_row(table, ['Name', 'Company', 'Function / Department', 'Closing Meeting', 'Signature'])
    for p in data.get('participants', []):
        add_data_row(table, [
            p.get('name', ''),
            p.get('company', ''),
            p.get('department', ''),
            p.get('closing_meeting', ''),
            p.get('signature', ''),
        ])

    notes = data.get('notes', '')
    if notes:
        doc.add_paragraph()
        add_section_heading(doc, 'Notes')
        add_body_text(doc, notes)

    doc.save(output_path)
    return output_path


def generate_certificate_text(data, output_path):
    doc = Document()
    setup_document(doc)
    add_cover_page(doc, 'Certificate',
                   data.get('client_name', 'N/A'),
                   data.get('standard', 'N/A'),
                   data.get('audit_date', 'N/A'))

    fields = [
        ('Certificate Number', data.get('certificate_number', 'N/A')),
        ('Client', data.get('client_name', 'N/A')),
        ('Standard', data.get('standard', 'N/A')),
        ('Audit Date', data.get('audit_date', 'N/A')),
        ('Scope', data.get('scope', 'N/A')),
        ('Lead Auditor', data.get('lead_auditor', 'N/A')),
        ('Certification Body', data.get('certification_body', 'TÜV AUSTRIA')),
        ('Certification Decision', data.get('certification_decision', 'N/A')),
        ('Issue Date', data.get('issue_date', 'N/A')),
        ('Expiry Date', data.get('expiry_date', 'N/A')),
        ('Authorized Signatory', data.get('authorized_signatory', 'N/A')),
    ]

    add_section_heading(doc, 'Certificate Details')
    for label, value in fields:
        p = doc.add_paragraph()
        run = p.add_run(f'{label}: ')
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = TUV_BLUE
        run = p.add_run(str(value))
        run.font.size = Pt(10)
        p.space_after = Pt(4)

    doc.save(output_path)
    return output_path


def generate_audit_report(data, output_path):
    doc = Document()
    setup_document(doc)
    add_cover_page(doc, 'Audit Report', data.get('client_name', 'N/A'),
                   data.get('standard', 'N/A'), data.get('audit_date', 'N/A'),
                   data.get('lead_auditor', ''))

    add_toc(doc)

    add_section_heading(doc, '1. General Information')
    info = [
        ('Report Number', data.get('report_number', 'N/A')),
        ('Client', data.get('client_name', 'N/A')),
        ('Audit Date', data.get('audit_date', 'N/A')),
        ('Standard', data.get('standard', 'N/A')),
        ('Scope', data.get('scope', 'N/A')),
        ('Lead Auditor', data.get('lead_auditor', 'N/A')),
    ]
    for label, val in info:
        add_body_text(doc, f'{label}: {val}', bold=False)

    add_section_heading(doc, '2. Audit Team')
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    add_header_row(table, ['Name', 'Role', 'Audit Days'])
    for member in data.get('audit_team', []):
        add_data_row(table, [member.get('name', ''), member.get('role', ''), str(member.get('days', ''))])

    add_section_heading(doc, '3. Summary of Findings')
    add_body_text(doc, data.get('findings_summary', ''))

    if data.get('positive_findings'):
        add_sub_heading(doc, '3.1 Positive Findings')
        for pf in data['positive_findings']:
            add_bullet(doc, pf)

    if data.get('opportunities_for_improvement'):
        add_sub_heading(doc, '3.2 Opportunities for Improvement')
        for ofi in data['opportunities_for_improvement']:
            add_bullet(doc, ofi)

    if data.get('nonconformities'):
        add_sub_heading(doc, '3.3 Nonconformities')
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        add_header_row(table, ['Clause', 'Severity', 'Description', 'Due Date'])
        for nc in data['nonconformities']:
            sev = nc.get('severity', '')
            row_color = TUV_RED if sev in ('Major', 'Minor') else None
            add_data_row(table, [
                nc.get('clause', ''),
                sev,
                nc.get('description', ''),
                nc.get('due_date', ''),
            ], color=row_color)

    add_section_heading(doc, '4. Conclusion')
    add_body_text(doc, data.get('conclusion', ''))

    p = doc.add_paragraph()
    run = p.add_run(f"\nReport Date: {data.get('report_date', 'N/A')}")
    run.font.size = Pt(10)

    doc.save(output_path)
    return output_path


def generate_iso_checklist(data, output_path, template_path=None):
    if template_path and os.path.exists(template_path):
        doc = Document(template_path)
        setup_document(doc, landscape=True)
        sections = data.get('sections', [])

        injected = False
        for table in doc.tables:
            if len(table.rows) < 3:
                continue
            first_row_text = ' '.join(c.text for c in table.rows[0].cells).lower()
            num_cols = len(table.rows[0].cells)

            if num_cols >= 5:
                _inject_into_template_table(table, sections)
                set_col_widths(table, [12, 22, 12, 28, 14, 12], available_inches=9.5)
                injected = True
                break

        overall = data.get('overall_assessment', '')
        if overall:
            for p in doc.paragraphs:
                text = p.text.strip().lower()
                if ('overall' in text or 'assessment' in text) and len(text) < 40:
                    run = p.add_run(f'\n{overall}')
                    run.font.size = Pt(10)
                    break
        doc.save(output_path)
        return output_path

    doc = Document()
    setup_document(doc, landscape=True)
    add_cover_page(doc, 'ISO Compliance Checklist',
                   data.get('client_name', 'N/A'),
                   data.get('standard', 'N/A'),
                   data.get('audit_date', 'N/A'),
                   data.get('auditor', ''))

    add_section_heading(doc, 'Checklist Results')

    table = doc.add_table(rows=1, cols=6)
    table.style = 'Table Grid'
    add_header_row(table, ['Clause', 'Requirement', 'Status', 'Evidence', 'Notes', 'Reference'])
    for section in data.get('sections', []):
        status = section.get('status', '')
        checkbox = '☐'
        row_color = None
        if status == 'Conformant':
            checkbox = '☒'
        elif status == 'Non-Conformant':
            checkbox = '☒'
            row_color = TUV_RED
        elif status == 'Partially Conformant':
            checkbox = '☒'
            row_color = RGBColor(0xCC, 0x7A, 0x00)
        add_data_row(table, [
            section.get('clause', ''),
            section.get('requirement', ''),
            f'{checkbox} {status}',
            section.get('evidence', ''),
            section.get('notes', ''),
            section.get('reference', ''),
        ], color=row_color)

    doc.add_paragraph()
    add_section_heading(doc, 'Overall Assessment')
    add_body_text(doc, data.get('overall_assessment', ''))

    doc.save(output_path)
    return output_path


def _inject_into_template_table(table, sections, data_row_start=1):
    for i, section in enumerate(sections):
        row_idx = data_row_start + i
        if row_idx >= len(table.rows):
            break
        row = table.rows[row_idx]
        status = section.get('status', '')
        checkbox = '☐'
        row_color = None
        if status == 'Conformant':
            checkbox = '☒'
        elif status == 'Non-Conformant':
            checkbox = '☒'
            row_color = TUV_RED
        elif status == 'Partially Conformant':
            checkbox = '☒'
            row_color = RGBColor(0xCC, 0x7A, 0x00)

        col_map = [
            ('clause', 0),
            ('requirement', 1),
            ('title', 1),
            ('status', 2),
            ('evidence', 3),
            ('notes', 4),
            ('reference', 5),
        ]

        cell_values = {}
        for field, col in col_map:
            val = section.get(field, '')
            if field == 'status' and val:
                val = f'{checkbox} {val}'
            if val:
                cell_values[col] = val

        for col_idx, val in cell_values.items():
            if col_idx < len(row.cells):
                cell = row.cells[col_idx]
                cell.text = ''
                p = cell.paragraphs[0]
                run = p.add_run(str(val))
                run.font.size = Pt(8)
                if row_color and (col_idx == 2 or col_idx == 3):
                    run.font.color.rgb = row_color


GENERATORS = {
    'Audit_Plan_Stage_1': generate_audit_plan_stage_1,
    'Audit_Plan_Stage_2': generate_audit_plan_stage_2,
    'Participation_List': generate_participation_list,
    'Audit_Report': generate_audit_report,
    'ISO_Checklist': generate_iso_checklist,
    'Certificate_Text': generate_certificate_text,
}


def generate_document_file(doc_type, data, output_dir, template_path=None):
    os.makedirs(output_dir, exist_ok=True)
    safe_name = data.get('client_name', 'Client').replace(' ', '_')

    effective_template = template_path if (template_path and os.path.exists(template_path)) else None

    filename = f'{doc_type}_{safe_name}.docx'
    output_path = os.path.join(output_dir, filename)
    generator = GENERATORS.get(doc_type)
    if generator:
        if doc_type == 'ISO_Checklist':
            result = generator(data, output_path, effective_template)
        else:
            result = generator(data, output_path)
        if result and os.path.exists(result):
            return result
        return None
    return None
