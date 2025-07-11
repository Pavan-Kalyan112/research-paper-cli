import csv
import os
from pathlib import Path
from typing import List
from fpdf import FPDF
from rich.console import Console

console = Console()


def save_as_csv(results: List[dict], filename: str):
    """
    Save the fetched papers to a CSV file.
    """
    fieldnames = [
        "PubmedID",
        "Title",
        "Authors",
        "Summary",
        "Publication Date",
        "CompanyAffiliation(s)",
        "Corresponding Author Email",
        "Abstract"
    ]

    try:
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
                quoting=csv.QUOTE_ALL,
                quotechar='"',
                delimiter=','
            )
            writer.writeheader()
            for paper in results:
                writer.writerow({
                    "PubmedID": paper.get("PubmedID", ""),
                    "Title": paper.get("Title", ""),
                    "Authors": paper.get("Authors", ""),
                    "Summary": paper.get("summary", paper.get("Abstract", "")),
                    "Publication Date": paper.get("Publication Date", ""),
                    "CompanyAffiliation(s)": paper.get("CompanyAffiliation(s)", ""),
                    "Corresponding Author Email": paper.get("Corresponding Author Email", ""),
                    "Abstract": paper.get("Abstract", "")
                })
        console.print(f"[green]✅ Results successfully saved as CSV:[/green] {filename}")
    except Exception as e:
        console.print(f"[red]❌ Failed to save CSV: {e}[/red]")


def save_as_pdf(results: List[dict], filename: str):
    """
    Save the fetched papers to a PDF file using built-in font (Helvetica).
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    for paper in results:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 10, f"Title: {paper.get('Title', '')}")
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 10, f"PubMed ID: {paper.get('PubmedID', '')}")
        pdf.multi_cell(0, 10, f"Authors: {paper.get('Authors', '')}")
        pdf.multi_cell(0, 10, f"Publication Date: {paper.get('Publication Date', '')}")
        pdf.multi_cell(0, 10, f"Company Affiliations: {paper.get('CompanyAffiliation(s)', '')}")
        pdf.multi_cell(0, 10, f"Corresponding Email: {paper.get('Corresponding Author Email', '')}")
        pdf.multi_cell(0, 10, f"Abstract: {paper.get('Abstract', '')}")

        if paper.get("summary"):
            pdf.set_text_color(0, 0, 128)
            pdf.multi_cell(0, 10, f"Summary: {paper['summary']}")
            pdf.set_text_color(0, 0, 0)

        pdf.ln(10)

    try:
        pdf.output(filename)
        console.print(f"[green]✅ Results successfully saved as PDF:[/green] {filename}")
    except Exception as e:
        console.print(f"[red]❌ Failed to save PDF: {e}[/red]")


def save_as_markdown(results: List[dict], filename: str):
    """
    Save the fetched papers to a Markdown file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for paper in results:
                f.write(f"# {paper.get('Title', '')}\n\n")
                f.write(f"- **PubMed ID**: {paper.get('PubmedID', '')}\n")
                f.write(f"- **Authors**: {paper.get('Authors', '')}\n")
                f.write(f"- **Publication Date**: {paper.get('Publication Date', '')}\n")
                f.write(f"- **Company Affiliations**: {paper.get('CompanyAffiliation(s)', '')}\n")
                f.write(f"- **Corresponding Email**: {paper.get('Corresponding Author Email', '')}\n")
                f.write(f"- **Abstract**: {paper.get('Abstract', '')}\n")
                if paper.get("summary"):
                    f.write(f"\n### Summary\n{paper['summary']}\n")
                f.write("\n---\n\n")
        console.print(f"[green]✅ Results successfully saved as Markdown:[/green] {filename}")
    except Exception as e:
        console.print(f"[red]❌ Failed to save Markdown: {e}[/red]")


def save_results(results: List[dict], filename: str, format: str):
    """
    Save results in the specified format: csv, pdf, or markdown.
    Raises ValueError for unsupported formats.
    """
    format = format.lower()
    Path(filename).parent.mkdir(parents=True, exist_ok=True)

    try:
        if format == "csv":
            save_as_csv(results, filename)
        elif format == "pdf":
            save_as_pdf(results, filename)
        elif format in ["md", "markdown"]:
            save_as_markdown(results, filename)
        else:
            raise ValueError(f"Unsupported format: '{format}'. Use 'csv', 'pdf', or 'markdown'.")
    except ValueError:
        raise  # Allow test to catch it
    except Exception as e:
        console.print(f"[red]❌ Error saving results: {e}[/red]")
