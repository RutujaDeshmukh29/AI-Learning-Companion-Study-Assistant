from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings
from utils.vector_store import store_embeddings, search_similar_chunks
from utils.llm import ask_llm
from utils.prompts import build_rag_prompt

def run_rag_pipeline(pdf_path, question):
    """
    Runs the RAG pipeline for a given PDF and question.
    """
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Split the text into chunks
    chunks = split_text(text)

    # Generate embeddings for the chunks
    embeddings = generate_embeddings(chunks)

    # Store the embeddings in the vector store
    store_embeddings(chunks, embeddings)

    # Generate an embedding for the user's question
    query_embedding = generate_embeddings([question])[0]

    # Search for similar chunks in the vector store
    results = search_similar_chunks(query_embedding)
    retrieved_chunks = results["documents"][0]

    # Build the RAG prompt
    prompt = build_rag_prompt("\n\n".join(retrieved_chunks), question)

    # Get the answer from the LLM
    answer = ask_llm(prompt)

    return answer, retrieved_chunks
