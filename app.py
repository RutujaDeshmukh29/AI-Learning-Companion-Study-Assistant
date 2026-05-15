import streamlit as st
import os

from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings
from utils.vector_store import (
    store_embeddings,
    search_similar_chunks
)
from utils.gemini_api import ask_gemini
from utils.prompts import build_rag_prompt

# -----------------------------
# Streamlit Page Config
# -----------------------------

st.set_page_config(
    page_title="AI Learning Companion",
    page_icon="📘",
    layout="wide"
)

# -----------------------------
# App Title
# -----------------------------

st.title("📘 AI Learning Companion")

st.write(
    "Upload your study PDF and ask questions using AI-powered RAG."
)

# -----------------------------
# PDF Upload
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

# -----------------------------
# Process PDF
# -----------------------------

if uploaded_file is not None:

    # Create upload folder if not exists
    os.makedirs("data/uploaded_pdfs", exist_ok=True)

    # Save uploaded PDF
    pdf_path = os.path.join(
        "data/uploaded_pdfs",
        uploaded_file.name
    )

    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("PDF uploaded successfully!")

    # -----------------------------
    # Extract Text
    # -----------------------------

    with st.spinner("Extracting text from PDF..."):

        text = extract_text_from_pdf(pdf_path)

    st.success("Text extracted successfully!")

    # -----------------------------
    # Chunk Text
    # -----------------------------

    with st.spinner("Splitting text into chunks..."):

        chunks = split_text(text)

    st.write(f"Total Chunks Created: {len(chunks)}")

    # -----------------------------
    # Generate Embeddings
    # -----------------------------

    with st.spinner("Generating embeddings..."):

        embeddings = generate_embeddings(chunks)

    st.success("Embeddings generated!")

    # -----------------------------
    # Store in ChromaDB
    # -----------------------------

    with st.spinner("Storing embeddings in ChromaDB..."):

        store_embeddings(chunks, embeddings)

    st.success("Embeddings stored successfully!")

    st.divider()

    # -----------------------------
    # User Question
    # -----------------------------

    user_question = st.text_input(
        "Ask a question from your PDF:"
    )

    # -----------------------------
    # Generate Answer
    # -----------------------------

    if st.button("Get Answer"):

        if user_question:

            with st.spinner("Searching relevant context..."):

                # Generate query embedding
                query_embedding = generate_embeddings(
                    [user_question]
                )[0]

                # Retrieve similar chunks
                results = search_similar_chunks(
                    query_embedding
                )

                retrieved_chunks = results["documents"][0]

                # Combine retrieved chunks
                context = "\n\n".join(retrieved_chunks)

            with st.spinner("Generating AI response..."):

                # Build RAG prompt
                prompt = build_rag_prompt(
                    context,
                    user_question
                )

                # Generate response
                response = ask_gemini(prompt)

            # -----------------------------
            # Display Response
            # -----------------------------

            st.subheader("AI Response")

            st.write(response)

            # -----------------------------
            # Optional Debug Section
            # -----------------------------

            with st.expander("View Retrieved Context"):

                st.write(context)

        else:

            st.warning("Please enter a question.")