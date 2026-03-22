
# Setup & Installation

DocSage runs on any modern Windows, macOS, or Linux machine.
You do not need a GPU — CPU inference works fine.

## System Requirements

- **Python:** 3.10 or higher
- **RAM:** Minimum 8GB (16GB recommended for smoother performance)  
  > Note: On machines with 8GB RAM, using the Phi model will be faster
- **Disk space:** ~4GB for the model
- **CPU:** Works on CPU (no GPU required)


## 1. Clone the repo
```bash
git clone https://github.com/r-wambui/DocSage.git
cd DocSage
```


## 2. Create and activate virtual environment

Always use a virtual environment to keep DocSage's dependencies isolated.

```bash
python -m venv venv

# Activate it
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```


## 3. Install dependencies
```bash
pip install -r requirements.txt
```

>  **Windows users**:- if `llama-cpp-python` fails to build, install the C++ Build Tools.  
> This is the proper long-term fix for Windows Python development in general:
> 
> - Download **Visual Studio Build Tools** from [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
> - Run the installer and select the **Desktop development with C++** workload
> - Restart your terminal and retry the `pip install -r requirements.txt` command


## 4. Download the model

> Download Mistral 7B Instruct (Q4_K_M quantization, ~4GB)

```bash
mkdir models

# Download the model (MacOs / Linux)
curl -L "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf" \
     -o models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path models
Invoke-WebRequest -Uri "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf" `
  -OutFile "models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
```

Alternatively, download it manually from [HuggingFace](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF)
and place it in the `models/` folder.

### Why this model?

`Q4_K_M` is a 4-bit quantized version of Mistral 7B. Quantization reduces the model
from ~14GB (full precision) to ~4GB by representing weights with lower precision.


## 5. Configure environment
Create a `.env` file in the project root with the following variables:

```env

```

## 6. Run DocSage
```bash
streamlit run src/ui/app.py
```
Open http://localhost:8501 in your browser, paste/browse your documents folder path, and start chatting.

## Step 7 — Ingest Your Documents

1. Click **Browse Folder** in the sidebar
2. Select the folder containing your documents
3. Click **Ingest Documents**
4. Wait for the ingestion to complete (progress shown in terminal)
5. Start asking questions

:::tip First run takes longer
The first time you ingest, the embedding model (`nomic-embed-text-v1`) downloads
from HuggingFace (~270MB) and is cached locally. Subsequent runs are instant.
:::

## Testing 

Run the test scripts in order to verify each component works:



## Troubleshooting

| Error | Fix |
|-------|-----|
| `Model file not found` | Check `MODEL_PATH` in `.env` matches your file location |
| `No module named einops` | Run `pip install einops` |
| `Vector store is empty` | Ingest a folder first before asking questions |
| CMake error on Windows | (see Step 3) |

