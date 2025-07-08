# src/pubmed_fetcher/utils.py

import csv
from fpdf import FPDF

def save_as_markdown(results: list, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        for paper in results:
            f.write(f"# {paper['title']}\n")
            f.write(f"**Authors:** {paper['authors']}\n\n")
            f.write(f"**Abstract:**\n{paper['abstract']}\n\n")
            if "summary" in paper:
                f.write(f"**LLM Summary:**\n{paper['summary']}\n\n")
            f.write("---\n\n")

def save_as_csv(results: list, filename: str):
    fieldnames = ["title", "authors", "abstract", "summary"]
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for paper in results:
            writer.writerow({
                "title": paper.get("title", ""),
                "authors": paper.get("authors", ""),
                "abstract": paper.get("abstract", ""),
                "summary": paper.get("summary", "")
            })

def save_as_pdf(results: list, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for paper in results:
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Title: {paper['title']}")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, f"Authors: {paper['authors']}")
        pdf.multi_cell(0, 10, f"Abstract: {paper['abstract']}")
        if "summary" in paper:
            pdf.set_text_color(0, 0, 128)
            pdf.multi_cell(0, 10, f"LLM Summary: {paper['summary']}")
            pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

    pdf.output(filename)
