import os
import re
from docx import Document


def parse_docx(filepath):
    doc = Document(filepath)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    tables = []
    for table in doc.tables:
        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append(cells)
        tables.append(rows)
    return {
        'filename': os.path.basename(filepath),
        'paragraphs': paragraphs,
        'text': '\n'.join(paragraphs),
        'tables': tables,
    }


def parse_txt(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return {
        'filename': os.path.basename(filepath),
        'paragraphs': lines,
        'text': text,
        'tables': [],
    }


def extract_audit_notes(filepath):
    if filepath.endswith('.txt'):
        return parse_txt(filepath)
    return parse_docx(filepath)


def extract_manday_data(filepath):
    data = parse_docx(filepath)
    full_text = data['text']

    fields = {}

    client_match = re.search(r'(?:Client|Customer|Company|Organization)\s*[:;]\s*(.+?)(?:\n|$)', full_text, re.IGNORECASE)
    if client_match:
        fields['client_name'] = client_match.group(1).strip()

    address_match = re.search(r'(?:Address|Location|Site)\s*[:;]\s*(.+?)(?:\n|$)', full_text, re.IGNORECASE)
    if address_match:
        fields['client_address'] = address_match.group(1).strip()

    date_match = re.search(r'(?:Audit\s*Date|Date[s]?)\s*[:;]\s*(.+?)(?:\n|$)', full_text, re.IGNORECASE)
    if date_match:
        fields['audit_date'] = date_match.group(1).strip()

    manday_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:Manday|Man[- ]?Day|MD|Audit\s*Day)', full_text, re.IGNORECASE)
    if manday_match:
        fields['mandays'] = manday_match.group(1)

    standard_match = re.search(r'(?:ISO|Standard)\s*[:;]\s*(.+?)(?:\n|$)', full_text, re.IGNORECASE)
    if standard_match:
        fields['standard'] = standard_match.group(1).strip()

    experts = []
    expert_pattern = re.compile(r'(?:Auditor|Expert|Assessor|Team\s*Member)\s*[:;]\s*(.+?)(?:\n|$)', re.IGNORECASE)
    for m in expert_pattern.finditer(full_text):
        experts.append(m.group(1).strip())
    if experts:
        fields['experts'] = experts

    for table in data['tables']:
        for row in table:
            row_lower = [c.lower() for c in row]
            if any('manday' in c or 'man-day' in c or 'man day' in c or 'audit days' in c for c in row_lower):
                fields['manday_table_row'] = ' | '.join(row)

    data['extracted'] = fields
    return data
