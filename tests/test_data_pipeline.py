import pytest
from pubmed_fetcher.data_pipeline import search_and_fetch

def test_search_and_fetch_results():
    query = "hair loss treatment"
    results = search_and_fetch(query, limit=3)

    assert isinstance(results, list), "Results should be a list"
    assert len(results) <= 3, "Should return 3 or fewer results"

    for paper in results:
        assert isinstance(paper, dict), "Each paper should be a dictionary"
        assert "Title" in paper, "Missing 'Title' in paper data"
        assert "Abstract" in paper, "Missing 'Abstract' in paper data"

def test_empty_query():
    results = search_and_fetch("")
    assert isinstance(results, list)
    assert len(results) == 0
