"""
Connects retrival to generation

This is how the whole process is:
    User_query:
        -> retrieves the relevant chunks
        -> build a prompt with context
        -> send to llama.cpp for generation
        -> returns generated answers and sources

"""
from typing import List, Dict, Generator

from llama_cpp import Llama
from sentence_transformers import SentenceTransformer

from src.config import  MODEL_PATH, N_CTX, TOP_K, TEMPERATURE
from src.retriever import retrieve, format_context, get_sources

import os
os.environ["GGML_METAL_NDEBUG"] = "1"

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


def ask(query: str, llm: Llama, embedding_model: SentenceTransformer, top_k: int = TOP_K) -> Dict:
    """
    Receives the user query and returns the generated answer
    
    """
    # Retrieve relevant chunks from ChromaDB
    chunks = retrieve(query, embedding_model, top_k=top_k)
 
    # Format chunks into a context string for the prompt
    context = format_context(chunks)
 
    # Build the full prompt
    prompt = build_prompt(query, context)

    # Generates the answer
    print("[DocSage] Generating answer...")
    response = llm(
        prompt,
        max_tokens=512,     # max length of the geneated answer, you can increase it
        temperature=TEMPERATURE,
        stop=["</s>", "[INST]"], 
        echo=False,
    )

    answer = response["choices"][0]["text"].strip()

    return {
        "answer": answer,
        "sources": get_sources(chunks),
        "chunks": chunks,

    }


def ask_stream(query: str, llm: Llama, embedding_model: SentenceTransformer, top_k: int = TOP_K,) -> Generator:
    """
    Streaming version of ask(), Yield token one by one as they are generated,
    Helpful in the UI instead of waiting for whole response

    """

    # Retrieve relevant chunks from ChromaDB
    chunks = retrieve(query, embedding_model, top_k=top_k)
 
    # Format chunks into a context string for the prompt
    context = format_context(chunks)
 
    # Build the full prompt
    prompt = build_prompt(query, context)

    # Stream response
    response = llm(
        prompt,
        max_tokens=512,
        temperature=TEMPERATURE,
        stop=["</s>", "[INST]"],
        echo=False,
        stream=True,
    )

    for token in response:
        text = token["choices"][0]["text"]
        yield text

    yield {"sources": get_sources(chunks)}
    yield {"chunks": chunks}
 



