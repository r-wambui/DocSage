import os
from pathlib import Path

# Root of the project (DocSage)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Where ChromaDB persists its data
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(ROOT_DIR / "vectorstore")))