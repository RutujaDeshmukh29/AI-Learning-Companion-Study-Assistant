"""
Text Splitter Module
Splits extracted text into semantic chunks optimized for RAG retrieval
"""

import re
from typing import List


def split_into_chunks(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[str]:
    """
    Split text into overlapping chunks for RAG.
    
    Args:
        text: Full document text
        chunk_size: Target characters per chunk
        chunk_overlap: Overlap between consecutive chunks
        
    Returns:
        List of text chunks
    """
    # First try to split by paragraphs
    paragraphs = split_by_paragraphs(text)
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # If adding this paragraph won't exceed chunk_size, add it
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk = (current_chunk + "\n\n" + paragraph).strip()
        else:
            # Save current chunk if it has content
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If paragraph itself is too long, split it by sentences
            if len(paragraph) > chunk_size:
                sentence_chunks = split_long_paragraph(paragraph, chunk_size, chunk_overlap)
                chunks.extend(sentence_chunks[:-1])
                current_chunk = sentence_chunks[-1] if sentence_chunks else ""
            else:
                # Start new chunk, carry over overlap from previous
                overlap_text = get_overlap_text(current_chunk, chunk_overlap)
                current_chunk = (overlap_text + "\n\n" + paragraph).strip() if overlap_text else paragraph
    
    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Filter out tiny chunks
    chunks = [c for c in chunks if len(c.strip()) > 50]
    
    return chunks


def split_by_paragraphs(text: str) -> List[str]:
    """Split text by double newlines (paragraphs)."""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def split_long_paragraph(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split a long paragraph into sentence-based chunks."""
    # Split by sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            overlap_text = get_overlap_text(current_chunk, overlap)
            current_chunk = (overlap_text + " " + sentence).strip() if overlap_text else sentence
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def get_overlap_text(text: str, overlap_size: int) -> str:
    """Get the last `overlap_size` characters of text for context continuity."""
    if not text or overlap_size <= 0:
        return ""
    
    if len(text) <= overlap_size:
        return text
    
    # Try to find a sentence boundary in the overlap region
    overlap_candidate = text[-overlap_size:]
    sentence_start = overlap_candidate.find('. ')
    
    if sentence_start != -1 and sentence_start < overlap_size - 50:
        return overlap_candidate[sentence_start + 2:].strip()
    
    return overlap_candidate.strip()


def add_chunk_metadata(chunks: List[str], source_name: str) -> List[dict]:
    """
    Add metadata to each chunk for better retrieval.
    
    Args:
        chunks: List of text chunks
        source_name: Name of the source document
        
    Returns:
        List of dicts with chunk text and metadata
    """
    return [
        {
            "text": chunk,
            "metadata": {
                "source": source_name,
                "chunk_index": i,
                "chunk_length": len(chunk),
            }
        }
        for i, chunk in enumerate(chunks)
    ]