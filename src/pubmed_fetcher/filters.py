import re
import string
from typing import List, Tuple, Set

# Add more relevant pharmaceutical/biotech keywords as needed
COMPANY_KEYWORDS = [
    "Pfizer", "Moderna", "AstraZeneca", "Johnson", "Novartis", "GSK",
    "Merck", "Sanofi", "Roche", "Bayer", "Amgen", "Biogen", "AbbVie",
    "Eli Lilly", "Takeda", "Genentech", "Bristol-Myers", "Regeneron", "Vertex"
]

# Common academic institution keywords
ACADEMIC_KEYWORDS = [
    "university", "institute", "college", "school of medicine",
    "hospital", "center", "centre", "faculty"
]


def extract_emails(text: str) -> Set[str]:
    """
    Extract email addresses from a string using regex.

    Args:
        text (str): Input text possibly containing emails.

    Returns:
        Set[str]: Set of extracted email addresses.
    """
    return set(re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text))


def extract_person_name(affiliation: str) -> str:
    """
    Heuristic to extract a potential name from an affiliation string.

    Args:
        affiliation (str): Raw affiliation text.

    Returns:
        str: Extracted name or raw snippet.
    """
    tokens = affiliation.strip().split()
    # Remove punctuation from each token to avoid trailing commas, periods, etc.
    name_tokens = [token.strip(string.punctuation) for token in tokens if token.istitle()]

    if len(name_tokens) >= 2:
        return f"{name_tokens[0]} {name_tokens[1]}"
    elif name_tokens:
        return name_tokens[0]
    else:
        return "Unknown"


def classify_authors(affiliations: List[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Classifies affiliations into:
    - Non-academic author names
    - Company affiliations based on keyword match
    - Emails extracted from affiliation text

    Args:
        affiliations (List[str]): A list of affiliation strings.

    Returns:
        Tuple[Set[str], Set[str], Set[str]]: non_academic_names, company_names, emails
    """
    non_academic = set()
    companies = set()
    emails = set()

    for aff in affiliations:
        aff_lower = aff.lower()

        # 💼 Check if not academic
        if not any(keyword in aff_lower for keyword in ACADEMIC_KEYWORDS):
            non_academic.add(extract_person_name(aff))

        # 🏢 Look for company names
        for keyword in COMPANY_KEYWORDS:
            if keyword.lower() in aff_lower:
                companies.add(keyword)

        # ✉️ Extract emails
        found_emails = extract_emails(aff)
        emails.update(found_emails)

    return non_academic, companies, emails
