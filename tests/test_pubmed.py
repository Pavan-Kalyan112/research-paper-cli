from pubmed_fetcher.pubmed import search_and_fetch

def test_search_and_fetch():
    results = search_and_fetch("covid vaccine", retmax=2)
    assert isinstance(results, list)
    assert len(results) > 0
    for paper in results:
        assert "pubmed_id" in paper
        assert "title" in paper
        assert "abstract" in paper
        assert "authors" in paper
        assert isinstance(paper["authors"], str)
  