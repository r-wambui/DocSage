<h1>
  <img src="https://img.icons8.com/fluency/96/documents.png" width="32" style="vertical-align: middle;" />
  DocSage
</h1>

> Chat with your local documents privately and securely. No data leaving your local machine.

DocSage is a local app that let's users chat and ask questions about their own files (PDFs, Markdown, text) locally. Its powered by RAGs and llama.cpp to run LLMs locally

## How it works
```
Your documents  in a folder
        → Scanned & chunked  
        → Embedded (nomic-embed-text-v1)  
        → Stored in ChromaDB (local vector store)  
        → Query comes in  
        → Top-k chunks retrieved  
        → Prompt built with context  
        → llama.cpp generates answer  
        → Answer + sources shown in UI
```

## Stack

| Layer         | Tool                              | Why                                                                 |
|---------------|-----------------------------------|----------------------------------------------------------------------|
| Inference     | `llama-cpp-python`                | Direct llama.cpp bindings; runs in-process with no server required  |
| LLM Model     | `mistral-7b-instruct-v0.2.Q4_K_M` | 4-bit quantized (~4GB RAM); runs on most modern laptops             |
| Embeddings    | `nomic-embed-text-v1`             | Optimized for retrieval; strong semantic search performance         |
| Vector Store  | `ChromaDB`                        | Lightweight, in-process, persists to disk                           |
| UI            | `Streamlit`                       | Python-native; fast for building dev-facing interfaces              |

> **Note**  
> Uses `mistral-7b-instruct` by default. On lower-spec machines (e.g. Intel Macs - 8GB, 1.4ghz), a smaller `Phi-3-mini-4k-instruct-q4.gguf` is used for smoother performance.

## Quickstart 
> How to set it up on your local machine


### 1. Clone the repo
```bash
git clone https://github.com/r-wambui/DocSage.git
cd DocSage
```


### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```


### 3. Install dependencies
```bash
pip install -r requirements.txt
```

>  **Windows users**:- if `llama-cpp-python` fails to build, install the C++ Build Tools.  
> This is the proper long-term fix for Windows Python development in general:
> 
> - Download **Visual Studio Build Tools** from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
> - Run the installer and select the **Desktop development with C++** workload
> - Restart your terminal and retry the `pip install -r requirements.txt` command


### 4. Download the model
> Download Mistral 7B Instruct (Q4_K_M quantization, ~4GB)
```bash
mkdir models
curl -L "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf" \
     -o models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 5. Create the vectorstore folder
ChromaDB persists your document embeddings here between sessions — 
so you only need to ingest your documents once.

```bash
mkdir vectorstore
```

### 6. Configure environment
Create a `.env` file in the project root with the following variables:.You can change the values depending on what settings and model you want to use

```env
MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
CHROMA_PERSIST_DIR=./vectorstore
EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1
CHUNK_SIZE=512
CHUNK_OVERLAP=64
TOP_K=4
N_CTX=4096
TEMPERATURE=0.2
```

### 7. Run DocSage
```bash
streamlit run src/ui/main.py
```
Open http://localhost:8501 in your browser, paste/browse your documents folder path, and start chatting.

## System Requirements

- **Python:** 3.10 or higher
- **RAM:** Minimum 8GB (16GB recommended for smoother performance)  
  > Note: On machines with 8GB RAM, using the Phi model will be faster
- **Disk space:** ~4GB for the model
- **CPU:** Works on CPU (no GPU required)
