import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas

def generate_pdf_certificate(student_name: str, issue_date: datetime, cert_code: str) -> io.BytesIO:
    """
    Generates a landscape PDF certificate of completion.
    Returns a BytesIO stream containing the PDF.
    """
    buffer = io.BytesIO()
    # Letter size landscape is 792 x 612 points
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    
    # Draw double border
    # Outer border (dark slate)
    p.setStrokeColor(colors.HexColor("#1e293b"))
    p.setLineWidth(5)
    p.rect(20, 20, 752, 572)
    
    # Inner border (indigo accent)
    p.setStrokeColor(colors.HexColor("#6366f1"))
    p.setLineWidth(1.5)
    p.rect(28, 28, 736, 556)
    
    # Corner decorations (triangles)
    p.setFillColor(colors.HexColor("#6366f1"))
    # Top-Left Corner
    p.beginPath()
    p.moveTo(28, 550)
    p.lineTo(60, 584)
    p.lineTo(28, 584)
    p.close()
    p.fill()
    
    # Top-Right Corner
    p.beginPath()
    p.moveTo(764, 550)
    p.lineTo(732, 584)
    p.lineTo(764, 584)
    p.close()
    p.fill()
    
    # Bottom-Left Corner
    p.beginPath()
    p.moveTo(28, 62)
    p.lineTo(60, 28)
    p.lineTo(28, 28)
    p.close()
    p.fill()
    
    # Bottom-Right Corner
    p.beginPath()
    p.moveTo(764, 62)
    p.lineTo(732, 28)
    p.lineTo(764, 28)
    p.close()
    p.fill()
    
    # Title
    p.setFont("Helvetica-Bold", 36)
    p.setFillColor(colors.HexColor("#0f172a"))
    p.drawCentredString(396, 460, "CERTIFICATE OF COMPLETION")
    
    # Subtitle
    p.setFont("Helvetica-Oblique", 14)
    p.setFillColor(colors.HexColor("#475569"))
    p.drawCentredString(396, 410, "This certificate is proudly presented to")
    
    # Name
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(colors.HexColor("#6366f1"))
    p.drawCentredString(396, 350, student_name.upper())
    
    # Divider line
    p.setStrokeColor(colors.HexColor("#cbd5e1"))
    p.setLineWidth(1)
    p.line(246, 325, 546, 325)
    
    # Body text
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.HexColor("#475569"))
    p.drawCentredString(396, 290, "for successfully completing the 3-Month curriculum of the")
    
    p.setFont("Helvetica-Bold", 18)
    p.setFillColor(colors.HexColor("#0f172a"))
    p.drawCentredString(396, 255, "Personalized AI Data Science Tutor Course")
    
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.HexColor("#64748b"))
    p.drawCentredString(396, 225, "covering Python Fundamentals, Statistics, Machine Learning, Deep Learning, and Projects")
    
    # Bottom Details (Date, Signature)
    # Date line
    p.setStrokeColor(colors.HexColor("#94a3b8"))
    p.setLineWidth(1)
    p.line(80, 140, 230, 140)
    
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor("#475569"))
    p.drawString(80, 120, f"DATE: {issue_date.strftime('%B %d, %Y')}")
    
    # Signature line
    p.line(562, 140, 712, 140)
    
    p.setFont("Helvetica-Oblique", 13)
    p.setFillColor(colors.HexColor("#6366f1"))
    p.drawCentredString(637, 148, "AI Tutor Engine")
    
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor("#475569"))
    p.drawCentredString(637, 120, "AUTHORIZED EVALUATOR")
    
    # Certificate ID at the very bottom
    p.setFont("Courier", 9)
    p.setFillColor(colors.HexColor("#94a3b8"))
    p.drawCentredString(396, 75, f"Certificate ID: {cert_code}")
    
    # Decorative Seal graphic at the bottom center
    p.setFillColor(colors.HexColor("#e0e7ff"))
    p.circle(396, 135, 28, stroke=0, fill=1)
    p.setFillColor(colors.HexColor("#6366f1"))
    p.circle(396, 135, 22, stroke=0, fill=1)
    p.setFillColor(colors.HexColor("#ffffff"))
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(396, 131, "AI")
    
    # Finish page
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
