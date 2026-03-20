"""
Test our RAG pipeline

"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine import load_llm


llm = load_llm()