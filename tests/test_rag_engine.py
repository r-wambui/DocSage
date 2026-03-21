"""
Test our RAG pipeline

"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestor import load_embedding_model
from src.rag_engine import load_llm, ask


llm = load_llm()
embedding_model = load_embedding_model()


sample_test_queries = [

    "What's deliverables are expected?"
    "What's the deadline given?"
]
for query in sample_test_queries:

    result = ask(query, llm, embedding_model)
 
    print(f"  A: {result['answer']}")
    print(f"\n  Sources used: {result['sources']}")
    print(f"  Chunks retrieved: {len(result['chunks'])}")
    print(f"  Top chunk score: {result['chunks'][0]['score']}")
 