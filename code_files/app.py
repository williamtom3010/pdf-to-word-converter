import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from html import escape
from pathlib import Path

import streamlit as st

import pdf_main

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="File Converter",
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
# Conversion modes: everything that differs between conversions lives here
# ---------------------------------------------------------------------------
def _docx_to_pdf(data: bytes) -> bytes:
    """docx2pdf drives MS Word through COM on Windows, and COM must be
    initialised in any non-main thread. Harmless on other platforms."""
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        pass
    return pdf_main.convert_docx_to_pdf(data)


MODES = {
    "PDF → Word": {
        "upload_label": "Upload your PDF file",
        "types": ["pdf"],
        "func": pdf_main.convert_pdf_to_docx,
        "out_suffix": ".docx",
        "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "button": "Convert to Word",
        "download": "Download Word document",
        "working": "Converting your PDF...",
        "hint": "Check that the PDF isn't password-protected or corrupted.",
    },
    "Word → PDF": {
        "upload_label": "Upload your Word file",
        "types": ["docx"],
        "func": _docx_to_pdf,
        "out_suffix": ".pdf",
        "mime": "application/pdf",
        "button": "Convert to PDF",
        "download": "Download PDF",
        "working": "Converting your document...",
        "hint": "This conversion needs Microsoft Word installed on the server.",
    },
    "Image → PDF": {
        "upload_label": "Upload your image",
        "types": ["png", "jpg", "jpeg"],
        "func": pdf_main.convert_img_to_pdf,
        "out_suffix": ".pdf",
        "mime": "application/pdf",
        "button": "Convert to PDF",
        "download": "Download PDF",
        "working": "Converting your image...",
        "hint": "Transparent PNGs can fail. Try a JPG or a PNG without transparency.",
    },
    "PDF → Images": {
        "upload_label": "Upload your PDF file",
        "types": ["pdf"],
        "func": pdf_main.convert_pdf_to_img,
        "out_suffix": "_pages.zip",
        "mime": "application/zip",
        "button": "Convert to Images",
        "download": "Download images (ZIP)",
        "working": "Rendering your pages...",
        "hint": "Check that Poppler is installed and on PATH (or set POPPLER_PATH).",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def format_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024


def run_with_progress(func, data: bytes, text: str) -> bytes:
    """Run func(data) in a background thread while animating a progress bar."""
    progress = st.progress(0, text="Preparing your file...")
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(func, data)

            pct = 5.0
            while not future.done():
                pct = min(pct + (90 - pct) * 0.08, 90)
                progress.progress(int(pct), text=text)
                time.sleep(0.2)

            result = future.result()  # re-raises any error from the thread

        progress.progress(100, text="Done")
        time.sleep(0.4)
        return result
    finally:
        progress.empty()


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
render("hero")

# ---------------------------------------------------------------------------
# Mode selector
# ---------------------------------------------------------------------------
mode_name = st.radio(
    "Conversion type",
    list(MODES.keys()),
    horizontal=True,
    label_visibility="collapsed",
)
mode = MODES[mode_name]

# ---------------------------------------------------------------------------
# Upload (separate uploader per mode, so switching modes clears the file)
# ---------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    mode["upload_label"],
    type=mode["types"],
    accept_multiple_files=False,
    label_visibility="collapsed",
    key=f"uploader_{mode_name}",
)

if uploaded_file is not None:
    render(
        "file_card",
        file_name=uploaded_file.name,
        file_size=format_size(uploaded_file.size),
    )

    # Reset any previous result if the file or the mode changed
    file_key = f"{mode_name}-{uploaded_file.name}-{uploaded_file.size}"
    if st.session_state.get("file_key") != file_key:
        st.session_state["file_key"] = file_key
        st.session_state.pop("result_data", None)

    if st.button(mode["button"], type="primary"):
        try:
            st.session_state["result_data"] = run_with_progress(
                mode["func"], uploaded_file.getvalue(), mode["working"]
            )
        except Exception as e:
            st.session_state.pop("result_data", None)
            st.error(f"Conversion failed: {e}. {mode['hint']}")

    if "result_data" in st.session_state:
        base_name = os.path.splitext(uploaded_file.name)[0]
        output_filename = base_name + mode["out_suffix"]

        render("done_card")

        st.download_button(
            label=mode["download"],
            data=st.session_state["result_data"],
            file_name=output_filename,
            mime=mode["mime"],
        )

# ---------------------------------------------------------------------------
# Feature row + footer
# ---------------------------------------------------------------------------
render("features")