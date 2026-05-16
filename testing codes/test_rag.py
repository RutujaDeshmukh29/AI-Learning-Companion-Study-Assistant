"""Integration test: full RAG pipeline"""
from utils.rag_pipeline import run_rag_pipeline
import os

PDF_PATH = "data/uploaded_pdfs/python_notes.pdf"

def test_rag_pipeline():
    if not os.path.exists(PDF_PATH):
        print(f"\nSkipped: {PDF_PATH} not found.")
        return
    answer, chunks = run_rag_pipeline(PDF_PATH, "What is Python?")
    assert isinstance(answer, str)
    assert len(answer) > 10
    print(f"\nAnswer:\n{answer}\n")
    print(f"Retrieved {len(chunks)} chunks")

def test_rag_no_pdf():
    """Should return graceful error, not crash."""
    answer, chunks = run_rag_pipeline("data/nonexistent.pdf", "test question")
    assert "❌" in answer or "not found" in answer.lower()
    print(f"\nGraceful error: {answer}")
