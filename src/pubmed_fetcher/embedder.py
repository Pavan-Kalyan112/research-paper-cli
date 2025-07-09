# src/pubmed_fetcher/embedder.py

import os
import json
import faiss
import numpy as np
from rich.console import Console
from sentence_transformers import SentenceTransformer

console = Console()

# File paths
SUMMARY_FILE = "summarized_results.json"
INDEX_FILE = "faiss_index.bin"
META_FILE = "metadata.json"

# Load embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def load_data():
    if not os.path.exists(SUMMARY_FILE):
        console.print(f"[red]❌ Summary file not found: {SUMMARY_FILE}[/red]")
        return []
    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def embed_texts(texts):
    return model.encode(texts, show_progress_bar=True)

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def save_index(index, metadata):
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    console.print(f"[green]✅ FAISS index and metadata saved to {INDEX_FILE} and {META_FILE}[/green]")

def main():
    console.print("[blue]🔍 Loading summarized research papers...[/blue]")
    papers = load_data()
    if not papers:
        return

    console.print(f"[cyan]📄 {len(papers)} papers loaded. Generating embeddings...[/cyan]")

    texts_to_embed = [
        f"Title: {paper.get('Title', '')}. "
        f"Authors: {paper.get('Authors', 'N/A')}. "
        f"Summary: {paper.get('summary') or paper.get('Abstract', '')}"
        for paper in papers
    ]

    embeddings = embed_texts(texts_to_embed)
    embeddings_np = np.array(embeddings).astype("float32")

    index = build_faiss_index(embeddings_np)

    metadata = [
        {
            "PubmedID": paper.get("PubmedID"),
            "Title": paper.get("Title"),
            "Authors": paper.get("Authors"),
            "Summary": paper.get("summary", paper.get("Abstract")),
            "Publication Date": paper.get("Publication Date"),
            "CompanyAffiliation(s)": paper.get("CompanyAffiliation(s)"),
            "Corresponding Author Email": paper.get("Corresponding Author Email"),
            "Abstract": paper.get("Abstract", "")
        }
        for paper in papers
    ]

    save_index(index, metadata)

if __name__ == "__main__":
    main()
