# src/pubmed_fetcher/cli.py

import argparse
import json
from rich.console import Console

from pubmed_fetcher.pubmed import search_and_fetch
from pubmed_fetcher.summarizer import summarize_abstract
from pubmed_fetcher.utils import save_as_csv, save_as_pdf, save_as_markdown

console = Console()

def main():
    parser = argparse.ArgumentParser(description="PubMed Research Paper Fetcher with LLM Summarizer")
    parser.add_argument("query", type=str, help="Search query for PubMed")
    parser.add_argument("-l", "--limit", type=int, default=3, help="Number of articles to fetch")
    parser.add_argument("-f", "--file", type=str, help="Filename to save results (optional)")
    parser.add_argument("--format", choices=["csv", "pdf", "md"], help="Output format if saving")
    parser.add_argument("--llm", action="store_true", help="Use LLM to summarize abstracts")
    parser.add_argument("--download", action="store_true", help="Download only and save raw JSON")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Logging search
    if args.debug:
        console.log(f"Searching for: {args.query}, Limit: {args.limit}")
    results = search_and_fetch(args.query, args.limit)

    if not results:
        console.print("[red]No results found for your query.[/red]")
        return

    # Save raw data if requested
    if args.download:
        json_file = (args.file or "raw_pubmed_data") + ".json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        console.print(f"Raw data saved to [green]{json_file}[/green]")
        return

    # Summarize using LLM
    if args.llm:
        for paper in results:
            summary = summarize_abstract(paper.get("abstract", ""))
            paper["summary"] = summary
            if args.debug:
                console.log(f"LLM summary: {summary[:120]}...")

    # Save to file
    if args.file and args.format:
        filename = args.file
        if args.format == "csv":
            save_as_csv(results, filename)
        elif args.format == "pdf":
            save_as_pdf(results, filename)
        elif args.format == "md":
            save_as_markdown(results, filename)
        console.print(f"Results saved to: [blue]{filename}[/blue]")
        return

    # Show in console
    for i, paper in enumerate(results, 1):
        console.rule(f"Paper {i}")
        console.print(f"[bold]Title:[/bold] {paper.get('title', 'No title')}")
        console.print(f"[italic]Authors:[/italic] {paper.get('authors', 'Unknown')}")
        console.print(f"[dim]Abstract:[/dim] {paper.get('abstract', 'No abstract')[:500]}...\n")
        if "summary" in paper:
            console.print(f"[magenta]Summary:[/magenta] {paper['summary']}\n")

if __name__ == "__main__":
    main()
