from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings

pdf_path = "data/uploaded_pdfs/python_notes.pdf"

# Extract text
text = extract_text_from_pdf(pdf_path)

# Split into chunks
chunks = split_text(text)

# Generate embeddings
embeddings = generate_embeddings(chunks)

print("\nTotal Chunks:")
print(len(chunks))

print("\nEmbedding Shape:")
print(embeddings.shape)

print("\nFirst Embedding Vector:")
print(embeddings[0])