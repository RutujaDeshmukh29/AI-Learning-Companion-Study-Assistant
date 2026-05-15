"""
Vector Store Module
Manages ChromaDB for storing and retrieving document embeddings
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import hashlib
import os

from utils.embeddings import create_embeddings, create_single_embedding

# ChromaDB persistence directory
CHROMA_DIR = "chroma_db"


def get_chroma_client() -> chromadb.Client:
    """
    Initialize and return a persistent ChromaDB client.
    
    Returns:
        ChromaDB client instance
    """
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client


def get_or_create_collection(collection_name: str = "study_documents"):
    """
    Get or create a ChromaDB collection.
    
    Args:
        collection_name: Name for the collection
        
    Returns:
        ChromaDB collection object
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection


def store_chunks(
    chunks: List[str],
    source_name: str,
    collection_name: str = "study_documents"
) -> int:
    """
    Store text chunks with their embeddings in ChromaDB.
    
    Args:
        chunks: List of text chunks
        source_name: Source document name for metadata
        collection_name: ChromaDB collection name
        
    Returns:
        Number of chunks stored
    """
    if not chunks:
        return 0
    
    collection = get_or_create_collection(collection_name)
    
    # Generate unique IDs for each chunk
    ids = [
        hashlib.md5(f"{source_name}_{i}_{chunk[:50]}".encode()).hexdigest()
        for i, chunk in enumerate(chunks)
    ]
    
    # Create embeddings for all chunks
    embeddings = create_embeddings(chunks)
    
    # Build metadata list
    metadatas = [
        {"source": source_name, "chunk_index": i}
        for i in range(len(chunks))
    ]
    
    # Upsert to ChromaDB (handles duplicates gracefully)
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    return len(chunks)


def retrieve_relevant_chunks(
    query: str,
    n_results: int = 5,
    collection_name: str = "study_documents",
    source_filter: str = None
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant chunks for a given query.
    
    Args:
        query: User's question or query text
        n_results: Number of chunks to retrieve
        collection_name: ChromaDB collection name
        source_filter: Optional filter by source document name
        
    Returns:
        List of dicts with document text and metadata
    """
    collection = get_or_create_collection(collection_name)
    
    # Check if collection has documents
    if collection.count() == 0:
        return []
    
    # Create query embedding
    query_embedding = create_single_embedding(query)
    
    # Build where filter if source specified
    where_filter = {"source": source_filter} if source_filter else None
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    retrieved = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            retrieved.append({
                "text": doc,
                "source": meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "similarity": 1 - dist  # Convert distance to similarity
            })
    
    return retrieved


def get_all_sources(collection_name: str = "study_documents") -> List[str]:
    """
    Get list of all unique source documents in the collection.
    
    Returns:
        List of source document names
    """
    collection = get_or_create_collection(collection_name)
    
    if collection.count() == 0:
        return []
    
    results = collection.get(include=["metadatas"])
    sources = list(set(
        meta.get("source", "unknown")
        for meta in results["metadatas"]
    ))
    return sources


def delete_source(source_name: str, collection_name: str = "study_documents") -> bool:
    """
    Delete all chunks from a specific source document.
    
    Args:
        source_name: Name of the source to delete
        collection_name: Collection name
        
    Returns:
        True if successful
    """
    collection = get_or_create_collection(collection_name)
    collection.delete(where={"source": source_name})
    return True


def get_collection_stats(collection_name: str = "study_documents") -> Dict[str, Any]:
    """Get statistics about the current collection."""
    collection = get_or_create_collection(collection_name)
    count = collection.count()
    sources = get_all_sources(collection_name)
    
    return {
        "total_chunks": count,
        "total_documents": len(sources),
        "sources": sources
    }