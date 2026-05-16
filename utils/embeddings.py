"""
Embeddings Module
Creates sentence embeddings using sentence-transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Use a lightweight but powerful model for fast local embeddings
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None  # Singleton model instance


def get_embedding_model() -> SentenceTransformer:
    """
    Load or return cached embedding model (singleton pattern).
    
    Returns:
        SentenceTransformer model instance
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks.
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of embedding vectors (as lists of floats)
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def create_single_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text string.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as list of floats
    """
    model = get_embedding_model()
    embedding = model.encode([text], show_progress_bar=False, convert_to_numpy=True)
    return embedding[0].tolist()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
        
    Returns:
        Cosine similarity score between 0 and 1
    """
    a = np.array(vec1)
    b = np.array(vec2)
    
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return float(np.dot(a, b) / (norm_a * norm_b))
