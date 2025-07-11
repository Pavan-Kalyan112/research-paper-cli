import os
import json
import faiss
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from rich.console import Console
from sentence_transformers import SentenceTransformer

console = Console()
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# === Model Loader ===
def get_embedding_model(model_name: str = MODEL_NAME) -> SentenceTransformer:
    """Load a SentenceTransformer model for embedding."""
    console.print(f"[bold blue]🔧 Loading embedding model: [italic]{model_name}[/italic][/bold blue]")
    try:
        model = SentenceTransformer(model_name)
        console.print("[green]✅ Embedding model loaded successfully.[/green]")
        return model
    except Exception as e:
        console.print(f"[red]❌ Failed to load embedding model: {e}[/red]")
        raise RuntimeError("Failed to load SentenceTransformer model.") from e


# === Data Loaders ===
def load_data(path: str = "summarized_results.json") -> List[dict]:
    """Load summarized paper data from JSON file."""
    path = Path(path)
    if not path.exists():
        console.print(f"[red]❌ Summary file not found: {path}[/red]")
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Invalid JSON structure. Expected a list of papers.")
            return data
    except Exception as e:
        console.print(f"[red]❌ Error loading JSON from {path}: {e}[/red]")
        return []


def load_faiss_index_and_metadata(index_path: str, meta_path: str) -> Tuple[Optional[faiss.IndexFlatL2], Optional[List[dict]]]:
    """Load existing FAISS index and metadata."""
    if not Path(index_path).exists() or not Path(meta_path).exists():
        console.print(f"[red]❌ Missing index or metadata file.[/red]")
        return None, None
    try:
        index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        return index, metadata
    except Exception as e:
        console.print(f"[red]❌ Error loading FAISS index or metadata: {e}[/red]")
        return None, None


# === Embedding Logic ===
def embed_texts(texts: List[str], model: Optional[SentenceTransformer] = None) -> np.ndarray:
    """Generate embeddings for given list of texts."""
    if model is None:
        model = get_embedding_model()
    try:
        return model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    except Exception as e:
        console.print(f"[red]❌ Embedding generation failed: {e}[/red]")
        return np.array([])


def embed_papers(papers: List[dict], model: Optional[SentenceTransformer] = None) -> Tuple[Optional[np.ndarray], Optional[List[dict]]]:
    """Create embeddings and metadata from paper list."""
    console.print(f"[blue]📄 Embedding {len(papers)} papers...[/blue]")

    texts_to_embed = [
        f"Title: {paper.get('Title', '')}. "
        f"Authors: {paper.get('Authors', 'N/A')}. "
        f"Summary: {paper.get('summary') or paper.get('Abstract', '')}"
        for paper in papers
    ]

    embeddings = embed_texts(texts_to_embed, model=model)
    if embeddings.size == 0:
        console.print("[red]❌ No embeddings generated.[/red]")
        return None, None

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

    return embeddings.astype("float32"), metadata


def build_faiss_index(embeddings: np.ndarray) -> Optional[faiss.IndexFlatL2]:
    """Create a FAISS index from embeddings."""
    if not isinstance(embeddings, np.ndarray) or embeddings.size == 0:
        console.print("[red]❌ Invalid or empty embeddings. Cannot build index.[/red]")
        return None
    try:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        return index
    except Exception as e:
        console.print(f"[red]❌ Failed to build FAISS index: {e}[/red]")
        return None


def save_index(index: faiss.IndexFlatL2, metadata: List[dict], output_dir: str = ".") -> None:
    """Save FAISS index and metadata to disk."""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        index_path = output_dir / "faiss_index.bin"
        meta_path = output_dir / "metadata.json"

        faiss.write_index(index, str(index_path))
        with meta_path.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        console.print(f"[green]✅ FAISS index and metadata saved:[/green]\n - {index_path}\n - {meta_path}")
    except Exception as e:
        console.print(f"[red]❌ Failed to save index or metadata: {e}[/red]")


# === CLI Main Runner ===
def main(data_path: str = "summarized_results.json"):
    console.print(f"[bold cyan]🚀 Starting FAISS embedding process: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold cyan]")

    papers = load_data(data_path)
    if not papers:
        console.print("[yellow]⚠️ No papers found. Exiting.[/yellow]")
        return

    model = get_embedding_model()
    embeddings, metadata = embed_papers(papers, model=model)
    if embeddings is None or metadata is None:
        return

    index = build_faiss_index(embeddings)
    if index is None:
        return

    save_index(index, metadata)
    console.print(f"[green]🎉 Embedding and indexing completed successfully![/green]")


if __name__ == "__main__":
    main()
