import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Root of the project (DocSage)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Where ChromaDB persists its data
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR"))

# Set the embedding model to use
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}