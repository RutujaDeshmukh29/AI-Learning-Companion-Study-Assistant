from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings
from utils.vector_store import (
    store_embeddings,
    search_similar_chunks
)
from utils.gemini_api import ask_gemini
from utils.prompts import build_rag_prompt

# PDF path
pdf_path = "data/uploaded_pdfs/python_notes.pdf"

# Extract text
text = extract_text_from_pdf(pdf_path)

# Split into chunks
chunks = split_text(text)

# Generate embeddings
embeddings = generate_embeddings(chunks)

# Store embeddings
store_embeddings(chunks, embeddings)

# User question
question = "what is the primary purpose of marketing techniques.?"

# Generate query embedding
query_embedding = generate_embeddings([question])[0]

# Retrieve relevant chunks
results = search_similar_chunks(query_embedding)

retrieved_chunks = results["documents"][0]

# Combine retrieved chunks
context = "\n\n".join(retrieved_chunks)

# Build RAG prompt
prompt = build_rag_prompt(context, question)

# Generate AI response
response = ask_gemini(prompt)

print("\nAI Response:\n")
print(response)