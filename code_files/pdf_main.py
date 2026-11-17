import os
import tempfile


def convert_pdf_to_docx(pdf_bytes: bytes) -> bytes:

    from pdf2docx import Converter

    """Convert PDF bytes to DOCX bytes using temporary files."""
    pdf_path = None
    docx_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(pdf_bytes)
            pdf_path = tmp_pdf.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            docx_path = tmp_docx.name

        cv = Converter(pdf_path)
        try:
            cv.convert(docx_path)
        finally:
            cv.close()

        with open(docx_path, "rb") as f:
            return f.read()
    finally:
        for path in (pdf_path, docx_path):
            if path and os.path.exists(path):
                os.remove(path)

def convert_docx_to_pdf(pdf_bytes: bytes) -> bytes:

    from docx2pdf import convert

    # Converting docx specifying both the input 
    # and output paths
    docx_path = "GeeksForGeeks\GFG_1.docx"
    pdf_path = "Other_Folder\Mine.pdf"
    convert(docx_path, pdf_path)

def convert_img_to_pdf(pdf_bytes: bytes) -> bytes:
    pass

def convert_pdf_to_img(pdf_bytes: bytes) -> bytes:
    pass