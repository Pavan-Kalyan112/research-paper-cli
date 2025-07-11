import os
import json
import faiss
import numpy as np
import argparse
from rich.console import Console
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from sentence_transformers.util import cos_sim
from pubmed_fetcher.chat import chat_with_llm  # Uses Mistral or model defined in .env

load_dotenv()
console = Console()

# === Constants ===
INDEX_PATH = "faiss_index.bin"
META_PATH = "metadata.json"
EMBEDDING_MODEL_NAME = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
TOP_K = 3
CACHE_FILE = ".last_results.json"

# === FAISS + Metadata ===
def load_index():
    """Load FAISS index and metadata or fallback to cache."""
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

# === Embedding ===
def embed_query(query, model):
    """Convert the query into a vector embedding."""
    embedding = model.encode([query], normalize_embeddings=True)
    return embedding.astype("float32")

# === Semantic Search ===
def search(query: str, top_k: int = TOP_K):
    """Search papers using FAISS or brute-force similarity."""
    console.print(f"\n🔎 Searching for: [bold green]{query}[/bold green]")
    index, metadata = load_index()

    if metadata is None:
        console.print("[red]❌ No metadata found. Please run CLI with --llm first to build summaries.[/red]")
        return []

    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    except Exception as e:
        console.print(f"[red]❌ Failed to load embedding model: {e}[/red]")
        return []

    if index:
        query_vector = embed_query(query, model)
        distances, indices = index.search(query_vector, top_k)
        selected = [metadata[i] for i in indices[0]]
    else:
        console.print("[blue]⚙️ Using brute-force similarity search (no FAISS index).[/blue]")
        all_texts = [p.get("summary") or p.get("Abstract", "") for p in metadata]
        if not any(all_texts):
            console.print("[red]❌ No summaries or abstracts found in metadata.[/red]")
            return []

        query_vec = model.encode(query, convert_to_tensor=True)
        doc_vecs = model.encode(all_texts, convert_to_tensor=True)
        similarities = cos_sim(query_vec, doc_vecs)[0]
        top_k_idx = np.argsort(similarities)[-top_k:][::-1]
        selected = [metadata[i] for i in top_k_idx]

    for i, paper in enumerate(selected, 1):
        console.rule(f"[bold blue]Match {i}[/bold blue]")
        console.print(f"[bold]Title:[/bold] {paper.get('Title', 'N/A')}")
        console.print(f"[italic]Authors:[/italic] {paper.get('Authors', 'N/A')}")
        console.print(f"[dim]PubMed ID:[/dim] {paper.get('PubmedID', 'N/A')}")
        console.print(f"[italic]Publication Date:[/italic] {paper.get('Publication Date', 'N/A')}")
        console.print(f"[italic]Affiliations:[/italic] {paper.get('CompanyAffiliation(s)', 'N/A')}")
        console.print(f"[italic]Email:[/italic] {paper.get('Corresponding Author Email', 'N/A')}")
        abstract = paper.get("Abstract", "")
        console.print(f"[dim]Abstract:[/dim] {abstract[:400]}...\n")

    return selected

# === Ask LLM to Explain ===
def ask_llm_about_matches(query: str, papers: list):
    """Send top matches + query to LLM and print the response."""
    if not papers:
        return
    context = "\n\n".join([
        f"Paper {i+1}:\n"
        f"Title: {p.get('Title', 'N/A')}\n"
        f"Authors: {p.get('Authors', 'N/A')}\n"
        f"Publication Date: {p.get('Publication Date', 'N/A')}\n"
        f"Summary: {p.get('summary', p.get('Abstract', 'N/A'))}"
        for i, p in enumerate(papers)
    ])
    prompt = f"The user query is:\n'{query}'\n\nUse the below research papers to answer it:\n\n{context}"
    answer = chat_with_llm(prompt)
    console.print(f"\n🤖 [bold magenta]LLM Response:[/bold magenta] {answer.strip()}\n")

# === CLI Entrypoint ===
def main():
    parser = argparse.ArgumentParser(description="🔎 Semantic Search on PubMed Papers")
    parser.add_argument("--query", type=str, help="Search question for research papers")
    parser.add_argument("--topk", type=int, default=TOP_K, help="Number of top matches to return")
    parser.add_argument("--explain", action="store_true", help="Ask LLM to explain the results")

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
