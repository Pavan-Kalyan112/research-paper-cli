import argparse
import json
import os
from rich.console import Console

from pubmed_fetcher.data_pipeline import search_and_fetch
from pubmed_fetcher.utils import save_results
from pubmed_fetcher.llm import summarize_with_llm
from pubmed_fetcher.summary import summarize_abstract
from pubmed_fetcher.rag import main as rag_main  # ✅ Import RAG mode

console = Console()
CACHE_FILE = ".last_results.json"

def filter_by_keyword(papers, keyword):
    keyword = keyword.lower()
    return [
        paper for paper in papers
        if keyword in paper.get("Title", "").lower() or keyword in paper.get("Abstract", "").lower()
    ]

def append_extension(filename: str, ext: str):
    return filename if filename.endswith(f".{ext}") else f"{filename}.{ext}"

def main():
    parser = argparse.ArgumentParser(description="🧪 PubMed Research Paper Fetcher CLI Tool")

    # ✅ Optional positional query (only required when not in RAG mode)
    parser.add_argument("query", nargs="?", help="Search query for PubMed")

    parser.add_argument("-l", "--limit", type=int, default=5, help="Number of articles to fetch")
    parser.add_argument("-f", "--file", type=str, help="Filename to save results (without extension)")
    parser.add_argument("--format", choices=["csv", "pdf", "md"], help="File format to export (csv/pdf/md)")
    parser.add_argument("--llm", action="store_true", help="Use LLM to summarize abstracts")
    parser.add_argument("--download", action="store_true", help="Download raw JSON only")
    parser.add_argument("--filter-keyword", type=str, help="Filter papers by keyword in title/abstract")
    parser.add_argument("--rag", action="store_true", help="Start GPT-based conversational RAG chat")  # ✅ New flag
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # ✅ Run RAG assistant if --rag is specified
    if args.rag:
        rag_main()
        return

    # ✅ Otherwise, query is required
    if not args.query:
        parser.error("the following argument is required: query (unless using --rag)")

    console.print(f"[bold]INFO:[/bold] Searching PubMed for: [bold green]{args.query}[/bold green]...")
    results = search_and_fetch(args.query, args.limit)

    if not results:
        console.print("[bold red]ERROR:[/bold red] No articles found.")
        return

    if args.filter_keyword:
        results = filter_by_keyword(results, args.filter_keyword)
        if not results:
            console.print(f"[bold yellow]WARNING:[/bold yellow] No papers matched the keyword: {args.filter_keyword}")
            return

    if args.llm:
        console.print("[bold]INFO:[/bold] Generating LLM summaries for abstracts...")
        for paper in results:
            abstract = paper.get("Abstract", "")
            paper["summary"] = summarize_with_llm(abstract) if abstract.strip() else "No abstract provided."
            if args.debug:
                console.log(f"Summary: {paper['summary'][:100]}...")

    if args.download or args.format:
        if not args.file:
            console.print("[bold red]ERROR:[/bold red] Please specify a filename with --file when using --download or --format.")
            return

        if args.download:
            json_file = append_extension(args.file, "json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            console.print(f"[bold blue]SAVED:[/bold blue] Raw data saved to: {json_file}")

        if args.format:
            output_file = append_extension(args.file, args.format)
            save_results(results, output_file, args.format)
            console.print(f"[bold green]SUCCESS:[/bold green] {args.format.upper()} file saved as: {output_file}")

    elif args.file and args.format:
        output_file = append_extension(args.file, args.format)
        save_results(results, output_file, args.format)
        console.print(f"[bold green]SUCCESS:[/bold green] Results saved to {output_file}")

    else:
        for i, paper in enumerate(results, 1):
            console.rule(f"[bold blue]Paper {i}[/bold blue]")
            console.print(f"[bold]PubMed ID:[/bold] {paper.get('PubmedID', 'N/A')}")
            console.print(f"[bold]Title:[/bold] {paper.get('Title', 'N/A')}")
            console.print(f"[bold]Publication Date:[/bold] {paper.get('Publication Date', 'N/A')}")
            console.print(f"[bold]Non-academicAuthor(s):[/bold] {paper.get('Non-academicAuthor(s)', 'N/A')}")
            console.print(f"[bold]CompanyAffiliation(s):[/bold] {paper.get('CompanyAffiliation(s)', 'N/A')}")
            console.print(f"[bold]Corresponding Author Email:[/bold] {paper.get('Corresponding Author Email', 'N/A')}")
            console.print(f"[dim]Abstract:[/dim] {paper.get('Abstract', '')[:400]}...")
            if paper.get("summary"):
                console.print(f"[bold magenta]Summary:[/bold magenta] {paper['summary']}\n")

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        if args.debug:
            console.print(f"[grey]Cached results saved to {CACHE_FILE}[/grey]")
    except Exception as e:
        console.print(f"[bold red]ERROR:[/bold red] Failed to save cache: {e}")

if __name__ == "__main__":
    main()
