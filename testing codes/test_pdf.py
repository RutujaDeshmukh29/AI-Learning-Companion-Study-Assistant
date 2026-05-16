"""Test PDF extraction — run: python -m pytest tests/ -v"""
from utils.pdf_loader import extract_text_from_pdf
import os

PDF_PATH = "data/uploaded_pdfs/python_notes.pdf"

def test_extract_text():
    if not os.path.exists(PDF_PATH):
        print(f"\nSkipped: {PDF_PATH} not found. Add a test PDF to run this test.")
        return
    text = extract_text_from_pdf(PDF_PATH)
    assert isinstance(text, str)
    assert len(text) > 100, "Expected meaningful text from PDF"
    print(f"\nExtracted {len(text)} characters")
    print(text[:500])
