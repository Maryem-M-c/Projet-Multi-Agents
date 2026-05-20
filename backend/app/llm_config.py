# backend/app/llm_config.py
import os
import locale
locale.setlocale(locale.LC_ALL, '')

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

def get_llm(temperature: float = 0):
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "tinyllama"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
        num_ctx=512,
        num_predict=256,
    )