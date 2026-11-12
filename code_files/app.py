import streamlit as st
from pdf2docx import Converter
from io import BytesIO
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="PDF to Word Converter",
    page_icon="📄",
    layout="centered"
)

# Application title
st.title("📄 PDF to Word Converter")
st.write("Upload your PDF file and convert it into an editable Word document.")

st.divider()

# PDF uploader
uploaded_file = st.file_uploader(
    "Upload your PDF file",
    type=["pdf"],
    accept_multiple_files=False
)

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    # Convert button
    if st.button("Convert to Word", type="primary", use_container_width=True):

        temp_pdf_path = None
        temp_docx_path = None

        try:
            with st.spinner("Converting PDF to Word... Please wait."):

                # Create temporary files
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_pdf:

                    temp_pdf.write(uploaded_file.getvalue())
                    temp_pdf_path = temp_pdf.name

                temp_docx_path = tempfile.mktemp(suffix=".docx")

                # Convert PDF to DOCX
                cv = Converter(temp_pdf_path)

                try:
                    cv.convert(temp_docx_path)
                finally:
                    cv.close()

                # Read converted DOCX into memory
                with open(temp_docx_path, "rb") as file:
                    docx_data = BytesIO(file.read())

            st.success("PDF successfully converted to Word!")

            # Generate output filename
            output_filename = (
                os.path.splitext(uploaded_file.name)[0] + ".docx"
            )

            # Download button
            st.download_button(
                label="⬇️ Download Word Document",
                data=docx_data.getvalue(),
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Conversion failed: {str(e)}")

        finally:
            # Clean up temporary files
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

            if temp_docx_path and os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)