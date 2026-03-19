"""

Responsiple for the whole ingestion pipeline

Folder check > file loading > text cleaning > chunking > embedding > store in chromadb

"""
from typing import List
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import (CHROMA_PERSIST_DIR, 
                        EMBEDDING_MODEL, 
                        SUPPORTED_EXTENSIONS)

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


def load_embedding_model() -> SentenceTransformer:
    """
    Loads the embedding model from HuggingFace (cached locally after first download).

    """
    print(f"[DocSage] Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL, trust_remote_code=True)
    print("[DocSage] Embedding model ready.")
    return model


def scan_folder(folder_path: str) -> List[Path]:
    """
    Scans a folder recursively and returns all supported files listed in the config. 

    """
    folder = Path(folder_path)

    # check if folder exists and is a directory
    if not folder.exists():
        raise FileNotFoundError(f"[DocSage] Folder not found: {folder_path}")
    if not folder.is_dir():
        raise NotADirectoryError(f"[DocSage] Path is not a folder: {folder_path}")

    # get all supported files
    files = [
        f for f in folder.rglob("*")
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
        and f.is_file()
    ]

    if not files:
        raise ValueError(
            f"[DocSage] No supported files found in: {folder_path}\n"
            f"Supported types: {SUPPORTED_EXTENSIONS}"
        )
 
    print(f"[DocSage] Found {len(files)} file(s) in {folder_path}")
    return files
 