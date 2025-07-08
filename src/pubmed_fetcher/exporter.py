import requests
import xml.etree.ElementTree as ET
import csv

ENTREZ_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EMAIL = "neelampavan95@gmail.com"  # replace with your email

COMPANY_KEYWORDS = ["Pfizer", "Moderna", "AstraZeneca", "Johnson", "Novartis", "GSK"]

def fetch_pubmed_ids(query, max_results=10):
    res = requests.get(f"{ENTREZ_BASE}esearch.fcgi", params={
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "email": EMAIL
    })
    res.raise_for_status()
    return res.json()["esearchresult"]["idlist"]

def fetch_articles(pmids):
    res = requests.get(f"{ENTREZ_BASE}efetch.fcgi", params={
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "email": EMAIL
    })
    res.raise_for_status()
    return ET.fromstring(res.content)

def extract_info(article):
    pmid = article.findtext(".//PMID")
    title = article.findtext(".//ArticleTitle")
    pub_date = article.findtext(".//PubDate/Year") or "Unknown"

    authors = []
    emails = set()
    company_affiliations = set()
    non_academic_authors = set()

    for author in article.findall(".//Author"):
        last = author.findtext("LastName") or ""
        first = author.findtext("ForeName") or ""
        full_name = f"{first} {last}".strip()

        affil = author.findtext(".//AffiliationInfo/Affiliation")
        if affil:
            if "univ" not in affil.lower() and "hospital" not in affil.lower():
                non_academic_authors.add(full_name)
            for company in COMPANY_KEYWORDS:
                if company.lower() in affil.lower():
                    company_affiliations.add(company)
            if "@" in affil:
                emails.update(part for part in affil.split() if "@" in part)

        authors.append(full_name)

    return {
        "PubmedID": pmid,
        "Title": title,
        "Publication Date": pub_date,
        "Non-academic Author(s)": "; ".join(non_academic_authors),
        "Company Affiliation(s)": "; ".join(company_affiliations),
        "Corresponding Author Email": "; ".join(emails)
    }

def export_to_csv(data, filename="pubmed_results.csv"):
    if not data:
        print("❌ No data to export.")
        return
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Results saved to: {filename}")

def main(query="covid vaccine", max_results=5):
    pmids = fetch_pubmed_ids(query, max_results)
    xml_root = fetch_articles(pmids)
    articles = xml_root.findall(".//PubmedArticle")

    extracted = [extract_info(article) for article in articles]
    export_to_csv(extracted)
