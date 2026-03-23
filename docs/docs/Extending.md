# How to Extend DocSage

DocSage is intentionally minimal — it covers the core RAG loop clearly and nothing more.
That's a feature, not a limitation.

The best way to learn how RAG systems work is to extend one. Each direction below introduces
a real engineering tradeoff worth understanding. They're ordered roughly by difficulty,
but feel free to start wherever your curiosity takes you.

For each extension, we tell you:
- **What problem it solves** — the real motivation
- **Why it's an interesting problem** — the engineering tradeoff
- **Where to start** — the exact file and function to open

---

## 1. Contextual Chunk Enrichment

**What problem it solves**

Generic chunking loses structural context. A chunk that reads *"- performs well above
1800m"* means nothing in isolation. Which crop? Which region? The retriever finds it,
the LLM receives it, and the answer suffers.

**Why it's an interesting problem**

This is the most impactful improvement you can make to a RAG system without changing
any models. Anthropic published research on this called Contextual Retrieval — the idea
is to programmatically prepend a context label to every chunk at ingestion time,
so each chunk is self-contained regardless of where it was cut.

The tradeoff is ingestion time and token cost - richer chunks take longer to embed
and consume more context window. How much context is enough without being wasteful?

**Where to start**

`src/ingestor.py → chunk_text()`

Try prepending metadata to each chunk before it gets embedded:
```python
def add_context(chunk: str, metadata: dict) -> str:
    parts = []
    if metadata.get("source"):
        parts.append(f"Source: {metadata['source']}")
    header = " | ".join(parts)
    return f"[{header}]\n{chunk}" if header else chunk
```

Then measure whether retrieval scores improve on the same queries.

---

## 2. Re-ranking

**What problem it solves**

Vector similarity is fast but imprecise. It finds chunks that are *related* to your query,
not necessarily the chunks that *best answer* it. A chunk about planting schedules
might score highly for "how do I prevent pests" simply because both mention the same crop.

**Why it's an interesting problem**

Re-ranking introduces a second model — a CrossEncoder — that scores each retrieved chunk
against the query more precisely. Unlike bi-encoders (which embed query and chunk separately),
a CrossEncoder sees both at once and can reason about their relationship.

The tradeoff is latency. You're now running a second model on every query. Is the quality
improvement worth the extra 200-500ms? That depends entirely on your use case.

**Where to start**

`src/retriever.py → retrieve()`

After the ChromaDB query, add:
```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

scores = reranker.predict([(query, chunk["text"]) for chunk in chunks])
chunks = [c for _, c in sorted(zip(scores, chunks), reverse=True)]
```

Compare answer quality before and after on the same set of questions.


## 3. Add a REST API

**What problem it solves**

Streamlit is great for a developer tool but it is not the right interface for every use case.
A REST API would let you connect DocSage to a mobile app, a CLI, a browser extension,
or any other frontend.

**Why it's an interesting problem**

Adding FastAPI reveals something important about the architecture — because all the logic
lives in `rag.py`, `ingestor.py` and `retriever.py`, the UI layer is completely decoupled.
You are not rewriting the RAG pipeline, you are just adding a new interface to it.
That is what good separation of concerns looks like in practice.

**Where to start**

Create `src/api/routes.py`:
```python
from fastapi import FastAPI
from pydantic import BaseModel
from src.rag import ask

app = FastAPI(title="DocSage API")

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_endpoint(request: QueryRequest):
    result = ask(request.question, llm, embedding_model)
    return {"answer": result["answer"], "sources": result["sources"]}
```

Notice how little code this takes — that is the payoff of the modular design.

---

## 4. Multi-format Document Support

**What problem it solves**

Real document collections are not just PDFs and markdown. Teams store knowledge in
Word documents, CSVs, PowerPoints, Notion exports, and HTML pages.

**Why it's an interesting problem**

Each format has its own extraction challenge. PDFs lose tables. Word documents
have nested styles. CSVs have no natural prose flow — each row needs context
from its column headers to be meaningful as a chunk. There is no universal solution.

**Where to start**

`src/ingestor.py → load_file()` and `src/config.py → SUPPORTED_EXTENSIONS`

Adding a format is two changes — register the extension and write a loader:
```python
# config.py
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

# ingestor.py
def _load_docx(file_path: Path) -> str:
    import docx
    doc = docx.Document(str(file_path))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
```

The interesting challenge is CSV — try loading one and see what the chunks look like.
How would you make each row meaningful without its column headers?

---

## 6. Evaluation — Does It Actually Work?

**What problem it solves**

How do you know if your changes improved things? Intuition is not enough.
Without evaluation you are flying blind — a change that feels better might
actually reduce accuracy on a different set of questions.

**Why it's an interesting problem**

RAG evaluation is an open research problem. The two main approaches are:

- **Human evaluation** — curate a set of question-answer pairs from your documents
  and manually score responses. Slow but reliable.
- **LLM-as-judge** — use another LLM to score whether the generated answer
  is faithful to the retrieved context. Fast but introduces its own biases.

Neither is perfect. Understanding the tradeoffs between them is one of the most
valuable things you can learn about production RAG systems.

**Where to start**

Create `tests/evaluate.py`. Start with 10 questions you can answer from `sample_docs/`
and manually score DocSage's answers on a 1-3 scale. Then make one change — swap the
model, add re-ranking, change chunk size — and score again. The delta tells you
whether the change actually helped.
