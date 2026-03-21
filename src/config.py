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

# Current supported file extensions
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

# Chunk size and the overlap to use
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))

# Number of relevant chunks to retrieve per query
TOP_K = int(os.getenv("TOP_K", 4))

# model path
MODEL_PATH = Path(os.getenv("MODEL_PATH"))

# Number of tokens the model can process in one pass
# Larger = more context but more RAM usage
N_CTX = int(os.getenv("N_CTX"))

# Controls randomness in responses (0.0 = deterministic, 1.0 = creative)
TEMPERATURE = float(os.getenv("TEMPERATURE"))