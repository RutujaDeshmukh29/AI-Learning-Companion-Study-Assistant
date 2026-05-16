"""Test embedding generation"""
from utils.text_splitter import split_text
from utils.embeddings import generate_embeddings

SAMPLE = "Neural networks learn by adjusting weights during backpropagation. " * 20

def test_generate_embeddings():
    chunks = split_text(SAMPLE)
    embeddings = generate_embeddings(chunks)
    assert len(embeddings) == len(chunks), "One embedding per chunk"
    assert len(embeddings[0]) == 384, "all-MiniLM-L6-v2 produces 384-dim vectors"
    print(f"\nChunks: {len(chunks)}, Embedding shape: ({len(embeddings)}, {len(embeddings[0])})")
