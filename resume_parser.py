
import fitz  # PyMuPDF


def extract_resume_text(pdf_file):
    """Extract text from an uploaded PDF resume."""
    text_parts = []

    with fitz.open(
        stream=pdf_file.read(),
        filetype="pdf"
    ) as document:
        for page in document:
            text_parts.append(page.get_text())

    return "\n".join(text_parts).strip()
