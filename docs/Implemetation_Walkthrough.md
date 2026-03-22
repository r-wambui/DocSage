# Implementation Walkthrough

This page walks through every module in DocSage, explaining the key decisions
made at each step. Read this if you want to understand exactly how it works
before modifying or extending it.

## `src/config.py` - Central Settings

All settings live in one place and are loaded from `.env` at startup.
No other module hardcodes paths, model names, or tuning parameters.


```python
# Where ChromaDB persists its data
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR"))

# Set the embedding model to use
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

```


## `src/ingestor.py` - Document Processing

The ingestion pipeline runs once per folder and writes to ChromaDB.

### Scanning

```python
def scan_folder(folder_path: str) -> List[Path]:
    files = [
        f for f in folder.rglob("*")   # recursive — handles nested folders
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
```

`rglob("*")` walks the entire directory tree recursively, so nested folder
structures are handled automatically.


### Loading

```python
def load_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return _load_pdf(file_path)
    elif ext in {".md", ".txt"}:
        return _load_text(file_path)
```

File loading is dispatched by extension. Adding a new format means adding
one `elif` branch and one loader function.

### Chunking

```python
def chunk_text(text: str, source: str) -> List[Dict]:
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        # Move forward by CHUNK_SIZE minus overlap
        start += CHUNK_SIZE - CHUNK_OVERLAP
```

Fixed-size chunking with overlap. The overlap (`CHUNK_OVERLAP=64`) ensures
context is preserved at chunk boundaries — a sentence split across two chunks
still appears complete in at least one.

### Deduplication

```python
def _chunk_id(chunk: Dict) -> str:
    content = f"{chunk['source']}::{chunk['chunk_index']}::{chunk['text']}"
    return hashlib.md5(content.encode()).hexdigest()
```

Each chunk gets an MD5 hash as its ChromaDB ID. ChromaDB's `upsert` skips
chunks that already exist, so re-ingesting the same folder is always safe.

### Embedding

```python
embeddings = embedding_model.encode(
    texts,
    batch_size=32,
    normalize_embeddings=True,  # required for cosine similarity
)
```

All chunks are embedded in one batch for efficiency. `normalize_embeddings=True`
is critical — without it, cosine similarity scores won't be meaningful.

---

## `src/retriever.py` - Semantic Search


### The Core Search

```python
query_embedding = embedding_model.encode(
    query,
    normalize_embeddings=True,
).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=min(top_k, collection.count()),
    include=["documents", "metadatas", "distances"],
)
```

The query is embedded using the **same model** used during ingestion.
This is a hard requirement — different models produce incompatible vector spaces.

### Distance to Similarity

```python
"score": round(1 - distance, 4)
```

ChromaDB returns cosine *distance* (0 = identical, 2 = opposite).
We convert to *similarity* (1 = identical, 0 = opposite) because it's
more intuitive to display and reason about.

### Context Formatting

```python
def format_context(chunks: List[Dict]) -> str:
    sections = []
    for chunk in chunks:
        sections.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(sections)
```

Each chunk is labelled with its source filename before being included in the prompt.
This allows the LLM to reference specific documents in its answer, which improves
accuracy and traceability.

## `src/rag_engine.py` - RAG Pipeline
### Prompt Engineering

When working with different LLM families, one important detail is that **each model expects a specific prompt format**. Using the wrong format can significantly degrade output quality.

In this project, we used both **Mistral** and **Phi**, each requiring a different prompt structure.



```python
d
def build_prompt(query: str, context: str) -> str:
    """
    Build the full prompmt to feed to Mistral model
    """

    system = (
        "You are DocSage, an AI assistant that answers questions using ONLY the provided context.\n\n"
        "Rules:\n"
        "1. Use only the information in the context.\n"
        "2. If the answer is not in the context, say: 'I could not find this in the provided documents.'\n"
        "3. Do NOT use prior knowledge.\n"
        "4. Be concise and accurate.\n"
        "5. Always reference the source document.(source: <filename>).\n"
    )
    # prmont for Minstral
    # prompt =  (
    #     f"[INST] {system}\n\n"
    #     f"### Context from your documents:\n{context}\n\n"
    #     f"### Question:\n{query} [/INST]"
    # )

    # Prompt for Phi
    prompt = (
        f"<|system|>\n{system}<|end|>\n"
        f"<|user|>\n"
        f"### Context from your documents:\n{context}\n\n"
        f"### Question:\n{query}<|end|>\n"
        f"<|assistant|>\n"
    )
    return prompt
```

Two key decisions here:

1. **Mistral `[INST]` format** — every model family has its own instruction format.
   Using the wrong format produces poor answers. Mistral uses `<s>[INST]...[/INST]`.

2. **"Only use the context" instruction** — explicitly anchoring the model to
   retrieved documents reduces hallucination significantly.


### Inference

```python
response = llm(
    prompt,
    max_tokens=512,
    temperature=TEMPERATURE,
    stop=["</s>", "[INST]"],    # prevent runaway generation
    echo=False,
)
```

`stop=["</s>", "[INST]"]` tells llama.cpp to halt generation at Mistral's
end-of-sequence token or if it starts generating a new instruction block —
preventing the model from hallucinating a second question-answer pair.

### Streaming

```python
def ask_stream(...) -> Generator:
    stream = llm(prompt, ..., stream=True)

    for token in stream:
        text = token["choices"][0]["text"]
        yield text

    # Yield metadata after streaming completes
    yield {"sources": get_sources(chunks)}
    yield {"chunks": chunks}
```

`ask_stream()` yields text tokens one at a time for real-time display in the UI.
After the token stream ends, it yields metadata dicts so the UI can display
source references without a second network call.


## `src/ui/app.py` — Streamlit Interface

### Model Caching

```python
@st.cache_resource(show_spinner="Loading LLM...")
def get_llm():
    return load_llm()
```

`@st.cache_resource` loads the LLM once and reuses it across all reruns.
Without this, the 4GB model would reload on every user interaction.

### Streaming Display

```python
for token in ask_stream(query, llm, embedding_model):
    if isinstance(token, dict):
        if "sources" in token:
            sources = token["sources"]
    else:
        full_response += token
        response_placeholder.markdown(full_response + "▌")  # typing cursor

response_placeholder.markdown(full_response)  # final render without cursor
```

The `▌` cursor appended during streaming gives a natural typing effect.
It's removed on the final render once the stream completes.

