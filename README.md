# 📄 PDF to Word Converter

A clean web app that converts PDF files into editable Word (`.docx`) documents. Built with [Streamlit](https://streamlit.io/) and [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx).

Upload a PDF, click **Convert to Word**, and download the result. Text, tables and images are kept in place.

## Features

- Drag-and-drop PDF upload with a file name and size preview
- One-click conversion to `.docx`
- Progress bar while the file converts
- Download button that stays on screen after conversion
- Custom, responsive interface for desktop and mobile
- Files are processed in memory and temporary files are deleted after conversion

## Project structure

```
pdf-to-word-converter/
├── PDF-to-Word.bat          # One-click launcher for Windows
├── code_files/
│   ├── app.py               # Streamlit app: upload, conversion and download logic
│   ├── template.html        # HTML sections (hero, file card, success panel, features)
│   ├── styles.css           # All styling and colour variables
│   └── requirements.txt     # Python dependencies
└── README.md
```

- `app.py` loads `template.html` and `styles.css` and fills in values such as the file name and size.
- `template.html` is split into named sections (`hero`, `file_card`, `done_card`, `features`).
- `styles.css` holds the theme. Colours are CSS variables at the top of the file.

## Getting started

### Prerequisites

- Python 3.9 or later
- pip

### Option 1: Windows one-click launcher

1. Download or clone the repository.
2. Double-click **`PDF-to-Word.bat`**.

The script will:

1. Check that Python is installed.
2. Create a virtual environment in `code_files/venv` if it doesn't exist.
3. Install the dependencies from `requirements.txt` if they are missing.
4. Start the Streamlit server on port 8501 and open `http://localhost:8501` in your browser.

To stop the app, close the "PDF to Word Server" command window.

### Option 2: Run manually (Windows, macOS, Linux)

```bash
# 1. Clone the repository
git clone https://github.com/williamtom3010/pdf-to-word-converter.git
cd pdf-to-word-converter/code_files

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Streamlit opens the app in your browser, usually at `http://localhost:8501`.

## How to use

1. Upload a PDF file using the upload box.
2. Click **Convert to Word**.
3. When the progress bar finishes, click **Download Word document**.

## Customization

All paths below are inside `code_files/`.

- **Colours:** edit the variables in the `:root` block at the top of `styles.css` (`--ink`, `--accent`, `--paper` and so on).
- **Page background:** change the `.stApp` block in `styles.css`.
- **Text and layout:** edit the sections in `template.html`.
- **Streamlit toolbar:** the menu and rerun options are hidden by the "Hide default Streamlit chrome" rule in `styles.css`. Remove `header` from that rule to show them again.
- **Light or dark theme:** create `.streamlit/config.toml` and set:

  ```toml
  [theme]
  base = "light"
  ```

## Limitations

- Scanned PDFs (pages that are images of text) won't convert to editable text, because the converter has no OCR.
- Password-protected or corrupted PDFs will fail to convert.
- Complex layouts may not match the original exactly, so check the result in Word.
- The progress bar is an estimate, not exact per-page progress.

## Built with

- [Streamlit](https://streamlit.io/) for the web interface
- [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) for the PDF to DOCX conversion

## Contributing

Contributions are welcome. Fork the repository, create a branch for your change, and open a pull request.

## License

Add a license of your choice (for example MIT) and describe it here.
