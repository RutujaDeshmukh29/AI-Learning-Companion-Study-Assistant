from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text

pdf_path = "data/uploaded_pdfs/python_notes.pdf"

text = extract_text_from_pdf(pdf_path)

chunks = split_text(text)

print(f"\nTotal Chunks: {len(chunks)}\n")

print("First Chunk:\n")
print(chunks[0])

print("\nSecond Chunk:\n")
print(chunks[1])