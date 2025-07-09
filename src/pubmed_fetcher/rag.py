import os
import json
import numpy as np
import faiss
from rich.console import Console
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from pubmed_fetcher.chat import chat_with_retry
from pubmed_fetcher.data_pipeline import search_and_fetch
from pubmed_fetcher.llm import summarize_with_llm

# Load environment variables
load_dotenv()

# Setup
console = Console()
EMBEDDING_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K = 3


def embed_texts(texts, model):
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings).astype("float32")


def build_faiss_index(papers, model):
    texts = [paper.get("Abstract", "") or paper.get("Title", "") for paper in papers]
    embeddings = embed_texts(texts, model)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, embeddings, papers


def retrieve_top_k(query, index, metadata, model, top_k=TOP_K):
    query_vector = model.encode([query], normalize_embeddings=True).astype("float32")
    distances, indices = index.search(query_vector, top_k)
    return [metadata[i] for i in indices[0] if i < len(metadata)]


def generate_answer_with_context(query: str, papers: list):
    if not papers:
        return "❌ No relevant papers found for your question."

    context = "\n\n".join([
        f"Paper {i+1}:\n"
        f"PubMed ID: {p.get('PubmedID')}\n"
        f"Title: {p['Title']}\n"
        f"Authors: {p.get('Authors', 'N/A')}\n"
        f"Abstract: {p.get('Abstract', 'N/A')}\n"
        f"Summary: {p.get('Summary', 'N/A')}"
        for i, p in enumerate(papers)
    ])

    prompt = (
        f"User question: {query}\n\n"
        f"Research papers related to this question:\n\n{context}\n\n"
        f"Based on this, provide a clear, helpful answer."
    )
    return chat_with_retry(prompt)


def print_paper_summaries(papers: list):
    console.print(f"\n📚 [bold]Top {len(papers)} Relevant Papers:[/bold]")
    for i, p in enumerate(papers, 1):
        console.print(
            f"\n[bold cyan]Paper {i}[/bold cyan]\n"
            f"[bold]Title:[/bold] {p['Title']}\n"
            f"[bold]PubMed ID:[/bold] {p['PubmedID']}\n"
            f"[bold]Authors:[/bold] {p.get('Authors', 'N/A')}\n"
            f"[bold]Summary:[/bold] {p.get('Summary', 'N/A')[:250]}...\n"
        )


def fetch_and_embed_index(query):
    console.print(f"🔎 Searching PubMed for: [italic]{query}[/italic]")
    results = search_and_fetch(query, limit=5)

    if not results:
        console.print("[red]❌ No papers found.[/red]")
        return None, None, []

    for paper in results:
        abstract = paper.get("Abstract", "")
        paper["Summary"] = summarize_with_llm(abstract) if abstract else "No abstract to summarize."

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    index, _, metadata = build_faiss_index(results, model)
    return index, model, metadata


def start_conversational_loop(papers):
    while True:
        follow_up = input("\n💬 Ask about a specific paper (e.g., 'Summarize paper 2') or type 'back' to start over: ").strip()
        if follow_up.lower() in {"back", "exit", "quit"}:
            break

        context = "\n\n".join([
            f"Paper {i+1}:\n"
            f"PubMed ID: {p.get('PubmedID')}\n"
            f"Title: {p['Title']}\n"
            f"Authors: {p.get('Authors', 'N/A')}\n"
            f"Abstract: {p.get('Abstract', 'N/A')}\n"
            f"Summary: {p.get('Summary', 'N/A')}"
            for i, p in enumerate(papers)
        ])

        prompt = (
            f"The user asked: {follow_up}\n\n"
            f"Here are the research papers:\n\n{context}\n\n"
            f"Answer the user's question based on this data."
        )

        response = chat_with_retry(prompt)
        console.print(f"\n🤖 [bold magenta]LLM:[/bold magenta] {response.strip()}\n")


def main():
    try:
        console.print("[bold blue]\n🔍 Welcome to the RAG-powered Research Assistant[/bold blue]")
        while True:
            query = input("\n🧠 Ask a research question (or type 'exit'): ").strip()
            if query.lower() in {"exit", "quit"}:
                console.print("[cyan]👋 Exiting RAG Assistant.[/cyan]")
                break

            index, model, metadata = fetch_and_embed_index(query)
            if not metadata:
                console.print(f"[yellow]⚠️ No relevant papers found for your question.[/yellow]")
                console.print(
                    f"[bold red]💡 Tip:[/bold red] You can download related papers using:\n"
                    f"[italic green]python -m src.pubmed_fetcher.cli \"{query}\" --limit 5 --file fresh_results --format csv --download[/italic green]\n"
                )
                console.print("[blue]📘 After downloading, rerun the assistant to get LLM summaries and answers.[/blue]")
                continue

            top_papers = retrieve_top_k(query, index, metadata, model)
            print_paper_summaries(top_papers)

            answer = generate_answer_with_context(query, top_papers)
            console.print(f"\n🤖 [bold green]LLM Answer:[/bold green] {answer.strip()}\n")

            console.print(
                f"[bold blue]\n📥 To download these papers:[/bold blue] "
                f"Run this:\n"
                f"[italic]python -m src.pubmed_fetcher.cli \"{query}\" --limit {len(top_papers)} --file filtered_results --format csv --download[/italic]\n"
            )

            # 🧠 Interactive chat loop
            start_conversational_loop(top_papers)

    except KeyboardInterrupt:
        console.print("\n[cyan]👋 Interrupted by user.[/cyan]")


if __name__ == "__main__":
    main()
