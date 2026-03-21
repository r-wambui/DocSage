"""
Responsible for reading/retriecing the data/vectors stored in chromadb

Given a user query, it:
    1. Embeds the query using the SAME model used during ingestion - IMPORTANT
    2. Searches ChromaDB for the most semantically similar chunks
    3. Returns those chunks as context for the LLM

"""
from typing import List, Dict

from sentence_transformers import SentenceTransformer

from src.config import TOP_K
from src.ingestor import get_chroma_collection


def retrieve(query:str, embedding_model: SentenceTransformer, top_k: int = TOP_K) -> List[Dict]:
    """"
    Finds the most relevant document chunk foe the user query

    Args:
        query          : The user's question or search string
        embedding_model: The same SentenceTransformer used during ingestion
        top_k          : How many chunks to return (default from config.py)
 
    Returns:
        List of dicts, each containing:
            - text         : The chunk content
            - source       : The filename it came from
            - chunk_index  : Position of this chunk within its source file
            - score        : Similarity score (0-1, higher = more relevant)
    """
    collection = get_chroma_collection()

     # Check if collection is empty
    if collection.count() == 0:
        raise ValueError(
            "[DocSage] Vector store is empty. "
            "Please ingest a folder first."
        )

    # Embed the query
    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    # Query ChromaDB for the top_k most similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    # Format the results
    chunks = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
 
    for doc, meta, distance in zip(documents, metadatas, distances):
        chunks.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "chunk_index": meta.get("chunk_index", 0),
            "score": round(1 - distance, 4),
        })
 
    return chunks


def format_context(chunks: List[Dict]) -> str:
    """
    Format the retrieved chunks into a string to feed to the LLM
    
    Each chunk is labelled with its source file so the LLM can reference
    where information came from, which reduces hallucination.
    """
    context = []
    for chunk in chunks:
        context.append(
            f"[Source: {chunk['source']}]\n{chunk['text']}"
        )
    return "\n\n".join(context)


def get_sources(chunks: List[Dict]) -> List[str]:
    """
    Returns a list of source filenames where the chuinks were retrieved.
    Used in the UI to show users sources referenced
    """
    seen = set()
    sources = []
    for chunk in chunks:
        src = chunk["source"]
        if src not in seen:
            seen.add(src)
            sources.append(src)
    return sources

 