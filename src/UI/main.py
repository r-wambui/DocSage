"""
Streamlit UI for DocSage

"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import SUPPORTED_EXTENSIONS
from src.ingestor import load_embedding_model, ingest_folder
from src.rag_engine import load_llm, ask_stream

# Configure page

st.set_page_config(page_title="DocSage",
                    page_icon="https://img.icons8.com/fluency/96/documents.png",
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
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <img src="https://img.icons8.com/fluency/96/documents.png" width="28">
            <h2 style="margin: 0; font-size: 1.4rem;">DocSage</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()
 
    # Select folder
    st.markdown("### 📁 Documents")
    st.caption(
        f"Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}\n"
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
        placeholder="e.g. Users/docs/",
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
                st.success(f"{total} chunks ingested successfully!")

            except Exception as e:
                st.error(f"Ingestion failed:\n{e}")

    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
 
    st.divider()
    st.caption("🔒 100% local — no data leaves your machine.")

# Design the chat area
# st.title(" DocSage")
st.subheader("Chat with your local files privately")

if not st.session_state.ingested:
    st.info(
        "**Get started** — paste your documents folder path in the sidebar "
        "and click **Ingest Documents**."
    )
    st.stop()   # don't render the chat UI until docs are ingested


# Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    if message["role"] == "assistant" and message.get("sources"):
        with st.expander("📄 Sources referenced", expanded=False):
            for source in message["sources"]:
                st.markdown(f"- `{source}`")

        if message.get("chunks"):
            st.divider()
            st.caption("Retrieval details:")
            for chunk in message["chunks"]:
                st.caption(
                    f"`{chunk['source']}` — chunk {chunk['chunk_index']} "
                    f"— similarity: {chunk['score']}"
                    )


# Chat input
query = st.chat_input("Ask a question about your documents...")

if query:
    embedding_model = get_embedding_model()
    llm = get_llm()

    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append({
        "role": "user",
        "content": query,
    })


    # fetch ask_stream to stream the response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        status_placeholder = st.empty()
        status_placeholder.markdown("*Searching your documents...*")


        full_response = ""
        sources = []
        chunks = []
        first_token = True

        for token in ask_stream(query, llm, embedding_model):
            if isinstance(token, dict):
                if "sources" in token:
                    sources = token["sources"]
                if "chunks" in token:
                    chunks = token["chunks"]
            else:
                if first_token:
                    status_placeholder.empty()  # ← clears "thinking" once tokens start
                    first_token = False
                full_response += token
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

        if sources:
            with st.expander("📄 Sources referenced", expanded=True):
                for source in sources:
                    st.markdown(f"- `{source}`")

                    if chunks:
                        st.divider()
                        st.caption("Retrieval details:")
                        for chunk in chunks:
                            st.caption(
                                f"`{chunk['source']}` — chunk {chunk['chunk_index']} "
                                f"— similarity: {chunk['score']}"
                            )

    # save the messages for chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "sources": sources,
        "chunks": chunks,
    })

