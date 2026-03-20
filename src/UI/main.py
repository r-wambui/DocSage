"""
Streamlit UI for DocSage

"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestor import load_embedding_model
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



