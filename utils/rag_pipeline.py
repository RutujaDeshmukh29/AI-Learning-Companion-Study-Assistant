"""
RAG Pipeline Module
====================
WHY we're restructuring the original:

Original run_rag_pipeline() did EVERYTHING on every question:
  1. Extract PDF text
  2. Split into chunks
  3. Generate ALL embeddings
  4. Store in ChromaDB
  5. Generate query embedding
  6. Retrieve chunks
  7. Build prompt
  8. Call LLM

Problems with that approach:
  - Steps 1-4 (indexing) ran on EVERY question, even if the PDF hadn't changed.
    For a 100-page PDF this means generating ~200 embeddings per question = very slow.
  - No separation of concerns: indexing and querying were tangled together.

New architecture:
  - index_document(pdf_path)  -> run ONCE when PDF is uploaded
  - query_rag(question, ...)  -> run on every question (fast, retrieval only)
  - run_rag_pipeline()        -> kept for full backward compatibility with test files

Additional improvements:
  - Source citations returned alongside the answer
  - Learning mode passed through to prompt builder
  - Chat history context for follow-up questions
  - Proper error handling at each stage
"""

import os
from typing import Tuple, List, Dict, Any, Optional

from utils.pdf_loader    import extract_text_from_pdf
from utils.text_splitter import split_text, split_text_with_metadata
from utils.embeddings    import create_embeddings
from utils.vector_store  import store_embeddings, search_similar_chunks, get_collection_stats
from utils.llm           import ask_llm
from utils.prompts       import build_rag_prompt


# ────────────────────────────────────────────────────────────────────────────
# PHASE 1 — INDEXING  (call once per document upload)
# ────────────────────────────────────────────────────────────────────────────
def index_document(pdf_path: str, source_name: str = None) -> Dict[str, Any]:
    """
    Extract, chunk, embed, and store a PDF into ChromaDB.
    Call this ONCE when the user uploads a PDF.
    Do NOT call this on every question.

    Args:
        pdf_path:    Absolute or relative path to the PDF file.
        source_name: Display name for citations. Defaults to filename.

    Returns:
        {"success": True, "chunks": N, "source": "...", "characters": N}
        or
        {"success": False, "error": "..."}
    """
    if not os.path.exists(pdf_path):
        return {"success": False, "error": f"File not found: {pdf_path}"}

    source_name = source_name or os.path.basename(pdf_path)

    try:
        # Step 1: Extract
        text = extract_text_from_pdf(pdf_path)
        if len(text.strip()) < 100:
            return {"success": False, "error": "PDF appears to be empty or scanned (no extractable text)."}

        # Step 2: Split
        chunks = split_text(text)
        if not chunks:
            return {"success": False, "error": "Could not split document into usable chunks."}

        # Step 3 & 4: Embed + Store
        embeddings = create_embeddings(chunks)
        stored     = store_embeddings(chunks, embeddings, source_name=source_name)

        return {
            "success":    True,
            "chunks":     stored,
            "source":     source_name,
            "characters": len(text),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ────────────────────────────────────────────────────────────────────────────
# PHASE 2 — QUERYING  (call on every user question)
# ────────────────────────────────────────────────────────────────────────────
def query_rag(
    question: str,
    top_k: int = 5,
    learning_mode: str = "Beginner",
    chat_history: Optional[List[Dict]] = None,
    source_filter: str = None,
    username: str = None,
) -> Tuple[str, List[str]]:
    """
    Retrieve relevant chunks and generate an LLM answer for a question.
    Does NOT touch the PDF or regenerate embeddings.

    Args:
        question:      The user's question.
        top_k:         Number of chunks to retrieve from ChromaDB.
        learning_mode: Teaching style (Beginner/Exam/Practical/Interview).
        chat_history:  Previous turns for conversational context.
        source_filter: Limit retrieval to one specific PDF (by name).
        username:      For personalised prompt greeting.

    Returns:
        (answer_str, [retrieved_chunk_texts])
    """
    stats = get_collection_stats()
    if stats["total_chunks"] == 0:
        return (
            "📭 No study material found. Please upload a PDF first using the Upload tab.",
            []
        )

    try:
        # Step 1: Embed the question
        query_embedding = create_embeddings([question])[0]

        # Step 2: Retrieve similar chunks
        results         = search_similar_chunks(
            query_embedding,
            top_k=top_k,
            source_filter=source_filter,
        )
        retrieved_chunks = results.get("documents", [[]])[0]

        if not retrieved_chunks:
            return (
                "🔍 I couldn't find relevant content for that question. "
                "Try rephrasing or check that the right PDF is uploaded.",
                []
            )

        # Step 3: Build context string
        context = "\n\n".join(retrieved_chunks)

        # Step 4: Build mode-aware prompt
        prompt = build_rag_prompt(
            context=context,
            question=question,
            learning_mode=learning_mode,
            chat_history=chat_history,
            username=username,
        )

        # Step 5: Generate answer
        answer = ask_llm(prompt)

        # Attach source citations if metadata available
        metas = results.get("metadatas", [[]])[0]
        sources_seen = []
        for meta in metas:
            if meta:
                src = meta.get("source", "")
                if src and src not in sources_seen:
                    sources_seen.append(src)

        if sources_seen:
            answer += f"\n\n*📎 Sources: {', '.join(sources_seen)}*"

        return answer, retrieved_chunks

    except Exception as e:
        return f"⚠️ Error during retrieval: {str(e)}", []


# ────────────────────────────────────────────────────────────────────────────
# BACKWARD COMPATIBILITY — run_rag_pipeline
# ────────────────────────────────────────────────────────────────────────────
def run_rag_pipeline(pdf_path: str, question: str) -> Tuple[str, List[str]]:
    """
    Original function signature — preserved for test files and old app.py.

    Difference from original: indexing only re-runs if the collection is empty
    OR the document hasn't been indexed yet (checks by source name).
    This prevents re-embedding on every question.
    """
    source_name = os.path.basename(pdf_path)
    stats       = get_collection_stats()

    # Only index if this source is not already in the DB
    if source_name not in stats.get("sources", []):
        result = index_document(pdf_path, source_name=source_name)
        if not result["success"]:
            return f"❌ Indexing failed: {result['error']}", []

    return query_rag(question, source_filter=source_name)
