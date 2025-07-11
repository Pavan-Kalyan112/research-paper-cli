import os
import requests
import xml.etree.ElementTree as ET
from rich.console import Console
from dotenv import load_dotenv

from pubmed_fetcher.filters import classify_authors
from pubmed_fetcher.summary import summarize_abstract

load_dotenv()
console = Console()

NCBI_EMAIL = os.getenv("NCBI_EMAIL", "neelampavan95@gmail.com")  # Optional override


def search_and_fetch(query: str, retmax: int = 5) -> list:
    """
    Search PubMed and fetch article metadata with extended fields.

    Args:
        query (str): Search term for PubMed.
        retmax (int): Max number of articles to fetch.

    Returns:
        list: List of dictionaries with metadata for each paper.
    """
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # 🔍 Step 1: Get PubMed IDs
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "email": NCBI_EMAIL
    }

    try:
        search_response = requests.get(search_url, params=search_params, timeout=10)
        search_response.raise_for_status()
        idlist = search_response.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        console.print(f"[red]❌ Failed to search PubMed: {e}[/red]")
        return []

    if not idlist:
        console.print("[yellow]⚠️ No papers found for this query.[/yellow]")
        return []

    # 📥 Step 2: Fetch metadata
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(idlist),
        "retmode": "xml",
        "email": NCBI_EMAIL
    }

    try:
        fetch_response = requests.get(fetch_url, params=fetch_params, timeout=10)
        fetch_response.raise_for_status()
        return parse_pubmed_xml(fetch_response.text, idlist)
    except Exception as e:
        console.print(f"[red]❌ Failed to fetch article details: {e}[/red]")
        return []


def parse_pubmed_xml(xml_data: str, idlist: list) -> list:
    """
    Parse PubMed XML and extract article metadata.

    Args:
        xml_data (str): Raw XML response from PubMed.
        idlist (list): List of PubMed IDs for reference.

    Returns:
        list: List of article metadata dictionaries.
    """
    root = ET.fromstring(xml_data)
    results = []

    for idx, article in enumerate(root.findall(".//PubmedArticle")):
        pubmed_id = idlist[idx] if idx < len(idlist) else "Unknown"
        title = article.findtext(".//ArticleTitle", default="No title available")
        abstract = article.findtext(".//AbstractText", default="No abstract available")

        # 📅 Publication year
        pub_date = (
            article.findtext(".//PubDate/Year")
            or article.findtext(".//DateCompleted/Year")
            or "Unknown"
        )

        authors = []
        affiliations = []

        for author in article.findall(".//Author"):
            fore = author.findtext("ForeName")
            last = author.findtext("LastName")
            if fore and last:
                authors.append(f"{fore} {last}")

            aff = author.findtext(".//AffiliationInfo/Affiliation")
            if aff:
                affiliations.append(aff)

        # 🏢 Classify affiliations
        non_academic, companies, emails = classify_authors(affiliations)

        # 🧠 Optional: summarize abstract using LLM
        # summary = summarize_abstract(abstract) if abstract else "No abstract available"

        paper_data = {
            "PubmedID": pubmed_id,
            "Title": title,
            "Publication Date": pub_date,
            "Authors": ", ".join(authors) if authors else "Unknown",
            "Abstract": abstract,
            # "summary": summary,  # Uncomment if needed
            "Non-academicAuthor(s)": "; ".join(non_academic),
            "CompanyAffiliation(s)": "; ".join(companies),
            "Corresponding Author Email": "; ".join(emails)
        }

        results.append(paper_data)

    return results
