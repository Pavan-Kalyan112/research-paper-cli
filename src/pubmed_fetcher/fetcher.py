import requests
from typing import List, Dict


def fetch_pubmed_ids(query: str, max_results: int = 10) -> List[str]:
    """
    Use PubMed ESearch API to retrieve a list of PubMed IDs for a given query.
    
    Args:
        query (str): The search query (supports full PubMed syntax).
        max_results (int): Max number of PubMed IDs to return.
    
    Returns:
        List[str]: List of PubMed IDs.
    """
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return data.get("esearchresult", {}).get("idlist", [])


def fetch_pubmed_details(ids: List[str]) -> List[Dict]:
    """
    Use PubMed ESummary API to retrieve metadata for given PubMed IDs.
    
    Args:
        ids (List[str]): List of PubMed IDs.
    
    Returns:
        List[Dict]: List of dictionaries containing metadata for each paper.
    """
    if not ids:
        return []

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json().get("result", {})

    summaries = []
    for uid in ids:
        item = data.get(uid)
        if not item:
            continue

        authors_list = item.get("authors", [])
        authors = [author.get("name", "Unknown") for author in authors_list]

        summaries.append({
            "pubmed_id": uid,
            "title": item.get("title", "No Title"),
            "publication_date": item.get("pubdate", "Unknown"),
            "authors": ", ".join(authors) if authors else "Unknown",
            "source": item.get("source", "Unknown"),
            "doi": item.get("elocationid", "N/A"),
            # Additional fields for CSV compatibility
            "non_academic_authors": "N/A",          # Placeholder, can be filled by `filters`
            "company_affiliations": "N/A",          # Placeholder
            "corresponding_email": "N/A"            # Placeholder
        })

    return summaries
