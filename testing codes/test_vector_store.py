"""Test ChromaDB storage and retrieval"""
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings
from utils.vector_store import store_embeddings, search_similar_chunks, get_collection_stats

SAMPLE = "Python is a high-level programming language. " * 30

def test_store_and_search():
    chunks     = split_text(SAMPLE)
    embeddings = generate_embeddings(chunks)

    stored = store_embeddings(chunks, embeddings, source_name="test_doc.pdf")
    assert stored == len(chunks), "All chunks should be stored"

    query_emb = generate_embeddings(["What is Python?"])[0]
    results   = search_similar_chunks(query_emb, top_k=3)

    assert "documents" in results
    assert len(results["documents"][0]) > 0
    print(f"\nStored: {stored} chunks")
    print("Top result:", results["documents"][0][0][:200])

def test_stats():
    stats = get_collection_stats()
    assert "total_chunks" in stats
    print(f"\nStats: {stats}")
