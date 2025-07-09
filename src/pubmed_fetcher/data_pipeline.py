import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EMAIL = "neelampavan95@gmail.com"  # Change to your email

# Add more companies if needed
COMPANY_KEYWORDS = [
    "Pfizer", "Moderna", "AstraZeneca", "Johnson", "Novartis", "GSK",
    "Sanofi", "Bayer", "Roche", "Merck", "AbbVie", "Bristol-Myers"
]


def fetch_pubmed_ids(query: str, max_results: int = 10) -> List[str]:
    """
    Fetch PubMed IDs using ESearch API.
    """
    response = requests.get(f"{ENTREZ_BASE}esearch.fcgi", params={
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "email": EMAIL
    })
    response.raise_for_status()
    return response.json()["esearchresult"].get("idlist", [])


def fetch_articles_xml(pmids: List[str]) -> ET.Element:
    """
    Fetch full XML article metadata from PubMed using EFetch API.
    """
    response = requests.get(f"{ENTREZ_BASE}efetch.fcgi", params={
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": EMAIL
    })
    response.raise_for_status()
    return ET.fromstring(response.content)


def extract_info(article: ET.Element) -> Dict:
    """
    Parse metadata from a single PubMed XML article.
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
        first = author.findtext("ForeName") or ""
        last = author.findtext("LastName") or ""
        full_name = f"{first} {last}".strip()

        affil = author.findtext(".//AffiliationInfo/Affiliation")
        if affil:
            if "univ" not in affil.lower() and "hospital" not in affil.lower():
                non_academic_authors.add(full_name)

            for company in COMPANY_KEYWORDS:
                if company.lower() in affil.lower():
                    company_affiliations.add(company)

            emails.update(word for word in affil.split() if "@" in word)

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
    Full pipeline from query → XML fetch → metadata extraction.
    """
    pmids = fetch_pubmed_ids(query, limit)
    if not pmids:
        return []

    xml_root = fetch_articles_xml(pmids)
    articles = xml_root.findall(".//PubmedArticle")

    return [extract_info(article) for article in articles]
