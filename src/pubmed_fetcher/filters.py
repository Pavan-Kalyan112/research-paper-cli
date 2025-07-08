import re
from typing import List, Tuple

# Keywords to identify non-academic institutions
NON_ACADEMIC_KEYWORDS = [
    "hospital", "clinic", "health center", "medical center", "institute of health",
    "research institute", "gov", "ministry", "department of health", "nhs", "cdc",
    "independent", "researcher"
]


# Keywords to identify company affiliations (common pharma/biotech/corporate indicators)
COMPANY_KEYWORDS = [
    "pharma", "biotech", "inc", "ltd", "llc", "gmbh", "corp", "co.", "company",
    "novartis", "pfizer", "astrazeneca", "moderna", "gsk", "sanofi", "abbvie",
    "johnson", "merck", "bayer", "roche", "takeda", "amgen"
]

# Regex pattern for email extraction
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


def extract_emails(affiliations: List[str]) -> List[str]:
    """
    Extract all email addresses from a list of affiliation strings.

    Args:
        affiliations (List[str]): List of affiliations.

    Returns:
        List[str]: List of unique email addresses.
    """
    emails = []
    for aff in affiliations:
        found = re.findall(EMAIL_REGEX, aff)
        emails.extend(found)
    return list(set(emails))


def classify_authors(affiliations: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Classify affiliations into non-academic, company-affiliated, and extract emails.

    Args:
        affiliations (List[str]): Raw affiliation strings.

    Returns:
        Tuple[List[str], List[str], List[str]]:
            - non_academic: List of non-academic affiliations
            - companies: List of company affiliations
            - emails: List of unique email addresses
    """
    non_academic = []
    companies = []

    for aff in affiliations:
        aff_lower = aff.lower()

        if any(keyword in aff_lower for keyword in NON_ACADEMIC_KEYWORDS):
            non_academic.append(aff)

        if any(keyword in aff_lower for keyword in COMPANY_KEYWORDS):
            companies.append(aff)

    emails = extract_emails(affiliations)

    return list(set(non_academic)), list(set(companies)), emails
