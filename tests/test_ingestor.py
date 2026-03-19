"""
Test if the ingestor pipeline os working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestor import get_chroma_collection, load_embedding_model, scan_folder


collection = get_chroma_collection()
embedding_model = load_embedding_model()

# Ingest the docs folder in the test directory
sample_folder = str(Path(__file__).parent / "docs")
print(sample_folder)
total = scan_folder(sample_folder)

print(total)