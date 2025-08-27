import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import cnpdb, cnpconf

def export_clients_to_pdf(
        clients, 
        visible_columns,
        pdf_path,
        pdf_direction,
        title):
        
    try:
        if not os.path.exists(cnpconf.pdf_kfont_file):
            #raise FileNotFoundError(f"Font file '{pdf_kfont_path}' not found.")
            print(f"Font file '{pdf_kfont_file}' not found.")
            return
        pdfmetrics.registerFont(TTFont('KoreanFont', cnpconf.pdf_kfont_file))
    except Exception as e:
        print(f"Error registering font: {e}")
        # Fallback or error handling if the font file is missing
        return
    
    if pdf_direction == cnpconf.export_pdf_landscape:
        pagesize = landscape(letter)
    else:
        pagesize = portrait(letter)

    """
    clients: list of dicts (or sqlite3.Row) with keys below.
          Any missing/None fields are rendered as empty strings.
    pdf_path: output file path, e.g. 'clients.pdf'
    """

    # ---- Normalize rows (dict) and string-ify, handling None ----
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    record_list = [[Paragraph(f'<font name="Helvetica-Bold">{v}</font>', style) for v in visible_columns]]
    
    for r_ in clients:
        # sqlite3.Row → dict; dict stays as-is
        record = []
        for c_ in visible_columns:
            key = cnpdb.available_view_column_key(c_)
            val = r_.get(key, "")
            if val is None:
                val = ""
            if cnpdb.kr_name(key):
                record.append(Paragraph(f'<font name="KoreanFont">{val}</font>', style)) 
            else:
                record.append(Paragraph(f'<font name="Helvetica-Bold">{val}</font>', style))
        record_list.append(record)

    # ---- Build PDF ----
    pdf = SimpleDocTemplate(
        pdf_path,
        pagesize=pagesize,
        rightMargin=20, leftMargin=20,
        topMargin=20, bottomMargin=20
    )

    story = []

    # Title
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=style,
        fontName='Helvetica-Bold',
        fontSize=13,
        spaceAfter=12,
        alignment=TA_LEFT,
    )
    story.append(Paragraph(f"<b>{title}</b>", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style))
    story.append(Paragraph("<br/>", style))

    # Table
    col_widths = [None] * len(visible_columns)
    table = Table(record_list, repeatRows=1, hAlign='LEFT', colWidths=col_widths)

    # Styling
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        #('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        #('FONTNAME', (0, 0), (-1, 0), 'Batang'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ]))

    story.append(table)

    pdf.build(story)
    
    
if __name__ == "__main__":
    d_ = [{"last_name_kor": "홍", 
          "first_name_kor": "길동", 
          "first_name_eng": "car",
          "last_name_eng": "rider"}]
    v_ = ["Last KR", "First EN"]
    export_clients_to_pdf(d_,v_,'ppp.pdf', cnpconf.export_pdf_landscape, "sample")
    