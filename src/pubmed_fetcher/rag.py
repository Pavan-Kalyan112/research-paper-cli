import os
import json
import numpy as np
import faiss
from dotenv import load_dotenv
from rich.console import Console
from sklearn.metrics.pairwise import cosine_similarity

from pubmed_fetcher.chat import chat_with_retry
from pubmed_fetcher.data_pipeline import search_and_fetch
from pubmed_fetcher.llm import summarize_with_llm
from pubmed_fetcher.embedder import (
    get_embedding_model,
    embed_texts,
    embed_papers,
    build_faiss_index,
)

# === Setup ===
load_dotenv()
console = Console()
TOP_K = 3


def retrieve_top_k(query: str, index, embeddings, metadata: list[dict], model, top_k: int = TOP_K) -> list[dict]:
    """Return top-k most relevant papers using FAISS or fallback cosine similarity."""
    query_vec = embed_texts([query], model)
    if query_vec.size == 0:
        return []

    try:
        distances, indices = index.search(query_vec, top_k)
        return [metadata[i] for i in indices[0] if i < len(metadata)]
    except Exception:
        cosims = cosine_similarity(query_vec, embeddings)[0]
        top_indices = np.argsort(cosims)[-top_k:][::-1]
        return [metadata[i] for i in top_indices]


def generate_answer_with_context(query: str, papers: list[dict]) -> str:
    """Generate an LLM-based answer from retrieved papers and user query."""
    if not papers:
        return "❌ No relevant papers found for your question."

    context = "\n\n".join([
        f"Paper {i+1}:\n"
        f"PubMed ID: {p.get('PubmedID', 'N/A')}\n"
        f"Title: {p.get('Title', 'N/A')}\n"
        f"Authors: {p.get('Authors', 'N/A')}\n"
        f"Abstract: {p.get('Abstract', 'N/A')}\n"
        f"Summary: {p.get('summary', p.get('Summary', 'N/A'))}"
        for i, p in enumerate(papers)
    ])

    prompt = (
        f"User question: {query}\n\n"
        f"Research papers related to this question:\n\n{context}\n\n"
        f"Based on this, provide a clear, helpful answer."
    )

    return chat_with_retry(prompt)


def print_paper_summaries(papers: list[dict]):
    """Print a readable summary of all papers to the console."""
    console.print(f"\n📚 [bold]Top {len(papers)} Relevant Papers:[/bold]")
    for i, p in enumerate(papers, 1):
        summary = str(p.get('summary', p.get('Summary', 'N/A')))
        console.print(
            f"\n[bold cyan]Paper {i}[/bold cyan]\n"
            f"[bold]Title:[/bold] {p.get('Title', 'N/A')}\n"
            f"[bold]PubMed ID:[/bold] {p.get('PubmedID', 'N/A')}\n"
            f"[bold]Authors:[/bold] {p.get('Authors', 'N/A')}\n"
            f"[bold]Summary:[/bold] {summary[:2000]}...\n"
        )


def fetch_and_embed_index(query: str):
    """Fetch papers and build an embedding index for the query."""
    console.print(f"🔎 Searching PubMed for: [italic]{query}[/italic]")
    papers = search_and_fetch(query, limit=5)

    if not papers:
        console.print("[red]❌ No papers found.[/red]")
        return None, None, None, []

    for paper in papers:
        abstract = paper.get("Abstract", "")
        paper["summary"] = summarize_with_llm(abstract) if abstract else "No abstract to summarize."

    model = get_embedding_model()
    embeddings, metadata = embed_papers(papers, model=model)
    index = build_faiss_index(embeddings)

    return index, embeddings, model, metadata


def start_conversational_loop(papers: list[dict]):
    """Start the interactive RAG-based chat loop."""
    while True:
        try:
            follow_up = input("\n💬 Ask about a specific paper (e.g., 'Summarize paper 2') or type 'exit' to finish: ").strip()
        except EOFError:
            console.print("\n[cyan]👋 EOF received. Ending session.[/cyan]")
            break

        if follow_up.lower() in {"exit", "quit"}:
            console.print("[cyan]👋 Ending follow-up session.[/cyan]")
            break

        context = "\n\n".join([
            f"Paper {i+1}:\n"
            f"PubMed ID: {p.get('PubmedID', 'N/A')}\n"
            f"Title: {p.get('Title', 'N/A')}\n"
            f"Authors: {p.get('Authors', 'N/A')}\n"
            f"Abstract: {p.get('Abstract', 'N/A')}\n"
            f"Summary: {p.get('summary', p.get('Summary', 'N/A'))}"
            for i, p in enumerate(papers)
        ])

        prompt = (
            f"The user asked: {follow_up}\n\n"
            f"Here are the research papers:\n\n{context}\n\n"
            f"Answer the user's question based on this data."
        )

        response = chat_with_retry(prompt)
        console.print(f"\n🤖 [bold magenta]LLM:[/bold magenta] {response.strip()}\n")


def main(json_path: str = None, query: str = None, debug: bool = False):
    """Main RAG entry point: takes a query or JSON file of papers."""
    console.print("[bold blue]\n🔍 Welcome to the RAG-powered Research Assistant[/bold blue]")

    if json_path:
        if not os.path.exists(json_path):
            console.print(f"[red]❌ File not found:[/red] {json_path}")
            return

        with open(json_path, "r", encoding="utf-8") as f:
            papers = json.load(f)
        console.print(f"[green]✅ Loaded {len(papers)} papers from:[/green] {json_path}")

    elif query:
        index, embeddings, model, metadata = fetch_and_embed_index(query)
        if not metadata:
            console.print(f"[yellow]⚠️ No relevant papers found for: {query}[/yellow]")
            return
        papers = retrieve_top_k(query, index, embeddings, metadata, model)

    else:
        console.print(
            "[red]❌ Please provide a query (--query) or a JSON file (--use-file).[/red]\n"
            "[blue]💡 Example: poetry run pubmed-fetcher --query 'diabetes treatment' --rag --llm[/blue]"
        )
        return

    print_paper_summaries(papers)
    answer = generate_answer_with_context(query or "general research", papers)
    console.print(f"\n🤖 [bold green]LLM Answer:[/bold green] {answer.strip()}\n")

    start_conversational_loop(papers)


if __name__ == "__main__":
    main()
