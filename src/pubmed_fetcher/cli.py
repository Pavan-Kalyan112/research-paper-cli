import argparse
import json
import os
import sys
from rich.console import Console
from pubmed_fetcher import config
from pubmed_fetcher.data_pipeline import search_and_fetch
from pubmed_fetcher.utils import save_results
from pubmed_fetcher.llm import summarize_with_llm
from pubmed_fetcher.rag import main as rag_main
from pubmed_fetcher.chat import interactive_llm_chat

console = Console()

# Ensure proper Unicode support on Windows
if sys.platform == "win32":
    os.system("")
    sys.stdout.reconfigure(encoding="utf-8")

# Create exports directory
exports_dir = os.path.join(os.getcwd(), "exports")
os.makedirs(exports_dir, exist_ok=True)


def filter_by_keyword(papers, keyword):
    keyword = keyword.lower()
    return [
        paper for paper in papers
        if keyword in paper.get("Title", "").lower() or keyword in paper.get("Abstract", "").lower()
    ]


def append_extension(filename: str, ext: str):
    return filename if filename.endswith(f".{ext}") else f"{filename}.{ext}"


def handle_query(query, args):
    console.print(f"[bold]🔍 Searching PubMed for:[/bold] [green]{query}[/green]")
    results = search_and_fetch(query, args.limit)

    if not results:
        console.print("[red]❌ No articles found.[/red]")
        return

    # Optional keyword filter
    if args.filter_keyword:
        results = filter_by_keyword(results, args.filter_keyword)
        if not results:
            console.print(f"[yellow]⚠️ No papers matched keyword: {args.filter_keyword}[/yellow]")
            return

    # LLM summarization
    if args.llm and config.LLM_ENABLED:
        console.print("[cyan]✨ Generating summaries with LLM...[/cyan]")
        for paper in results:
            abstract = paper.get("Abstract", "")
            paper["summary"] = summarize_with_llm(abstract) if abstract.strip() else "No abstract provided."
            if args.debug:
                console.log(f"Summary: {paper['summary'][:1000]}...")

    output_name = args.file
    json_file_path = None

    if args.download or args.format:
        if not output_name:
            console.print("[red]❌ Please specify --file when using --download or --format.[/red]")
            return

        if args.download:
            json_file_path = os.path.join(exports_dir, append_extension(output_name, "json"))
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            console.print(f"[blue]📁 Raw JSON saved to:[/blue] {json_file_path}")

        if args.format:
            output_file = os.path.join(exports_dir, append_extension(output_name, args.format))
            try:
                save_results(results, output_file, args.format)
                console.print(f"[green]✅ Exported as {args.format.upper()}:[/green] {output_file}")
            except Exception as e:
                console.print(f"[red]❌ Failed to save {args.format.upper()}: {e}[/red]")
    else:
        for i, paper in enumerate(results, 1):
            console.rule(f"[blue]📄 Paper {i}[/blue]")
            console.print(f"[bold]PubMed ID:[/bold] {paper.get('PubmedID', 'N/A')}")
            console.print(f"[bold]Title:[/bold] {paper.get('Title', 'N/A')}")
            console.print(f"[bold]Publication Date:[/bold] {paper.get('Publication Date', 'N/A')}")
            console.print(f"[bold]Company Affiliation(s):[/bold] {paper.get('CompanyAffiliation(s)', 'N/A')}")
            console.print(f"[bold]Corresponding Author Email:[/bold] {paper.get('Corresponding Author Email', 'N/A')}")
            console.print(f"[dim]Abstract:[/dim] {paper.get('Abstract', '')[:400]}...")
            if paper.get("summary"):
                console.print(f"[magenta]Summary:[/magenta] {paper['summary']}\n")

    # Save cached result
    try:
        session_cache = os.path.join(exports_dir, "summarized_results.json")
        with open(session_cache, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        if args.debug:
            console.print(f"[grey]🗃️ Cached to: {session_cache}[/grey]")
    except Exception as e:
        console.print(f"[red]❌ Cache failed: {e}[/red]")

    # Optional RAG assistant
    if args.rag and args.file:
        if not json_file_path:
            json_file_path = os.path.join(exports_dir, append_extension(output_name, "json"))
        if os.path.exists(json_file_path):
            console.print("\n[bold blue]🧠 Launching RAG Assistant on saved data...[/bold blue]")
            rag_main(json_path=json_file_path, query=query)
        else:
            console.print(f"[red]❌ Cannot launch RAG - file not found: {json_file_path}[/red]")


def user_operation_loop(args):
    if args.chat:
        interactive_llm_chat()
        return

    if args.rag and args.use_file:
        rag_main(json_path=args.use_file, query=args.query)
        return

    if args.query:
        handle_query(args.query, args)

    # Start interactive loop
    while True:
        try:
            next_action = input("\n🔄 Do you want to make another query? Type 'yes' to continue or 'exit' to quit: ").strip().lower()
            if next_action in {"exit", "logout", "no", "n", "q"}:
                console.print("[cyan]👋 Session ended.[/cyan]")
                break

            new_query = input("🔎 Enter your new PubMed search query: ").strip()
            if not new_query:
                console.print("[yellow]⚠️ No query entered. Skipping.[/yellow]")
                continue

            args.query = new_query
            handle_query(new_query, args)
        except EOFError:
            console.print("\n[red]❌ Input stream closed unexpectedly. Exiting...[/red]")
            break
        except KeyboardInterrupt:
            console.print("\n[cyan]👋 Interrupted. Goodbye.[/cyan]")
            break


def main():
    parser = argparse.ArgumentParser(
        description="🧪 PubMed Research Paper Fetcher CLI Tool (LLM + RAG + Chat)"
    )
    parser.add_argument("--query", type=str, help="Search query for PubMed")
    parser.add_argument("-l", "--limit", type=int, default=config.DEFAULT_FETCH_LIMIT, help="Number of articles to fetch")
    parser.add_argument("-f", "--file", type=str, help="Filename to save results (without extension)")
    parser.add_argument("--format", choices=["csv", "pdf", "md"], help="File format to export (csv/pdf/md)")
    parser.add_argument("--llm", action="store_true", help="Use LLM to summarize abstracts")
    parser.add_argument("--download", action="store_true", help="Download raw JSON only")
    parser.add_argument("--filter-keyword", type=str, help="Filter papers by keyword in title/abstract")
    parser.add_argument("--rag", action="store_true", help="Start RAG-based Q&A mode")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat with LLM from summarized_results.json")
    parser.add_argument("--use-file", type=str, help="Path to a summarized_results.json file")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    user_operation_loop(args)


if __name__ == "__main__":
    main()
