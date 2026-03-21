<h1>
  <img src="https://img.icons8.com/fluency/96/documents.png" width="32" style="vertical-align: middle;" />
  DocSage
</h1>

**Chat with your local documents privately and securely**

DDocSage is a local app that let's users chat and ask questions about their own files (PDFs, Markdown, text) locally. Its powered by RAGs and llama.cpp to run LLMs locally

## What Problem Does It Solve?

Most AI chat tools send your documents to a remote server for processing.
That's a problem when your files contain sensitive, private, or proprietary information.

DocSage solves this by running the entire pipeline — document loading, embedding, retrieval,
and LLM inference — on your own hardware. The only network activity is the one-time download
of the model and embedding weights. After that, it runs fully offline.

## Who Is This For?
- **Developers** who want to understand how RAG systems work under the hood
- **Teams** that handle sensitive documents and can't use cloud AI
- **Researchers** who want a private, local document Q&A tool
- **Anyone** curious about running local LLMs in a real application

## Key Features

- **Folder-based ingestion** - point DocSage at any folder and it processes all supported files recursively
- **Semantic search** - finds relevant content by meaning, not just keywords
- **Local LLM** - powered by `llama-cpp-python`, runs on CPU
- **Source references** - every answer shows exactly which documents it came from
- **Streaming responses** - answers appear word by word
- **100% private** - zero data transmission after initial model download

## Supported File Types

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Markdown | `.md` |
| Plain text | `.txt` |


## Tech Stack

| Layer         | Tool                              | Why                                                                 |
|---------------|-----------------------------------|----------------------------------------------------------------------|
| Inference     | `llama-cpp-python`                | Direct llama.cpp bindings; runs in-process with no server required  |
| LLM Model     | `mistral-7b-instruct-v0.2.Q4_K_M` | 4-bit quantized (~4GB RAM); runs on most modern laptops             |
| Embeddings    | `nomic-embed-text-v1`             | Optimized for retrieval; strong semantic search performance         |
| Vector Store  | `ChromaDB`                        | Lightweight, in-process, persists to disk                           |
| UI            | `Streamlit`                       | Python-native; fast for building dev-facing interfaces              |

> **Note**  
> Uses `mistral-7b-instruct` by default. On lower-spec machines (e.g. Intel Macs - 8GB, 1.4ghz), a smaller `Phi-3-mini-4k-instruct-q4.gguf` is used for smoother performance.

## How DocSage Leverages RAG
A plain LLM answers from its training data alone — it has never seen your documents.
RAG bridges that gap:

```
Without RAG:   User question → LLM (training data only) → answer
With RAG:      User question → retrieve from YOUR docs → LLM + context → grounded answer
```

In DocSage, the prompt is explicitly constrained to only use the retrieved document chunks.  
This ensures that:

- Answers are **accurate and grounded in your documents**
- The LLM cannot “hallucinate” information from outside sources
- Every answer is **traceable back to a specific source file**