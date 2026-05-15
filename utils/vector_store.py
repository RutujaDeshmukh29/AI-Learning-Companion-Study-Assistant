import chromadb

# Create Chroma client
client = chromadb.PersistentClient(path="chroma_db")

# Create/get collection
collection = client.get_or_create_collection(
    name="study_materials"
)


def store_embeddings(chunks, embeddings):
    """
    Store chunks and embeddings in ChromaDB.
    """

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        collection.add(
            ids=[str(i)],
            embeddings=[embedding.tolist()],
            documents=[chunk]
        )

    print("Embeddings stored successfully!")


def search_similar_chunks(query_embedding, top_k=3):
    """
    Retrieve similar chunks from ChromaDB.
    """

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

    return results