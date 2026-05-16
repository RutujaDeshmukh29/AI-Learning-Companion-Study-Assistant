"""
Vector Store Module
====================
WHY we're improving from original:

CRITICAL BUG in original:
  store_embeddings() used str(i) as chunk IDs (0, 1, 2...).
  Upload PDF #1 -> stores IDs 0,1,2,3...
  Upload PDF #2 -> stores IDs 0,1,2,3... AGAIN -> overwrites PDF #1's chunks!
  This means in a multi-PDF session, only the LAST uploaded PDF exists in ChromaDB.

FIX: IDs are now SHA-256 hashes of (source_name + chunk_index + first 80 chars).
  Globally unique per document. Multiple PDFs coexist correctly.

NEW FEATURES:
- Source metadata stored with every chunk (enables "from: notes.pdf" citations)
- search_similar_chunks() returns source info alongside text
- get_all_sources() lets the UI show which PDFs are loaded
- delete_source() lets users remove a specific PDF from memory
- Collection stats for the sidebar display

Backward compatibility:
- store_embeddings(chunks, embeddings) still works (original signature).
- search_similar_chunks(query_embedding) still works.
  Both now accept optional source_name for multi-PDF support.
"""

import hashlib
import os
from typing import List, Dict, Any, Optional

import chromadb

# ChromaDB persists to disk here
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "study_materials"

# ── Singleton client + collection ───────────────────────────────────────────
_client     = None
_collection = None


def _get_collection():
    """Lazy-initialize and cache the ChromaDB collection."""
    global _client, _collection
    if _collection is None:
        os.makedirs(CHROMA_DIR, exist_ok=True)
        _client     = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ────────────────────────────────────────────────────────────────────────────
# PUBLIC: store_embeddings — backward-compatible (original signature)
# ────────────────────────────────────────────────────────────────────────────
def store_embeddings(
    chunks: List[str],
    embeddings,                       # numpy array or list-of-lists
    source_name: str = "document",
) -> int:
    """
    Store text chunks + embeddings in ChromaDB.

    Original signature: store_embeddings(chunks, embeddings)
    New optional arg:   source_name lets you tag which PDF these came from.

    Uses content-hash IDs so re-uploading the same PDF is idempotent
    and uploading multiple PDFs never corrupts each other.

    Returns number of chunks stored.
    """
    if not chunks:
        return 0

    collection = _get_collection()

    ids        = []
    docs       = []
    embs       = []
    metas      = []

    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        # Stable, unique ID: hash of source + position + content preview
        uid = hashlib.sha256(
            f"{source_name}::{i}::{chunk[:80]}".encode()
        ).hexdigest()[:32]

        # Convert numpy row to plain list if needed
        emb_list = emb.tolist() if hasattr(emb, "tolist") else list(emb)

        ids.append(uid)
        docs.append(chunk)
        embs.append(emb_list)
        metas.append({"source": source_name, "chunk_index": i})

    # upsert = insert or update — safe to call multiple times
    collection.upsert(ids=ids, documents=docs, embeddings=embs, metadatas=metas)
    return len(ids)


# ────────────────────────────────────────────────────────────────────────────
# PUBLIC: search_similar_chunks — backward-compatible
# ────────────────────────────────────────────────────────────────────────────
def search_similar_chunks(
    query_embedding,                  # numpy 1-D array or plain list
    top_k: int = 5,
    source_filters: Optional[List[str]] = None,
) -> dict:
    """
    Retrieve the most semantically similar chunks for a query embedding.

    Original return shape is preserved:
        {"documents": [[chunk1, chunk2, ...]], "metadatas": [[...]], ...}
    so existing code (test_rag.py, rag_pipeline.py) still works unchanged.

    New: source_filters lets you limit retrieval to a list of PDFs.
    New: metadatas[0] now contains {"source": "...", "chunk_index": N}.
    """
    collection = _get_collection()
    total = collection.count()
    if total == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Convert numpy to list
    qe = query_embedding.tolist() if hasattr(query_embedding, "tolist") else list(query_embedding)

    kwargs = dict(
        query_embeddings=[qe],
        n_results=min(top_k, total),
        include=["documents", "metadatas", "distances"],
    )
    if source_filters:
        if len(source_filters) == 1:
            kwargs["where"] = {"source": source_filters[0]}
        else:
            kwargs["where"] = {"source": {"$in": source_filters}}

    return collection.query(**kwargs)


# ────────────────────────────────────────────────────────────────────────────
# PUBLIC: higher-level helpers used by app.py / rag_pipeline.py
# ────────────────────────────────────────────────────────────────────────────
def store_chunks(
    chunks: List[str],
    source_name: str,
    embeddings_list: List[List[float]] = None,
) -> int:
    """
    Convenience wrapper: store pre-split chunks.
    If embeddings_list is None, generates them here.
    Returns number of chunks stored.
    """
    if embeddings_list is None:
        from utils.embeddings import create_embeddings
        embeddings_list = create_embeddings(chunks)
    return store_embeddings(chunks, embeddings_list, source_name=source_name)


def retrieve_relevant_chunks(
    query: str,
    n_results: int = 5,
    source_filters: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    High-level retrieval: accepts a raw query string, returns rich dicts.

    Returns:
        [{"text": "...", "source": "notes.pdf", "chunk_index": 0,
          "similarity": 0.87}, ...]
    """
    from utils.embeddings import create_embeddings
    qe      = create_embeddings([query])[0]
    results = search_similar_chunks(qe, top_k=n_results, source_filters=source_filters)

    retrieved = []
    docs  = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, dists):
        retrieved.append({
            "text":        doc,
            "source":      meta.get("source", "unknown"),
            "chunk_index": meta.get("chunk_index", 0),
            "similarity":  round(1 - dist, 3),
        })
    return retrieved


def get_all_sources() -> List[str]:
    """Return list of unique source document names in the collection."""
    collection = _get_collection()
    if collection.count() == 0:
        return []
    result = collection.get(include=["metadatas"])
    return list({m.get("source", "unknown") for m in result["metadatas"] if m is not None})


def delete_source(source_name: str) -> bool:
    """Delete all chunks belonging to a specific source document."""
    collection = _get_collection()
    collection.delete(where={"source": source_name})
    return True


def get_collection_stats() -> Dict[str, Any]:
    """Return stats dict for UI sidebar display."""
    collection = _get_collection()
    sources    = get_all_sources()
    return {
        "total_chunks":    collection.count(),
        "total_documents": len(sources),
        "sources":         sources,
    }
