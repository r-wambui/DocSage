"""
Test if the ingestor pipeline os working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestor import get_chroma_collection


collection = get_chroma_collection()

print(collection)