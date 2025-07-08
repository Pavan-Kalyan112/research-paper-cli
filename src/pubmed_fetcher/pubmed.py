import requests
import xml.etree.ElementTree as ET
from pubmed_fetcher.filters import classify_authors, extract_emails

def search_and_fetch(query: str, retmax: int = 5) -> list:
    """Search PubMed and fetch article metadata with extended fields."""
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    # Step 1: Search for PubMed IDs
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

    # Step 2: Fetch article details
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(idlist),
        "retmode": "xml"
    }

    fetch_response = requests.get(fetch_url, params=fetch_params)
    fetch_response.raise_for_status()
    return parse_pubmed_xml(fetch_response.text, idlist)

def parse_pubmed_xml(xml_data: str, idlist: list) -> list:
    """Parse XML and extract required metadata from PubMed articles."""
    root = ET.fromstring(xml_data)
    results = []

    for idx, article in enumerate(root.findall(".//PubmedArticle")):
        pubmed_id = idlist[idx] if idx < len(idlist) else "Unknown"
        title = article.findtext(".//ArticleTitle", default="No title available")
        abstract = article.findtext(".//AbstractText", default="No abstract available")
        pub_date = article.findtext(".//PubDate/Year") or article.findtext(".//DateCompleted/Year") or "Unknown"
        
        authors = []
        affiliations = []

        for author in article.findall(".//Author"):
            last = author.findtext("LastName")
            fore = author.findtext("ForeName")
            if last and fore:
                authors.append(f"{fore} {last}")

            aff = author.findtext(".//AffiliationInfo/Affiliation")
            if aff:
                affiliations.append(aff)

        # Extract additional info using filters
        non_academic, companies, emails = classify_authors(affiliations)

        results.append({
            "pubmed_id": pubmed_id,
            "title": title,
            "publication_date": pub_date,
            "abstract": abstract,
            "authors": ", ".join(authors) if authors else "Unknown",
            "non_academic_authors": "; ".join(non_academic),
            "company_affiliations": "; ".join(companies),
            "corresponding_emails": "; ".join(emails)
        })

    return results
