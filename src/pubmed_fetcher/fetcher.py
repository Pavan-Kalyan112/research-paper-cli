# src/pubmed_fetcher/fetcher.py

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
    result = response.json().get("result", {})

    summaries = []
    for uid in ids:
        item = result.get(uid)
        if not item:
            continue

        summaries.append({
            "pubmed_id": uid,
            "title": item.get("title", "No Title"),
            "publication_date": item.get("pubdate", "Unknown"),
            "authors": [author.get("name", "Unknown") for author in item.get("authors", [])],
            "source": item.get("source", "Unknown"),
            "doi": item.get("elocationid", "N/A"),
        })

    return summaries
