import os
import json
import requests
from dotenv import load_dotenv
from rich.console import Console

# Load environment variables
load_dotenv()

# Console for rich output
console = Console()

# Configuration from .env
LLM_MODEL = os.getenv("LLM_MODEL_NAME", "mistral")
LLM_CHAT_URL = os.getenv("LLM_CHAT_URL", "http://localhost:11434/api/chat")
USE_LLM = os.getenv("USE_LLM", "true").strip().lower() == "true"
DEBUG = os.getenv("DEBUG", "false").strip().lower() == "true"
SUMMARY_FILE = "summarized_results.json"

# === Utility ===
def log_debug(message: str) -> None:
    if DEBUG:
        console.print(f"[grey]{message}[/grey]")

# === Summary Loader ===
def load_summaries():
    if not os.path.exists(SUMMARY_FILE):
        console.print(f"[yellow]⚠️ Summary file not found: {SUMMARY_FILE}[/yellow]")
        return []

    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Failed to load summaries: {e}[/red]")
        return []

# === LLM Chat Call ===
def chat_with_llm(prompt: str) -> str:
    if not USE_LLM:
        return "🔇 LLM chat is disabled (USE_LLM=False)."

    if not prompt.strip():
        return "⚠️ Empty prompt."

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": prompt.strip()}
        ],
        "stream": False
    }

    try:
        log_debug(f"🔧 Sending chat request to {LLM_CHAT_URL} with model '{LLM_MODEL}'...")
        response = requests.post(LLM_CHAT_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        raw_output = result.get("message", {}).get("content") or result.get("response", "")
        log_debug(f"📥 RAW RESPONSE: {raw_output}")
        return raw_output.strip() or "⚠️ LLM returned no content."

    except requests.exceptions.RequestException as req_err:
        return f"⚠️ Network error while calling LLM: {req_err}"
    except Exception as e:
        return f"❌ LLM Error: {e}"

# === Retry Wrapper ===
def chat_with_retry(prompt: str, max_retries: int = 3) -> str:
    for attempt in range(1, max_retries + 1):
        result = chat_with_llm(prompt)
        if not result.startswith("❌") and not result.startswith("⚠️"):
            return result
        console.print(f"[yellow]⚠️ Retrying... ({attempt}/{max_retries})[/yellow]")
    return "❌ LLM failed to respond after multiple attempts."

# === Interactive CLI ===
def interactive_llm_chat():
    if not USE_LLM:
        console.print("[red]LLM chat is disabled via environment config.[/red]")
        return

    papers = load_summaries()
    if not papers:
        console.print("[red]❌ No paper data found. Please run the CLI with --llm flag first.[/red]")
        return

    console.print("\n[bold green]💬 Interactive Chat with LLM (type 'exit', 'logout', or 'quit' to leave)[/bold green]")

    while True:
        try:
            user_input = input("🧑‍💻 > ").strip()
            if user_input.lower() in {"exit", "quit", "logout"}:
                console.print("[cyan]👋 Exiting LLM chat session.[/cyan]")
                break
            if not user_input:
                continue

            paper_context = user_input

            if "paper" in user_input.lower():
                paper_num = ''.join(filter(str.isdigit, user_input))
                if paper_num.isdigit():
                    idx = int(paper_num) - 1
                    if 0 <= idx < len(papers):
                        paper = papers[idx]
                        paper_context = (
                            f"Here is the metadata for Paper {paper_num}:\n\n"
                            f"PubMed ID: {paper.get('PubmedID', 'N/A')}\n"
                            f"Title: {paper.get('Title', 'N/A')}\n"
                            f"Authors: {paper.get('Authors', 'N/A')}\n"
                            f"Abstract: {paper.get('Abstract', 'N/A')}\n"
                            f"Company Affiliations: {paper.get('CompanyAffiliation(s)', 'N/A')}\n"
                            f"Non-Academic Authors: {paper.get('Non-academicAuthor(s)', 'N/A')}\n"
                            f"Corresponding Email: {paper.get('Corresponding Author Email', 'N/A')}\n"
                            f"Summary: {paper.get('summary', 'No summary available.')}\n\n"
                            f"User question: {user_input}"
                        )
                    else:
                        paper_context = f"❌ Invalid paper number. Only {len(papers)} papers available."
                else:
                    paper_context = "⚠️ Please specify a valid paper number like 'explain paper 2'."

            response = chat_with_retry(paper_context)
            console.print(f"\n🤖 [bold magenta]LLM:[/bold magenta] {response.strip()}\n")

        except KeyboardInterrupt:
            console.print("\n[cyan]👋 Interrupted. Exiting LLM chat.[/cyan]")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")

# === Exports ===
__all__ = ["interactive_llm_chat", "chat_with_llm", "chat_with_retry"]

if __name__ == "__main__":
    interactive_llm_chat()
