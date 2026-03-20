"""
Connects retrival to generation

This is how the whole process is:
    User_query:
        -> retrieves the relevant chunks
        -> build a prompt with context
        -> send to llama.cpp for generation
        -> returns generated answers and sources

"""
from llama_cpp import Llama

from src.config import  MODEL_PATH, N_CTX

def load_llm() -> Llama:
    """
    Loads the GGUF model via llama-cpp-python.
    """

    print(f"[DocSage] Loading LLM from: {MODEL_PATH}")

    llm = Llama(
        model_path=str(MODEL_PATH),
        n_ctx=N_CTX,
        verbose=False,
    )

    print("[DocSage] LLM ready.\n")
    return llm

def build_prompt(query: str, context: str) -> str
