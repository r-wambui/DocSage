import os

# Where ChromaDB persists its data
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(ROOT_DIR / "vectorstore")))