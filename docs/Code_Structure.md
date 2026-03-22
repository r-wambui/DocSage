# Code Structure

This page is a complete reference for every file in DocSage - what it does,
why it exists, and how it connects to the rest of the system.

---

## Full Project Layout

```
docsage/
│
├── src/                          # Core Python package
│   ├── __init__.py               # Marks src/ as a Python package
│   ├── config.py                 # All settings — single source of truth
│   ├── ingestor.py               # Ingestion pipeline (write side)
│   ├── retriever.py              # Semantic search (read side)
│   ├── rag_engine.py                  # RAG orchestration + LLM inference
│   └── ui/
│       ├── __init__.py
│       └── app.py                # Streamlit interface
│
├── tests/
│   ├── __init__.py
|   ├── sample_docs/                      # Sample files for quick demofolder to ingest  
│   ├── test_ingestor.py          # Verify document processing
│   ├── test_retriever.py         # Verify semantic search
│   └── test_rag_engine.py             # Verify LLM inference end-to-end
│
├── models/                       # GGUF model files (gitignored)
│   └── mistral-7b-instruct-v0.2.Q4_K_M.gguf
|   └── Phi-3-mini-4k-instruct-q4.gguf
│
├── vectorstore/                  # ChromaDB persistence (gitignored)
│
├── docs/                         # Documentation
│
├── .env                          # Your local settings (gitignored)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Module Reference

### `src/config.py`

**Responsibility:** Single source of truth for all application settings.

Every other module imports constants from here. Nothing is hardcoded anywhere else
in the codebase — paths, model names, chunk sizes, and tuning parameters all
live here, loaded from `.env` at startup.

## Configuration Reference

| Export | Type | Purpose |
|--------|------|---------|
| `ROOT_DIR` | `Path` | Root directory of the DocSage project |
| `CHROMA_PERSIST_DIR` | `Path` | Directory where ChromaDB stores embeddings |
| `EMBEDDING_MODEL` | `str` | HuggingFace model used to generate embeddings |
| `SUPPORTED_EXTENSIONS` | `set` | File types supported for document ingestion |
| `CHUNK_SIZE` | `int` | Number of characters per document chunk |
| `CHUNK_OVERLAP` | `int` | Overlap between consecutive chunks |
| `TOP_K` | `int` | Number of top relevant chunks retrieved per query |
| `MODEL_PATH` | `Path` | Path to the `.gguf` language model file |
| `N_CTX` | `int` | Maximum number of tokens the model can process |
| `TEMPERATURE` | `float` | Controls randomness of model output |

**Depends on:** nothing (only stdlib + `python-dotenv`)

---

### `src/ingestor.py`

**Responsibility:** The write side of DocSage. Processes a folder of documents
and stores their embeddings in ChromaDB.

| Function | Purpose |
|----------|---------|
| `get_chroma_collection()` | Initialises ChromaDB client and returns the collection |
| `load_embedding_model()` | Loads `nomic-embed-text-v1` via sentence-transformers |
| `scan_folder(folder_path)` | Recursively finds all supported files in a folder |
| `load_file(file_path)` | Dispatches to the correct loader by file extension |
| `clean_text(text)` | Light text normalisation before chunking |
| `chunk_text(text, source)` | Splits text into overlapping fixed-size chunks |
| `ingest_folder(folder, model)` | Full pipeline — scan → load → chunk → embed → store |

**Depends on:** `config.py`, `chromadb`, `sentence_transformers`, `pypdf`

---

### `src/retriever.py`

**Responsibility:** The read side of DocSage. Given a user query, finds the
most semantically relevant chunks from the vector store.

| Function | Purpose |
|----------|---------|
| `retrieve(query, model, top_k)` | Embeds query and searches ChromaDB for top-k chunks |
| `format_context(chunks)` | Formats chunks into a labelled string for the LLM prompt |
| `get_sources(chunks)` | Returns deduplicated list of source filenames |

**Depends on:** `config.py`, `ingestor.get_chroma_collection()`, `sentence_transformers`

---

### `src/rag_engine.py`

**Responsibility:** Orchestrates the full RAG pipeline. Connects retrieval to
LLM inference and returns a grounded answer with sources.

| Function | Purpose |
|----------|---------|
| `load_llm()` | Loads the GGUF model via llama-cpp-python |
| `build_prompt(query, context)` | Builds a Mistral `[INST]` formatted prompt |
| `ask(query, llm, model)` | Full RAG pipeline — returns complete answer dict |
| `ask_stream(query, llm, model)` | Streaming version — yields tokens then metadata |

**Depends on:** `config.py`, `retriever.py`, `llama_cpp`

---

### `src/ui/app.py`

**Responsibility:** The Streamlit interface. Handles all user interaction —
folder selection, ingestion, chat display, and streaming responses.

| Section | Purpose |
|---------|---------|
| Session state init | Persists chat history, ingestion status, and folder path across reruns |
| `@st.cache_resource` | Ensures LLM and embedding model load exactly once |
| Sidebar | Folder picker, ingest button, status display, clear chat |
| Chat history | Renders previous messages with source expanders |
| Chat input | Triggers `ask_stream()`, renders tokens live with `▌` cursor |

**Depends on:** `config.py`, `ingestor.py`, `chain.py`

---


## Key Design Decisions

**No LangChain** — The RAG pipeline is implemented directly without an orchestration
framework. This keeps every step visible and understandable. LangChain would have
abstracted away the exact moments where embedding, retrieval, prompt building, and
inference happen — which are the most important parts to understand.

**Separate embedding and generation models** — `nomic-embed-text-v1` handles
representation, `mistral-7b-instruct` handles generation. Using a chat model for
embeddings is a common mistake — chat models aren't trained to produce
geometrically meaningful vector representations.

**In-process everything** — ChromaDB runs inside the same Python process.
llama-cpp-python runs inference in-process via direct bindings. No servers,
no Docker, no infrastructure. A developer can clone the repo and have a running
app in minutes.

**Test files mirror module structure** — every module in `src/` has a
corresponding test in `tests/`. Tests are standalone scripts that can be run
individually, making debugging straightforward during development.
