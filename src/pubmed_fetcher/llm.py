import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"

def summarize_with_llm(prompt: str) -> str:
    """
    Sends a summarization prompt to the Ollama LLM and returns the response.
    """
    if not USE_LLM:
        return "LLM summarization is disabled via USE_LLM=False."

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": f"Summarize this abstract in simple terms:\n\n{prompt}",
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json().get("response", "No summary generated.")
    except Exception as e:
        return f"LLM error: {e}"

def chat_with_llm(prompt: str, model: str = LLM_MODEL) -> str:
    """
    Sends a chat message to the Ollama LLM and returns the response.
    """
    if not USE_LLM:
        return "LLM chat is disabled via USE_LLM=False."

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful research assistant."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        return f"LLM Chat error: {e}"
