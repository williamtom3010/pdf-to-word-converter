# 📄 File Converter

A clean web app that converts between PDF, Word and image files. Built with [Streamlit](https://streamlit.io/).

Pick a conversion type, upload your file, click convert, and download the result. Everything is processed in memory, so nothing is kept on the server.

## Supported conversions

| Conversion   | Input                   | Output                     | Powered by                                               |
| ------------ | ----------------------- | -------------------------- | -------------------------------------------------------- |
| PDF → Word   | `.pdf`                  | `.docx`                    | [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx)  |
| Word → PDF   | `.docx`                 | `.pdf`                     | [docx2pdf](https://github.com/AlJohri/docx2pdf)          |
| Image → PDF  | `.png`, `.jpg`, `.jpeg` | `.pdf`                     | [img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf) |
| PDF → Images | `.pdf`                  | `.zip` (one JPEG per page) | [pdf2image](https://github.com/Belval/pdf2image)         |

## Features

- Four conversions in one app, chosen with a simple selector
- Drag-and-drop upload with a file name and size preview
- Progress bar while the file converts
- Download button that stays on screen after conversion
- Console logging for every conversion (start, duration, output size and errors)
- Custom, responsive interface for desktop and mobile
- Files are processed in memory, and temporary files are deleted after conversion

## Project structure

```
pdf-to-word-converter/
├── PDF-to-Word.bat          # One-click launcher for Windows
├── code_files/
│   ├── app.py               # Streamlit app: mode selector, upload and download logic
│   ├── pdf_main.py          # Conversion functions (bytes in, bytes out) and logging
│   ├── template.html        # HTML sections (hero, file card, success panel, features)
│   ├── styles.css           # All styling and colour variables
│   └── requirements.txt     # Python dependencies
└── README.md
```

- `app.py` holds a `MODES` table that describes each conversion (accepted file types, function, output name, MIME type, button text). Adding a new conversion means adding one entry there.
- `pdf_main.py` contains one function per conversion. Each takes bytes and returns bytes, and is wrapped by a `@logged` decorator.
- `template.html` is split into named sections (`hero`, `file_card`, `done_card`, `features`).
- `styles.css` holds the theme. Colours are CSS variables at the top of the file.

## Getting started

### Prerequisites

- Python 3.9 or later
- pip
- **Poppler**, for PDF → Images (see below)
- **Microsoft Word**, for Word → PDF (see below)

The first two conversions (PDF → Word and Image → PDF) need nothing beyond the Python packages.

#### Poppler (PDF → Images)

`pdf2image` relies on Poppler to render PDF pages.

- **Windows:** download a Poppler build, unzip it, and either add its `bin` folder to your `PATH`, or set the `POPPLER_PATH` environment variable to that folder.
- **macOS:** `brew install poppler`
- **Linux:** `sudo apt install poppler-utils`

#### Microsoft Word (Word → PDF)

`docx2pdf` drives Microsoft Word, so this conversion only works on Windows or macOS with Word installed. It will not work on Linux or on most hosting platforms (for example Streamlit Cloud or Docker).

### Option 1: Windows one-click launcher

1. Download or clone the repository.
2. Double-click **`PDF-to-Word.bat`**.

The script will:

1. Check that Python is installed.
2. Create a virtual environment in `code_files/venv` if it doesn't exist.
3. Install the dependencies from `requirements.txt` if they are missing.
4. Start the Streamlit server on port 8501 and open `http://localhost:8501` in your browser.

To stop the app, close the server command window.

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

## Dependencies

`requirements.txt` should include:

```
streamlit
pdf2docx
docx2pdf
img2pdf
pdf2image
Pillow
```

## How to use

1. Choose a conversion type at the top (PDF → Word, Word → PDF, Image → PDF or PDF → Images).
2. Upload a file using the upload box.
3. Click the convert button.
4. When the progress bar finishes, click the download button.

PDF → Images downloads a single ZIP file named `<original name>_pages.zip`, containing `page_1.jpg`, `page_2.jpg` and so on.

## Logging

Each conversion prints a short log to the terminal where Streamlit is running:

```
[INFO] convert_img_to_pdf: started (input 245.3 KB)
[INFO] convert_img_to_pdf: finished in 0.04s (output 246.1 KB)
```

If a conversion fails, the full traceback is printed with a `FAILED` line. `pdf2docx` also prints its own detailed page-by-page logs.

## Customization

All paths below are inside `code_files/`.

- **Colours:** edit the variables in the `:root` block at the top of `styles.css` (`--ink`, `--accent`, `--paper` and so on).
- **Page background:** change the `.stApp` block in `styles.css`.
- **Text and layout:** edit the sections in `template.html`.
- **Add a conversion:** write a bytes-in, bytes-out function in `pdf_main.py`, add `@logged` above it, then add an entry to `MODES` in `app.py`.
- **Poppler location:** set the `POPPLER_PATH` environment variable if Poppler is not on your `PATH`.
- **Upload size limit:** Streamlit allows 200 MB by default. Change it with `server.maxUploadSize` in `.streamlit/config.toml`.
- **Streamlit toolbar:** the menu and rerun options are hidden by the "Hide default Streamlit chrome" rule in `styles.css`. Remove `header` from that rule to show them again.
- **Light or dark theme:** create `.streamlit/config.toml` and set:

  ```toml
  [theme]
  base = "light"
  ```

## Limitations

- **PDF → Word:** scanned PDFs (pages that are images of text) won't convert to editable text, because there is no OCR. Password-protected or corrupted PDFs will fail. Complex layouts may not match the original exactly, so check the result in Word.
- **Word → PDF:** requires Microsoft Word installed on the machine running the app. Only `.docx` files are supported.
- **Image → PDF:** PNGs with transparency can fail. Use a JPG or a PNG without transparency.
- **PDF → Images:** requires Poppler. Output is JPEG, one image per page.
- The progress bar is an estimate, not exact per-page progress.

## Built with

- [Streamlit](https://streamlit.io/) for the web interface
- [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) for PDF to DOCX
- [docx2pdf](https://github.com/AlJohri/docx2pdf) for DOCX to PDF
- [img2pdf](https://gitlab.mister-muffin.de/josch/img2pdf) for images to PDF
- [pdf2image](https://github.com/Belval/pdf2image) and [Poppler](https://poppler.freedesktop.org/) for PDF to images

## Contributing

Contributions are welcome. Fork the repository, create a branch for your change, and open a pull request.
