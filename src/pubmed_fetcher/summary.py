import os
import requests
from dotenv import load_dotenv
from rich.console import Console

# === Setup ===
load_dotenv()
console = Console()

# === Configuration ===
LLM_CHAT_URL: str = os.getenv("LLM_CHAT_URL", "http://localhost:11434/api/generate")
LLM_MODEL: str = os.getenv("LLM_MODEL_NAME", "mistral")
USE_LLM: bool = os.getenv("USE_LLM", "true").strip().lower() == "true"

def summarize_abstract(text: str) -> str:
    """
    Summarizes a research abstract using a local LLM via an HTTP API.

    Args:
        text (str): The abstract to summarize.

    Returns:
        str: A simplified summary or an error message.
    """
    if not USE_LLM:
        return "⚠️ LLM summarization is disabled (set USE_LLM=true in .env)"

    if not text or not text.strip():
        return "⚠️ No abstract provided for summarization."

    payload = {
        "model": LLM_MODEL,
        "prompt": (
            "Summarize the following scientific research abstract in simple, clear terms:\n\n"
            f"{text.strip()}"
        ),
        "stream": False
    }

    try:
        response = requests.post(LLM_CHAT_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        summary = data.get("response", "").strip()
        return summary if summary else "⚠️ LLM returned an empty summary."

    except requests.exceptions.RequestException as e:
        return f"⚠️ Network error while calling LLM: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error during LLM summarization: {e}"

def main():
    """
    Allows testing summarization interactively from the terminal.
    """
    console.print("[bold blue]🔬 Local Abstract Summarizer using Ollama LLM[/bold blue]\n")

    while True:
        try:
            example_abstract = input("📜 Paste an abstract to summarize (or type 'exit' to quit):\n\n").strip()
            if example_abstract.lower() in {"exit", "quit"}:
                console.print("[cyan]👋 Exiting test mode.[/cyan]")
                break

            console.print("\n⏳ [italic]Generating summary...[/italic]\n")
            result = summarize_abstract(example_abstract)

            console.print("\n✅ [bold green]Summary:[/bold green]\n")
            console.print(result + "\n")

        except KeyboardInterrupt:
            console.print("\n[cyan]👋 Interrupted. Exiting summarizer test.[/cyan]")
            break

if __name__ == "__main__":
    main()
