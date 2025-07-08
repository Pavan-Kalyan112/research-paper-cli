# src/pubmed_fetcher/filters.py

import re
from typing import List, Tuple


ACADEMIC_KEYWORDS = [
    "university", "institute", "school", "college", "hospital",
    "faculty", "department", "center", "centre"
]

COMPANY_KEYWORDS = [
    "inc", "ltd", "gmbh", "llc", "corp", "biotech", "pharma", "therapeutics"
]


def is_academic(affiliation: str) -> bool:
    return any(keyword in affiliation.lower() for keyword in ACADEMIC_KEYWORDS)


def is_company(affiliation: str) -> bool:
    return any(keyword in affiliation.lower() for keyword in COMPANY_KEYWORDS)


def extract_emails(text: str) -> List[str]:
    """
    Extracts email addresses from any string using regex.
    """
    email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    return re.findall(email_pattern, text)


def classify_authors(affiliations: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Classifies authors by their affiliations:
    - Non-academic authors
    - Company affiliations
    - Emails
    """
    non_academic_authors = []
    company_affiliations = []
    emails = []

    for aff in affiliations:
        if not is_academic(aff):
            non_academic_authors.append(aff)
        if is_company(aff):
            company_affiliations.append(aff)
        emails.extend(extract_emails(aff))

    return non_academic_authors, company_affiliations, list(set(emails))
