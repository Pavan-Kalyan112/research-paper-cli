# src/pubmed_fetcher/chat.py

import os
import requests
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()

LLM_MODEL = os.getenv("LLM_MODEL_NAME", "ollama3")
LLM_CHAT_URL = os.getenv("LLM_CHAT_URL", "http://localhost:11434/api/chat")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"

def interactive_llm_chat():
    """
    Starts an interactive CLI session to chat with the LLM.
    """
    if not USE_LLM:
        console.print("[red]LLM chat is disabled via environment configuration.[/red]")
        return

    console.print("\n[bold green]🧠 Ask more questions to the LLM (type 'exit' to quit):[/bold green]")

    while True:
        try:
            user_input = input("🧑‍💻 > ").strip()
            if user_input.lower() in {"exit", "quit"}:
                console.print("[cyan]👋 Exiting LLM chat session.[/cyan]")
                break
            if not user_input:
                continue

            response = requests.post(
                LLM_CHAT_URL,
                json={
                    "model": LLM_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful research assistant."},
                        {"role": "user", "content": user_input}
                    ]
                },
                timeout=30
            )

            if response.status_code == 404:
                console.print("[red]❌ LLM Chat error: Model or endpoint not found. Is Ollama running?[/red]")
                break

            response.raise_for_status()
            result = response.json()

            # Handle both Ollama's streaming & non-streaming formats
            message = result.get("message", {}).get("content") or result.get("response")
            if message:
                console.print(f"🤖 LLM: {message.strip()}\n")
            else:
                console.print("[yellow]⚠️ No content received from LLM.[/yellow]")

        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ LLM Chat error: {e}[/red]")
        except KeyboardInterrupt:
            console.print("\n[cyan]👋 Interrupted. Exiting LLM chat.[/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
