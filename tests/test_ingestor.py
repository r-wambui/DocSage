"""
Test if the ingestor pipeline os working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestor import get_chroma_collection, load_embedding_model, ingest_folder


collection = get_chroma_collection()
embedding_model = load_embedding_model()

# Ingest the docs folder in the test directory
sample_folder = str(Path(__file__).parent / "docs")
total_chunks = ingest_folder(sample_folder, embedding_model)
print(f"\n  Chunks ingested  : {total_chunks}")

# verify collection in chromadb
collection = get_chroma_collection()
count = collection.count()
print(f"  ChromaDB count   : {count}")
