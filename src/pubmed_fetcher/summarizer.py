# src/pubmed_fetcher/summarizer.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
LLM_MODEL = os.getenv("LLM_MODEL_NAME", "llama3")
LLM_URL = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")

def summarize_abstract(text: str) -> str:
    """
    Summarizes the given abstract using Ollama, or fallback to a shorter version if unavailable.
    """
    if not USE_LLM:
        return _fallback_summary(text)

    payload = {
        "model": LLM_MODEL,
        "prompt": f"Summarize this abstract in simple language:\n{text}",
        "stream": False
    }

    try:
        response = requests.post(LLM_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "⚠️ No summary returned.")
    except requests.exceptions.RequestException as e:
        return f"⚠️ LLM summarization failed: {e}"

def _fallback_summary(text: str) -> str:
    return text[:300] + "..." if len(text) > 300 else text
