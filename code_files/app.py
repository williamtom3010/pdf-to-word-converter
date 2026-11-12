import os
import re
import tempfile
from html import escape
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from pdf2docx import Converter

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PDF to Word Converter",
    page_icon="📄",
    layout="centered",
)


# ---------------------------------------------------------------------------
# Asset loading (CSS + HTML live in their own files)
# ---------------------------------------------------------------------------
@st.cache_resource
def load_css(filename: str = "styles.css") -> str:
    return (BASE_DIR / filename).read_text(encoding="utf-8")


@st.cache_resource
def load_sections(filename: str = "template.html") -> dict:
    """Parse template.html into a {section_name: html} dictionary."""
    text = (BASE_DIR / filename).read_text(encoding="utf-8")
    pattern = re.compile(
        r"<!--\s*@section\s+(\w+)\s*-->(.*?)<!--\s*@end\s*-->", re.DOTALL
    )
    return {name: body.strip() for name, body in pattern.findall(text)}


def render(section: str, **values: str) -> None:
    """Render an HTML section, filling {{placeholders}} with escaped values."""
    html = load_sections()[section]
    for key, value in values.items():
        html = html.replace("{{" + key + "}}", escape(str(value)))
    st.markdown(html, unsafe_allow_html=True)


st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def convert_pdf_to_docx(pdf_bytes: bytes) -> bytes:
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


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
render("hero")

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload your PDF file",
    type=["pdf"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)

if uploaded_file is not None:
    render(
        "file_card",
        file_name=uploaded_file.name,
        file_size=format_size(uploaded_file.size),
    )

    # Reset previous result if a different file is uploaded
    file_key = f"{uploaded_file.name}-{uploaded_file.size}"
    if st.session_state.get("file_key") != file_key:
        st.session_state["file_key"] = file_key
        st.session_state.pop("docx_data", None)

    if st.button("Convert to Word", type="primary"):
        progress = st.progress(0, text="Preparing your file...")
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(convert_pdf_to_docx, uploaded_file.getvalue())

                # Move the bar forward while the conversion runs in the background
                pct = 5.0
                while not future.done():
                    pct = min(pct + (90 - pct) * 0.08, 90)
                    progress.progress(int(pct), text="Converting your PDF...")
                    time.sleep(0.2)

                st.session_state["docx_data"] = future.result()

            progress.progress(100, text="Done")
            time.sleep(0.4)
        except Exception as e:
            st.session_state.pop("docx_data", None)
            st.error(
                f"Conversion failed: {e}. Check that the PDF isn't password-protected "
                "or corrupted, then try again."
            )
        finally:
            progress.empty()

    if "docx_data" in st.session_state:
        output_filename = os.path.splitext(uploaded_file.name)[0] + ".docx"

        render("done_card")

        st.download_button(
            label="Download Word document",
            data=st.session_state["docx_data"],
            file_name=output_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

# ---------------------------------------------------------------------------
# Feature row + footer
# ---------------------------------------------------------------------------
render("features")