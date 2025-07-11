import re
import string
from typing import List, Tuple, Set

__all__ = [
    "classify_authors",
    "extract_emails",
    "extract_person_name",
]

# ✅ List of pharmaceutical/biotech companies
COMPANY_KEYWORDS = [
    "Pfizer", "Moderna", "AstraZeneca", "Johnson", "Novartis", "GSK",
    "Merck", "Sanofi", "Roche", "Bayer", "Amgen", "Biogen", "AbbVie",
    "Eli Lilly", "Takeda", "Genentech", "Bristol-Myers", "Regeneron", "Vertex"
]

# ✅ Common academic institutions (to exclude)
ACADEMIC_KEYWORDS = [
    "university", "institute", "college", "school of medicine",
    "hospital", "center", "centre", "faculty", "department"
]


def extract_emails(text: str) -> Set[str]:
    """
    Extract all email addresses from the given text using regex.

    Args:
        text (str): Text to search for email addresses.

    Returns:
        Set[str]: Set of unique email addresses found in the text.
    """
    return set(re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text))


def extract_person_name(affiliation: str) -> str:
    """
    Attempt to extract a person's name from an affiliation string using heuristics.

    Args:
        affiliation (str): An author's affiliation.

    Returns:
        str: Extracted name if possible, otherwise "Unknown".
    """
    tokens = affiliation.strip().split()
    name_tokens = [token.strip(string.punctuation) for token in tokens if token.istitle()]

    if len(name_tokens) >= 2:
        return f"{name_tokens[0]} {name_tokens[1]}"
    elif name_tokens:
        return name_tokens[0]
    return "Unknown"


def classify_authors(affiliations: List[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Classify author affiliations into:
        - Non-academic authors
        - Company affiliations
        - Email addresses

    Args:
        affiliations (List[str]): A list of affiliation strings.

    Returns:
        Tuple:
            - Set[str]: Names of non-academic authors.
            - Set[str]: Company names detected in affiliations.
            - Set[str]: Emails extracted from affiliations.
    """
    non_academic_names = set()
    company_names = set()
    email_addresses = set()

    for aff in affiliations:
        aff_lower = aff.lower()

        # Check for academic keywords
        is_academic = any(keyword in aff_lower for keyword in ACADEMIC_KEYWORDS)

        # If not academic, try extracting non-academic author name
        if not is_academic:
            name = extract_person_name(aff)
            if name != "Unknown":
                non_academic_names.add(name)

        # Check for company affiliations (case-insensitive)
        for company in COMPANY_KEYWORDS:
            if company.lower() in aff_lower:
                company_names.add(company)

        # Extract email addresses
        email_addresses.update(extract_emails(aff))

    return non_academic_names, company_names, email_addresses
