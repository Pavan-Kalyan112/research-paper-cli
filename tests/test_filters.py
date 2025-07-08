# tests/test_filters.py

from pubmed_fetcher.filters import classify_authors, extract_emails

def test_classify_authors():
    affiliations = [
        "Department of Biology, Stanford University, USA.",
        "Pfizer Inc., New York, NY, USA.",
        "John Doe, Google Health, California.",
        "Independent researcher, India"
    ]

    non_academic, companies, emails = classify_authors(affiliations)

    assert "Independent researcher, India" in non_academic
    assert "Pfizer Inc., New York, NY, USA." in companies or "Google Health, California." in companies
    assert isinstance(emails, list)

def test_extract_emails():
    affiliations = [
        "Corresponding author: john.doe@university.edu",
        "Contact us at: support@pfizer.com",
        "Visit our website"
    ]

    emails = extract_emails(affiliations)
    assert "john.doe@university.edu" in emails
    assert "support@pfizer.com" in emails
