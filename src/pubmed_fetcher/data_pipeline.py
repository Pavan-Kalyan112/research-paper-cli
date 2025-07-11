import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
import os
import re

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EMAIL = os.getenv("NCBI_EMAIL", "neelampavan95@gmail.com")  # 🔧 Configurable via env var

# Define known pharmaceutical companies (expandable)
COMPANY_KEYWORDS = [
    "Pfizer", "Moderna", "AstraZeneca", "Johnson", "Novartis", "GSK",
    "Sanofi", "Bayer", "Roche", "Merck", "AbbVie", "Bristol-Myers"
]

def fetch_pubmed_ids(query: str, max_results: int = 10) -> List[str]:
    """
    Fetch PubMed IDs using ESearch API based on a given query.
    """
    try:
        response = requests.get(
            f"{ENTREZ_BASE}esearch.fcgi",
            params={
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
                "email": EMAIL
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("esearchresult", {}).get("idlist", [])
    except requests.RequestException as e:
        print(f"❌ Error fetching PubMed IDs: {e}")
        return []

def fetch_articles_xml(pmids: List[str]) -> ET.Element:
    """
    Fetch PubMed article details in XML format via EFetch API.
    """
    try:
        response = requests.get(
            f"{ENTREZ_BASE}efetch.fcgi",
            params={
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "email": EMAIL
            },
            timeout=10
        )
        response.raise_for_status()
        return ET.fromstring(response.content)
    except requests.RequestException as e:
        print(f"❌ Error fetching article XML: {e}")
        return ET.Element("Empty")

def extract_info(article: ET.Element) -> Dict:
    """
    Extract structured metadata from a PubMed XML article node.
    """
    pmid = article.findtext(".//PMID") or "N/A"
    title = article.findtext(".//ArticleTitle") or "No title available"
    pub_date = article.findtext(".//PubDate/Year") or "Unknown"
    abstract = article.findtext(".//AbstractText") or "No abstract available"

    authors = []
    non_academic_authors = set()
    company_affiliations = set()
    emails = set()

    for author in article.findall(".//Author"):
        first = author.findtext("ForeName", "")
        last = author.findtext("LastName", "")
        full_name = f"{first} {last}".strip()

        affil = author.findtext(".//AffiliationInfo/Affiliation")
        if affil:
            affil_lower = affil.lower()

            # Non-academic detection
            if "univ" not in affil_lower and "hospital" not in affil_lower:
                non_academic_authors.add(full_name)

            # Match pharma company
            for company in COMPANY_KEYWORDS:
                if company.lower() in affil_lower:
                    company_affiliations.add(company)

            # Extract emails using regex
            emails.update(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", affil))

        if full_name:
            authors.append(full_name)

    return {
        "PubmedID": pmid,
        "Title": title,
        "Publication Date": pub_date,
        "Authors": ", ".join(authors),
        "Abstract": abstract,
        "Non-academicAuthor(s)": "; ".join(non_academic_authors),
        "CompanyAffiliation(s)": "; ".join(company_affiliations),
        "Corresponding Author Email": "; ".join(emails)
    }

def search_and_fetch(query: str, limit: int = 10) -> List[Dict]:
    """
    Complete pipeline to fetch and parse PubMed articles.
    """
    pmids = fetch_pubmed_ids(query, limit)
    if not pmids:
        print("⚠️ No PubMed IDs found.")
        return []

    xml_root = fetch_articles_xml(pmids)
    articles = xml_root.findall(".//PubmedArticle")

    return [extract_info(article) for article in articles]

# 🔍 Dev/test CLI entry point
if __name__ == "__main__":
    query = input("🔎 Enter a PubMed query: ")
    results = search_and_fetch(query, limit=5)
    for idx, paper in enumerate(results, 1):
        print(f"\n📄 Paper {idx}")
        for k, v in paper.items():
            print(f"{k}: {v}")
