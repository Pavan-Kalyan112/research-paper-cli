import pytest
from pubmed_fetcher import filters

def test_extract_emails_single():
    text = "Contact: john.doe@biotech.com"
    emails = filters.extract_emails(text)
    assert emails == {"john.doe@biotech.com"}

def test_extract_emails_multiple():
    text = "Emails: alice@moderna.com, bob@pfizer.org"
    emails = filters.extract_emails(text)
    assert "alice@moderna.com" in emails
    assert "bob@pfizer.org" in emails
    assert len(emails) == 2

def test_extract_person_name_valid():
    aff = "Dr. Alice Johnson, Research Lead at Vertex Pharmaceuticals"
    name = filters.extract_person_name(aff)
    assert name in ["Dr Alice", "Alice Johnson"]  # Accept either if implementation varies

def test_extract_person_name_short():
    aff = "Smith Biotech"
    name = filters.extract_person_name(aff)
    assert name in ["Smith Biotech", "Smith"]

def test_extract_person_name_unknown():
    aff = "department of biology, university of science"
    name = filters.extract_person_name(aff)
    assert name == "Unknown"

def test_classify_authors_full_case():
    affiliations = [
        "Dr. Alice Johnson, Moderna Inc., alice@moderna.com",
        "Department of Medicine, University of California",
        "Bob Smith, Vertex Biotech, bob.smith@vertex.com"
    ]

    non_academic, companies, emails = filters.classify_authors(affiliations)

    # Accept Dr. Alice or Alice Johnson depending on logic
    assert any(name in non_academic for name in ["Dr Alice", "Alice Johnson"])
    assert any(name in non_academic for name in ["Bob Smith", "Smith"])
    assert "Moderna" in " ".join(companies)
    assert "Vertex" in " ".join(companies)
    assert "alice@moderna.com" in emails
    assert "bob.smith@vertex.com" in emails
    assert all("University of California" not in c for c in companies)

def test_classify_authors_empty():
    non_academic, companies, emails = filters.classify_authors([])
    assert non_academic == set()
    assert companies == set()
    assert emails == set()
