# src/pubmed_fetcher/semantic_search.py

import os
import json
import faiss
import numpy as np
from rich.console import Console
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pubmed_fetcher.chat import chat_with_llm  # Use only mistral
import argparse

load_dotenv()
console = Console()

INDEX_PATH = "faiss_index.bin"
META_PATH = "metadata.json"
EMBEDDING_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K = 3
CACHE_FILE = ".last_results.json"

def load_index():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        console.print("[yellow]⚠️ FAISS index or metadata not found. Using cache fallback.[/yellow]")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return None, json.load(f)
        return None, None
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return index, metadata

def embed_query(query, model):
    embedding = model.encode([query], normalize_embeddings=True)
    return embedding.astype("float32")

def search(query: str, top_k: int = TOP_K):
    console.print(f"\n🔎 Searching for: [bold green]{query}[/bold green]")
    index, metadata = load_index()
    if metadata is None:
        console.print("[red]❌ No metadata found. Please run CLI with --llm first.[/red]")
        return []

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    if index:
        query_vector = embed_query(query, model)
        distances, indices = index.search(query_vector, top_k)
        selected = [metadata[i] for i in indices[0]]
    else:
        # Brute-force fallback
        console.print("[blue]⚙️ Using brute-force similarity search (no FAISS index).[/blue]")
        all_texts = [p.get("summary") or p.get("Abstract", "") for p in metadata]
        query_vec = model.encode(query, convert_to_tensor=True)
        doc_vecs = model.encode(all_texts, convert_to_tensor=True)

        from sentence_transformers.util import cos_sim
        similarities = cos_sim(query_vec, doc_vecs)[0]
        top_k_idx = np.argsort(similarities)[-top_k:][::-1]
        selected = [metadata[i] for i in top_k_idx]

    for i, paper in enumerate(selected, 1):
        console.rule(f"[bold blue]Match {i}[/bold blue]")
        console.print(f"[bold]Title:[/bold] {paper['Title']}")
        console.print(f"[italic]Authors:[/italic] {paper.get('Authors', 'N/A')}")
        console.print(f"[dim]PubMed ID:[/dim] {paper['PubmedID']}")
        console.print(f"[italic]Affiliations:[/italic] {paper.get('CompanyAffiliation(s)', 'N/A')}")
        console.print(f"[italic]Email:[/italic] {paper.get('Corresponding Author Email', 'N/A')}")
        console.print(f"[dim]Abstract:[/dim] {paper['Abstract'][:400]}...\n")
    return selected

def ask_llm_about_matches(query: str, papers: list):
    if not papers:
        return
    context = "\n\n".join([
        f"Paper {i+1}:\nTitle: {p['Title']}\nAuthors: {p.get('Authors', 'N/A')}\nSummary: {p.get('summary', p.get('Abstract', 'N/A'))}"
        for i, p in enumerate(papers)
    ])
    prompt = f"The user query is:\n'{query}'\n\nUse the below research papers to answer it:\n\n{context}"
    answer = chat_with_llm(prompt)
    console.print(f"\n🤖 [bold magenta]LLM Response:[/bold magenta] {answer.strip()}\n")

def main():
    parser = argparse.ArgumentParser(description="🔎 Semantic Search on PubMed Papers")
    parser.add_argument("query", nargs="?", type=str, help="Search question for research papers")
    parser.add_argument("--topk", type=int, default=TOP_K, help="Number of top matches to return")
    parser.add_argument("--explain", action="store_true", help="Ask LLM to explain results")

    args = parser.parse_args()
    if args.query:
        matches = search(args.query, args.topk)
        if matches and args.explain:
            ask_llm_about_matches(args.query, matches)
    else:
        try:
            while True:
                query = input("🔍 Enter your research question (or 'exit'): ").strip()
                if query.lower() in {"exit", "quit"}:
                    console.print("[cyan]👋 Exiting semantic search.[/cyan]")
                    break
                matches = search(query)
                if matches:
                    follow = input("💬 Would you like the LLM to explain these results? (y/n): ").strip().lower()
                    if follow == "y":
                        ask_llm_about_matches(query, matches)
        except KeyboardInterrupt:
            console.print("\n[cyan]👋 Interrupted. Goodbye.[/cyan]")

if __name__ == "__main__":
    main()
