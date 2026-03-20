"""
Test the if we can retrieve data, format the chunks retrieved 
and get the sources of documents used

"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import TOP_K
from src.ingestor import load_embedding_model
from src.retriever import retrieve, format_context, get_sources


embedding_model = load_embedding_model()
sample_test_queries = [

    "What's deliverables are expected?"
    "What's the deadline given?"
]
for query in sample_test_queries:
    chunks = retrieve(query, embedding_model, TOP_K)

    for i, chunk in enumerate(chunks):
        print(f"  [{i+1}] Source : {chunk['source']}")
        print(f"       Score  : {chunk['score']}")
        print(f"       Text   : {chunk['text'][:100].strip()}...") # You can comment out when you want to test this

    context = format_context(chunks)
    # print(context[:200]) You can comment out when you want to test this

    sources = get_sources(chunks)
    print(f"\n  Referenced docs: {sources}")

