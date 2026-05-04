from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_MD = os.path.join(BASE_DIR, 'project-report-en.md')
OUTPUT_PDF = os.path.join(BASE_DIR, 'project-report-output.pdf')

with open(INPUT_MD, 'r', encoding='utf-8') as f:
    md_content = f.read()

doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='CustomTitle',
    parent=styles['Title'],
    fontSize=24,
    textColor=colors.HexColor('#1a1a2e'),
    spaceAfter=20,
    alignment=TA_CENTER
))
styles.add(ParagraphStyle(
    name='CustomH1',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#0f3460'),
    spaceBefore=20,
    spaceAfter=12
))
styles.add(ParagraphStyle(
    name='CustomH2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#533483'),
    spaceBefore=15,
    spaceAfter=8
))
styles.add(ParagraphStyle(
    name='CustomH3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#1a1a2e'),
    spaceBefore=12,
    spaceAfter=6
))
styles.add(ParagraphStyle(
    name='CustomBody',
    parent=styles['Normal'],
    fontSize=11,
    leading=16,
    spaceAfter=8
))
styles.add(ParagraphStyle(
    name='CustomList',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    leftIndent=20,
    spaceAfter=4
))

def parse_markdown(text):
    story = []
    lines = text.split('\n')
    in_table = False
    table_data = []

    for line in lines:
        line = line.strip()

        if line.startswith('|') and line.endswith('|'):
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            if set(row) == {'---'}:
                continue
            table_data.append(row)
            in_table = True
            continue
        elif in_table:
            story.append(create_table(table_data))
            table_data = []
            in_table = False

        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['CustomTitle']))
            story.append(Spacer(1, 0.3*cm))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['CustomH1']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['CustomH2']))
        elif line.startswith('#### '):
            story.append(Paragraph(line[5:], styles['CustomH3']))
        elif line.startswith('- ') or line.startswith('* '):
            story.append(Paragraph(f"• {line[2:]}", styles['CustomList']))
        elif line.startswith('```'):
            continue
        elif line.startswith('>'):
            story.append(Paragraph(line[1:].strip(), styles['CustomBody']))
        elif line and not in_table:
            clean_line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            clean_line = re.sub(r'\*(.+?)\*', r'<i>\1</i>', clean_line)
            clean_line = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', clean_line)
            story.append(Paragraph(clean_line, styles['CustomBody']))

    if in_table and table_data:
        story.append(create_table(table_data))

    return story

def create_table(data):
    if not data:
        return Spacer(1, 0.5*cm)

    col_count = max(len(row) for row in data)
    formatted_data = []
    for i, row in enumerate(data):
        formatted_row = []
        for j in range(col_count):
            cell = row[j] if j < len(row) else ''
            if i == 0:
                formatted_row.append(f'<b>{cell}</b>')
            else:
                formatted_row.append(cell)
        formatted_data.append(formatted_row)

    table = Table(formatted_data, colWidths=[5*cm] * col_count)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
    ]))
    return table

story = parse_markdown(md_content)
doc.build(story)
print(f'PDF generated successfully: {OUTPUT_PDF}')