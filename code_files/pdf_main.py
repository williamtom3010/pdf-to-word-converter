import os
import tempfile
from dotenv import load_dotenv
import functools
import logging
import time

logger = logging.getLogger("pdf_main")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def logged(func):
    """Log start, output size, duration and errors for a conversion."""
    @functools.wraps(func)
    def wrapper(data: bytes, *args, **kwargs):
        logger.info("%s: started (input %.1f KB)", func.__name__, len(data) / 1024)
        start = time.perf_counter()
        try:
            result = func(data, *args, **kwargs)
        except Exception:
            logger.exception("%s: FAILED", func.__name__)
            raise
        logger.info(
            "%s: finished in %.2fs (output %.1f KB)",
            func.__name__, time.perf_counter() - start, len(result) / 1024,
        )
        return result
    return wrapper

load_dotenv()


@logged
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

@logged
def convert_docx_to_pdf(doc_bytes: bytes) -> bytes:

    from docx2pdf import convert

    pdf_path = None
    docx_path = None

    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
            tmp_docx.write(doc_bytes)
            docx_path = tmp_docx.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:            
            pdf_path = tmp_pdf.name
        

        convert(docx_path, pdf_path)
        with open(pdf_path, "rb") as f:
            return f.read()
        
    finally:
        for path in (docx_path, pdf_path):
            if path and os.path.exists(path):
                os.remove(path)

@logged
def convert_img_to_pdf(img_bytes: bytes) -> bytes:
    import img2pdf

    # convert raw image bytes to PDF bytes  
    pdf_bytes = img2pdf.convert(img_bytes)

    # output
    print("Successfully made pdf file")

    return pdf_bytes

@logged
def convert_pdf_to_img(pdf_bytes: bytes) -> bytes:

    from pdf2image import convert_from_bytes
    import io
    import zipfile


    # Poppler: Required to read and render PDF files.
    # Windows: click here to download. Add the bin/ folder to PATH or provide the path in your code:
    # poppler_path = r"C:\path\to\poppler-xx\bin"
    poppler_path = os.getenv("poppler_path")

    images = convert_from_bytes(pdf_bytes, poppler_path=poppler_path,)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for page_num, image in enumerate(images, start=1):
            buf = io.BytesIO()
            image.convert("RGB").save(buf, "JPEG")
            zf.writestr(f"page_{page_num}.jpg", buf.getvalue())

    return zip_buffer.getvalue()

    