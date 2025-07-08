import requests
import xml.etree.ElementTree as ET
from pubmed_fetcher.filters import classify_authors


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

    # 🔍 Step 1: Get PubMed IDs based on search query
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax
    }

    search_response = requests.get(search_url, params=search_params)
    search_response.raise_for_status()
    idlist = search_response.json().get("esearchresult", {}).get("idlist", [])

    if not idlist:
        return []

    # 📥 Step 2: Fetch article details using EFetch
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(idlist),
        "retmode": "xml"
    }

    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_response.raise_for_status()
    return parse_pubmed_xml(fetch_response.text, idlist)


def parse_pubmed_xml(xml_data: str, idlist: list) -> list:
    """
    Parse XML and extract metadata including affiliations and emails.

    Args:
        xml_data (str): Raw XML from PubMed EFetch.
        idlist (list): List of PubMed IDs to match.

    Returns:
        list: List of paper metadata dictionaries.
    """
    root = ET.fromstring(xml_data)
    results = []

    for idx, article in enumerate(root.findall(".//PubmedArticle")):
        pubmed_id = idlist[idx] if idx < len(idlist) else "Unknown"
        title = article.findtext(".//ArticleTitle", default="No title available")
        abstract = article.findtext(".//AbstractText", default="No abstract available")

        # 📅 Extract publication year
        pub_date = (
            article.findtext(".//PubDate/Year") or
            article.findtext(".//DateCompleted/Year") or
            "Unknown"
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

        # 🧠 Custom logic from filters.py
        non_academic, companies, emails = classify_authors(affiliations)

        results.append({
            "pubmed_id": pubmed_id,
            "title": title,
            "publication_date": pub_date,
            "abstract": abstract,
            "authors": ", ".join(authors) if authors else "Unknown",
            "non_academic_authors": "; ".join(non_academic),
            "company_affiliations": "; ".join(companies),
            "corresponding_email": "; ".join(emails)
        })

    return results
