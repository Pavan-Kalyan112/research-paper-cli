# src/pubmed_fetcher/summary.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment or defaults
LLM_CHAT_URL = os.getenv("LLM_CHAT_URL", "http://localhost:11434/api/generate")
LLM_MODEL = os.getenv("LLM_MODEL_NAME", "mistral")
USE_LLM = os.getenv("USE_LLM", "true").strip().lower() == "true"


def summarize_abstract(text: str) -> str:
    """
    Summarize the given research abstract using the local Ollama LLM.

    Args:
        text (str): Abstract to be summarized.

    Returns:
        str: Simplified summary or error message.
    """
    if not USE_LLM:
        return "⚠️ LLM summarization is disabled via USE_LLM=False."

    if not text or not text.strip():
        return "No abstract provided for summarization."

    try:
        response = requests.post(
            LLM_CHAT_URL,
            json={
                "model": LLM_MODEL,
                "prompt": f"Summarize this research paper abstract in simple terms:\n\n{text.strip()}",
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        summary = data.get("response", "").strip()
        return summary if summary else "⚠️ LLM returned no summary."

    except requests.exceptions.RequestException as req_err:
        return f"⚠️ Network error while calling LLM: {req_err}"

    except Exception as e:
        return f"⚠️ Unexpected error during LLM summarization: {e}"
