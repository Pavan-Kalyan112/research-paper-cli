import requests

def summarize_abstract(text: str) -> str:
    """
    Summarize the given research abstract using a local LLM API (Ollama).

    Args:
        text (str): The abstract text to summarize.

    Returns:
        str: A simplified summary or error message.
    """
    # Handle empty or None input gracefully
    if not text or not text.strip():
        return "No abstract provided for summarization."

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": f"Summarize this research paper abstract in simple terms:\n\n{text}",
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "LLM returned no summary.")
    except Exception as e:
        return f"⚠️ LLM summarization failed: {str(e)}"
