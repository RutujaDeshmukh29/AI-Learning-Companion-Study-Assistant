from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings
from utils.vector_store import (
    store_embeddings,
    search_similar_chunks
)

# PDF path
pdf_path = "data/uploaded_pdfs/python_notes.pdf"

# Extract text
text = extract_text_from_pdf(pdf_path)

# Split text
chunks = split_text(text)

# Generate embeddings
embeddings = generate_embeddings(chunks)

# Store embeddings
store_embeddings(chunks, embeddings)

# User query
query = "What is Python?"

# Generate query embedding
query_embedding = generate_embeddings([query])[0]

# Search similar chunks
results = search_similar_chunks(query_embedding)

print("\nRetrieved Chunks:\n")

for doc in results["documents"][0]:
    print(doc)
    print("\n-------------------\n")