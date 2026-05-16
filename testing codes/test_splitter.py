"""Test text splitter"""
from utils.text_splitter import split_text, split_into_chunks, split_text_with_metadata

SAMPLE = """
Machine learning is a subset of artificial intelligence.
It enables systems to learn from data without being explicitly programmed.
Supervised learning uses labelled training data to learn a mapping function.
Unsupervised learning finds patterns in data without labels.
Reinforcement learning trains agents through reward signals.
""" * 10  # repeat to make it long enough to chunk

def test_split_text():
    chunks = split_text(SAMPLE)
    assert len(chunks) > 0, "Should produce at least one chunk"
    for c in chunks:
        assert len(c) > 40, f"Chunk too short: {repr(c)}"
    print(f"\nTotal chunks: {len(chunks)}")
    print("First chunk:\n", chunks[0])

def test_split_into_chunks():
    """split_into_chunks is an alias — same behaviour."""
    chunks = split_into_chunks(SAMPLE)
    assert len(chunks) > 0

def test_split_with_metadata():
    result = split_text_with_metadata(SAMPLE, source_name="test.pdf")
    assert isinstance(result[0], dict)
    assert "text" in result[0] and "source" in result[0]
    assert result[0]["source"] == "test.pdf"
    print(f"\nMetadata chunks: {len(result)}")
