"""
Text Splitter Module
=====================
WHY upgraded from original:
- Original split_text() cut at exact character counts -> mid-sentence breaks
  like "...the neural net" | "work learns by..." which hurts LLM quality.
- New version respects sentence boundaries. Every chunk is semantically
  complete and reads naturally when injected into a RAG prompt.

Backward compatibility:
- split_text(text, chunk_size, overlap) still works -> test files unchanged.
- split_into_chunks() also available for any new code that calls it.
"""

import re
from typing import List


def split_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Split text into sentence-aware, overlapping chunks.
    Drop-in replacement for original character-based version.
    Same call signature -- all test files (test_splitter.py, test_rag.py,
    test_vector_store.py) continue to work without changes.
    """
    if not text or not text.strip():
        return []

    text      = _normalize(text)
    sentences = _split_sentences(text)
    chunks    = []
    current   = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            overlap_text = _get_overlap(current, overlap)
            current = (overlap_text + " " + sentence).strip() if overlap_text else sentence

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) > 40]


def split_into_chunks(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
    """Alias for split_text() using the chunk_overlap kwarg name."""
    return split_text(text, chunk_size=chunk_size, overlap=chunk_overlap)


def split_text_with_metadata(text: str, source_name: str, chunk_size: int = 800, overlap: int = 150) -> List[dict]:
    """
    Same as split_text() but returns dicts with chunk + source metadata.
    Used by rag_pipeline.py to enable source citations in AI responses.
    Returns: [{"text": "...", "source": "file.pdf", "chunk_index": 0}, ...]
    """
    chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)
    return [
        {"text": chunk, "source": source_name, "chunk_index": i}
        for i, chunk in enumerate(chunks)
    ]


def _normalize(text: str) -> str:
    """Remove PDF artifacts, normalize whitespace."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text.strip()


def _split_sentences(text: str) -> List[str]:
    """Tokenize text at punctuation + paragraph boundaries."""
    raw = re.split(r'(?<=[.!?])\s+|\n\n+', text)
    sentences = []
    for frag in raw:
        frag = frag.strip()
        if not frag:
            continue
        if len(frag) > 600:
            sentences.extend([s.strip() for s in frag.split('\n') if s.strip()])
        else:
            sentences.append(frag)
    return sentences


def _get_overlap(text: str, overlap_size: int) -> str:
    """Return tail of text as leading context for the next chunk."""
    if not text or overlap_size <= 0:
        return ""
    tail  = text[-overlap_size:] if len(text) > overlap_size else text
    match = re.search(r'(?<=[.!?])\s+', tail)
    if match and match.end() < len(tail) - 30:
        return tail[match.end():].strip()
    return tail.strip()
