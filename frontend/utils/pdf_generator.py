import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_bytes(markdown_text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1e88e5'),
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#42a5f5'),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#212121'),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    def clean_markdown_for_pdf(text: str) -> str:
        # Convert premium styled span badges into reportlab-friendly font tags
        text = re.sub(r'<span class="badge-verified"[^>]*><a href="([^"]*)"[^>]*>✓ source</a></span>', r' [<font color="#2e7d32">✓</font> source](\1)', text)
        text = re.sub(r'<span class="badge-weak"[^>]*><a href="([^"]*)"[^>]*>~ source</a></span>', r' [<font color="#f57f17">~</font> source](\1)', text)
        text = re.sub(r'<span class="badge-unverified"[^>]*>.*?</span>', r' [<font color="#c62828">?</font> unverified]', text)
        text = re.sub(r'<span class="badge-conflicted"[^>]*>.*?</span>', r' [<font color="#ef6c00">⚡</font> conflicted]', text)

        # Clean up markdown bold and italics tags
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        cleaned = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', cleaned)
        # Escape raw ampersands not followed by an entity name (e.g. &bull;, &amp;)
        cleaned = re.sub(r'&(?!(?:amp|lt|gt|quot|apos|bull);)', '&amp;', cleaned)
        return cleaned

    story = []
    in_code_block = False
    
    # Strip markdown specific syntax
    lines = markdown_text.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 4))
            continue
            
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            story.append(Paragraph(f"<code>{stripped}</code>", body_style))
            continue
            
        if stripped.startswith('# '):
            story.append(Paragraph(clean_markdown_for_pdf(stripped[2:]), title_style))
        elif stripped.startswith('## '):
            story.append(Paragraph(clean_markdown_for_pdf(stripped[3:]), h1_style))
        elif stripped.startswith('### '):
            story.append(Paragraph(clean_markdown_for_pdf(stripped[4:]), h2_style))
        elif stripped.startswith('* ') or stripped.startswith('- '):
            story.append(Paragraph(f"&bull; {clean_markdown_for_pdf(stripped[2:])}", bullet_style))
        else:
            story.append(Paragraph(clean_markdown_for_pdf(stripped), body_style))
            
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
