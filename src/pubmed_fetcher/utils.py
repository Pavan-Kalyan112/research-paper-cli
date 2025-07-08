import csv
from fpdf import FPDF
from typing import List


def save_as_csv(results: List[dict], filename: str):
    fieldnames = [
        "pubmed_id",
        "title",
        "publication_date",
        "non_academic_authors",
        "company_affiliations",
        "corresponding_email",
        "summary"
    ]

    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for paper in results:
            writer.writerow({
                "pubmed_id": paper.get("pubmed_id", ""),
                "title": paper.get("title", ""),
                "publication_date": paper.get("publication_date", ""),
                "non_academic_authors": paper.get("non_academic_authors", ""),
                "company_affiliations": paper.get("company_affiliations", ""),
                "corresponding_email": paper.get("corresponding_email", ""),
                "summary": paper.get("summary", "")
            })


def save_as_pdf(results: List[dict], filename: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for paper in results:
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Title: {paper.get('title', '')}")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, f"PubMed ID: {paper.get('pubmed_id', '')}")
        pdf.multi_cell(0, 10, f"Publication Date: {paper.get('publication_date', '')}")
        pdf.multi_cell(0, 10, f"Non-academic Authors: {paper.get('non_academic_authors', '')}")
        pdf.multi_cell(0, 10, f"Company Affiliations: {paper.get('company_affiliations', '')}")
        pdf.multi_cell(0, 10, f"Corresponding Email: {paper.get('corresponding_email', '')}")
        if paper.get("summary"):
            pdf.set_text_color(0, 0, 128)
            pdf.multi_cell(0, 10, f"LLM Summary: {paper['summary']}")
            pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

    pdf.output(filename)


def save_as_markdown(results: List[dict], filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        for paper in results:
            f.write(f"# {paper.get('title', '')}\n\n")
            f.write(f"- **PubMed ID**: {paper.get('pubmed_id', '')}\n")
            f.write(f"- **Publication Date**: {paper.get('publication_date', '')}\n")
            f.write(f"- **Non-academic Authors**: {paper.get('non_academic_authors', '')}\n")
            f.write(f"- **Company Affiliations**: {paper.get('company_affiliations', '')}\n")
            f.write(f"- **Corresponding Email**: {paper.get('corresponding_email', '')}\n")
            if paper.get("summary"):
                f.write(f"\n### Summary\n{paper['summary']}\n")
            f.write("\n---\n\n")


def save_results(results: List[dict], filename: str, format: str):
    """
    Save research paper results to the specified file format.

    Args:
        results (list): List of dictionaries containing paper data.
        filename (str): Output filename.
        format (str): Format to save the results: 'csv', 'pdf', or 'markdown'.
    """
    format = format.lower()

    if format == "csv":
        save_as_csv(results, filename)
    elif format == "pdf":
        save_as_pdf(results, filename)
    elif format in ["md", "markdown"]:
        save_as_markdown(results, filename)
    else:
        raise ValueError(f"❌ Unsupported format: '{format}'. Use 'csv', 'pdf', or 'markdown'.")
