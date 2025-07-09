import os
import json
import requests
from dotenv import load_dotenv
from rich.console import Console

# Load .env variables
load_dotenv()

console = Console()

# Environment-based configuration
LLM_MODEL = os.getenv("LLM_MODEL_NAME", "mistral")
LLM_CHAT_URL = os.getenv("LLM_CHAT_URL", "http://localhost:11434/api/chat")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"
SUMMARY_FILE = "summarized_results.json"

def load_summaries():
    """
    Load summaries from the summary file.
    """
    if not os.path.exists(SUMMARY_FILE):
        console.print(f"[yellow]⚠️ Summary file not found: {SUMMARY_FILE}[/yellow]")
        return []
    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Failed to load summaries: {e}[/red]")
        return []

def chat_with_llm(prompt: str) -> str:
    try:
        response = requests.post(
        LLM_CHAT_URL,
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful research assistant."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        },
        timeout=60
    )

        response.raise_for_status()
        print("🔧 RAW RESPONSE:", response.text)  # Add this line
        data = response.json()
        return data.get("message", {}).get("content") or data.get("response", "⚠️ LLM returned no content.")
    except requests.exceptions.RequestException as req_err:
        return f"⚠️ Network error while calling LLM: {req_err}"
    except Exception as e:
        return f"❌ LLM Error: {e}"


def chat_with_retry(prompt: str) -> str:
    """
    Retry mechanism for LLM queries (3 attempts max).
    """
    for attempt in range(3):
        result = chat_with_llm(prompt)
        if not result.startswith("❌") and not result.startswith("⚠️"):
            return result
    return "❌ LLM failed to respond after 3 attempts."

def interactive_llm_chat():
    """
    Launch an interactive CLI chat session with the LLM.
    """
    if not USE_LLM:
        console.print("[red]LLM chat is disabled via environment config.[/red]")
        return

    papers = load_summaries()
    if not papers:
        console.print("[red]❌ No paper data found. Please run the CLI tool with --llm flag first.[/red]")
        return

    console.print("\n[bold green]💬 Interactive Chat with LLM (type 'exit' to quit):[/bold green]")

    while True:
        try:
            user_input = input("🧑‍💻 > ").strip()
            if user_input.lower() in {"exit", "quit"}:
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

# ✅ Exported for external use
__all__ = ["interactive_llm_chat", "chat_with_llm", "chat_with_retry"]

if __name__ == "__main__":
    interactive_llm_chat()
