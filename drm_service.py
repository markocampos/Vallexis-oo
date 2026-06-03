from pypdf import PdfReader, PdfWriter, Transformation, PageObject
import math
from io import BytesIO
import os

def create_watermark(text: str) -> BytesIO:
    """
    Creates a transparent PDF with the given text as a diagonal watermark.
    Using PyPDF's pure-python transformation matrices and reportlab for simple text generation
    without PIL, to satisfy pure python requirement as much as possible.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import Color

    # We use reportlab here just to generate the base text PDF purely in python,
    # avoiding heavy PIL C-extensions for drawing.
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    # Set fill color to a translucent gray
    c.setFillColor(Color(0.6, 0.6, 0.6, alpha=0.5))
    c.setFont("Helvetica", 40)

    # Draw text in center-ish
    c.drawString(100, 400, text)
    c.save()
    packet.seek(0)
    return packet

def apply_watermark(source_pdf_path: str, buyer_info: str, output_path: str) -> str:
    """
    Applies a dynamic watermark to the source PDF using an underlay (over=False)
    and transformation matrices as requested.
    """
    if not os.path.exists(source_pdf_path):
        raise FileNotFoundError(f"Source PDF not found at {source_pdf_path}")

    watermark_io = create_watermark(buyer_info)
    watermark_reader = PdfReader(watermark_io)
    watermark_page = watermark_reader.pages[0]

    # Apply transformation to the watermark: scale and rotate 45 degrees
    angle_rad = math.radians(45)
    # create a transformation matrix
    # [cos(a) sin(a) -sin(a) cos(a) tx ty]
    op = Transformation().scale(sx=1.5, sy=1.5).rotate(45).translate(tx=100, ty=-100)
    watermark_page.add_transformation(op)

    source_reader = PdfReader(source_pdf_path)
    writer = PdfWriter()

    for page in source_reader.pages:
        # Merge watermark under the page (over=False) to ensure it acts as a background
        page.merge_page(watermark_page, over=False)
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path
