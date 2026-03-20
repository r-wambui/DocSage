"""
Streamlit UI for DocSage

"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import SUPPORTED_EXTENSIONS
from src.ingestor import load_embedding_model, ingest_folder
from src.rag_engine import load_llm

# Configure page

st.set_page_config(page_title="DocSage: Chat with your files",
                    page_icon="file_folder",
                    layout="wide")


# Persist values using state across multiple reruns withing the same session
# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if the folder has been ingested
if "ingested" not in st.session_state:
    st.session_state.ingested = False

#Check selected folder path 
if "selected_folder" not in st.session_state:
    st.session_state.selected_folder = "" 

# Check the ingested folder
if "ingested_folder" not in st.session_state:
    st.session_state.ingested_folder = "" 

# Check if the llm model is loaded
if "llm" not in st.session_state:
    st.session_state.llm = None

# Check if the embedding model is loaded
if "embedding_model" not in st.session_state:
    st.session_state.embedding_model = None 


# Model Loading and cache it
@st.cache_resource(show_spinner="Loading embedding model...")
def get_embedding_model():
    return load_embedding_model()


@st.cache_resource(show_spinner="Loading LLM (this may take a moment)...")
def get_llm():
    return load_llm()


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/documents.png", width=60)
    st.title("DocSage")
    st.caption("Chat with your local files — privately.")
    st.divider()
 
    # Select folder
    st.subheader("📁 Document Folder")
    st.caption(
        f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}\n"
        "Subfolders are scanned recursively."
    )

    # Browse folder on laptop
    if st.button("📂 Browse Folder", use_container_width=True):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes("-topmost", True)  # dialog appears on top
    
            selected = tk.filedialog.askdirectory(
                    title="Select your documents folder",
                    parent=root,
                )
            root.destroy()

            if selected:
                st.session_state.selected_folder = selected

        except ImportError:
            st.info(
            "💡 Folder picker unavailable on this system.\n"
            "Paste your folder path manually below."
        )

    folder_path = st.text_input(
        label="Folder path",
        value=st.session_state.selected_folder,
        placeholder="Or paste path manually: Users/Sample_docs/",
        help="Use the Browse button or paste a folder path manually.",
        label_visibility="collapsed",
    )


    # Ingest folder

    ingest_btn = st.button(
        "⚡ Ingest Documents",
        use_container_width=True,
        type="primary",
        disabled=not folder_path,
    )

    if ingest_btn and folder_path:
        folder = Path(folder_path.strip())

        if not folder.exists():
            st.error(f"Folder not found:\n`{folder_path}`")
        elif not folder.is_dir():
            st.error("That path is a file, not a folder.")

        else:
            try:
                embedding_model = get_embedding_model()

                with st.spinner("Scanning and ingesting documents..."):
                    total = ingest_folder(str(folder), embedding_model)
                
                st.session_state.ingested = True
                st.session_state.ingested_folder = str(folder)
                st.session_state.messages = []
                st.success(f"✅ {total} chunks ingested successfully!")

            except Exception as e:
                st.error(f"Ingestion failed:\n{e}")

    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
 
    st.divider()
    st.caption("🔒 100% local — no data leaves your machine.")
    st.caption("Powered by llama.cpp + ChromaDB")

 


        
 
 




