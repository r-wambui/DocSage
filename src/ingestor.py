"""

Responsiple for the whole ingestion pipeline

Folder check > file loading > text cleaning > chunking > embedding > store in chromadb

"""
import re
import hashlib
from typing import List, Dict
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

from src.config import (CHROMA_PERSIST_DIR, 
                        EMBEDDING_MODEL, 
                        SUPPORTED_EXTENSIONS,
                        CHUNK_SIZE,
                        CHUNK_OVERLAP)

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

def _load_pdf(file_path: Path) -> str:
    """
    Extract text from all pages of a pdf

    """
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)

def _load_text(file_path: Path) -> str:
    """

    Reads plain text and markdown files.

    """
    return file_path.read_text(encoding="utf-8", errors="ignore")

def load_file(file_path: Path) -> str:
    """
    Load and return text from different supported files, pdf and text files

    """

    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return _load_pdf(file_path)
    elif ext in {".md", ".txt"}:
        return _load_text(file_path)
    else:
        raise ValueError(f"[DocSage] Unsupported file type: {ext}")

def clean_text(text: str) -> str:
    """
    Clean text:
        1. Remove execessive blank spaces
        2. Collapse multiple tabs
    """
    text = re.sub(r"\n{3,}", "\n\n", text) 
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = text.strip()
    return text

def chunk_text(text: str, source: str) -> List[Dict]:
    """
    Split the text into chunks, include overlapping so no context is lost

     Returns a list of dicts:
        {
            "text": "chunk content...",
            "source": "filename.pdf",
            "chunk_index": 0
        }
    """

    chunks = []
    start = 0
    index = 0 

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]

        if chunk.strip():   # skip empty chunks
            chunks.append({
                "text": chunk,
                "source": source,
                "chunk_index": index,
            })
            index += 1
        
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def _chunk_id(chunk: Dict) -> str:
    """
    Generates a stable unique ID for a chunk using an MD5 hash of its content.
    This avoids duplication when a folder is ingested more than onces

    """
    content = f"{chunk['source']}::{chunk['chunk_index']}::{chunk['text']}"
    return hashlib.md5(content.encode()).hexdigest()

def ingest_folder(folder_path: str, embedding_model: SentenceTransformer) -> int:
    """

    This is the full ingestion pipeline of our folder:

        1. Scans folder for the support files
        2. Load the files
        3. Cleaning the text extracte from the files
        4. Chunking the text
        5. Embed each chunk
        6. Store in chromaDb
    
    Returns the total number of chunks stored.
    """
    collection = get_chroma_collection()
    files = scan_folder(folder_path)

    all_chunks = []

    for file_path in files:
        print(f"[DocSage] Processing: {file_path.name}")
        try:

            raw_text = load_file(file_path)
            clean = clean_text(raw_text)

            chunks = chunk_text(clean, source=file_path.name)
            all_chunks.extend(chunks)
            print(f"           → {len(chunks)} chunks")

        except Exception as e:
            print(f"[DocSage] ⚠ Error processing {file_path.name}: {e}")
            continue

    if not all_chunks:
        raise ValueError("[DocSage] No chunks generated — check your documents.")

    ## Embedding the chunks using batch size
    print(f"\n[DocSage] Embedding {len(all_chunks)} chunks (this may take a moment)...")
    texts = [c["text"] for c in all_chunks]
    embeddings = embedding_model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    ## Store in ChromaDb (Skipping duplicates using _chunk_id)
    print("[DocSage] Storing in vector database...")
    collection.upsert(
        ids=[_chunk_id(c) for c in all_chunks],
        documents=[c["text"] for c in all_chunks],
        embeddings=embeddings.tolist(),
        metadatas=[{"source": c["source"], "chunk_index": c["chunk_index"]} for c in all_chunks],
    )
 
    print(f"[DocSage] Ingestion complete — {len(all_chunks)} chunks stored.\n")
    return len(all_chunks)
 
 

