# tests/test_summarizer.py

import pytest
from pubmed_fetcher.summarizer import summarize_abstract

def test_summary_is_string():
    """Ensure that the summary is returned as a string."""
    abstract = "COVID-19 is a global pandemic affecting millions worldwide."
    summary = summarize_abstract(abstract)
    assert isinstance(summary, str)

def test_summary_is_not_empty():
    """Check that the summary is not empty."""
    abstract = "Vaccines have shown effectiveness in reducing COVID-19 transmission and severity."
    summary = summarize_abstract(abstract)
    assert summary.strip() != ""

def test_handles_empty_abstract():
    summary = summarize_abstract("")
    assert isinstance(summary, str)
    assert summary.strip() == "No abstract provided for summarization."

def test_handles_none_input():
    summary = summarize_abstract(None)
    assert isinstance(summary, str)
    assert summary.strip() == "No abstract provided for summarization."
