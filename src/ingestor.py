"""

Responsiple for the whole ingestion pipeline

Folder check > file loading > text cleaning > chunking > embedding > store in chromadb

"""
import chromadb

def get_chroma_collection() -> chromadb.Collection:

    """
    Initialises a persistent ChromaDB client and returns the collection.
    ChromaDB store data to disk at CHROMA_PERSIST_DIR so you only need to 
    add collection once

    """

    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
    collection = client.get_or_create_collection(
        name="docsage",
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )
    return collection