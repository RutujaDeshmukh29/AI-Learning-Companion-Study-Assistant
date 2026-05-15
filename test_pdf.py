from utils.pdf_loader import extract_text_from_pdf

pdf_path = "data/uploaded_pdfs/python_notes.pdf"

text = extract_text_from_pdf(pdf_path)

print("\nExtracted Text:\n")
print(text[:3000])  # Print first 3000 characters