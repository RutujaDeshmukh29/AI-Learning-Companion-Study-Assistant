import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF file.
    """

    text = ""

    pdf_document = fitz.open(pdf_path)

    for page in pdf_document:
        text += page.get_text()

    pdf_document.close()

    return text