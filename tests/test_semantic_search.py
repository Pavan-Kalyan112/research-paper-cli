import pytest
import json
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
import pubmed_fetcher.semantic_search as semantic_search


# --- Fixtures ---
@pytest.fixture
def sample_metadata():
    return [
        {
            "Title": "Cancer Drug Study",
            "Abstract": "This study explores cancer drug discovery methods.",
            "summary": "Cancer drug discovery summary.",
            "Authors": "John Doe",
            "CompanyAffiliation(s)": "Pfizer",
            "Corresponding Author Email": "john@example.com",
            "PubmedID": "12345",
            "Publication Date": "2022-01-01"
        },
        {
            "Title": "AI in Cancer Research",
            "Abstract": "AI can assist in cancer diagnosis and treatment.",
            "summary": "AI for cancer treatment.",
            "Authors": "Alice Smith",
            "CompanyAffiliation(s)": "Google Health",
            "Corresponding Author Email": "alice@example.com",
            "PubmedID": "12346",
            "Publication Date": "2022-02-01"
        }
    ]


# --- Test: Brute-force fallback ---
def test_search_with_metadata_no_index(sample_metadata):
    with patch("pubmed_fetcher.semantic_search.faiss.read_index", side_effect=FileNotFoundError()), \
         patch("pubmed_fetcher.semantic_search.load_index", return_value=(None, sample_metadata)), \
         patch("pubmed_fetcher.semantic_search.SentenceTransformer.encode", side_effect=lambda x, **kwargs: np.array([[0.1]*384 for _ in x])), \
         patch("pubmed_fetcher.semantic_search.cos_sim", return_value=np.array([[0.8, 0.6]])):  # Mock similarity

        results = semantic_search.search("cancer drug")
        assert isinstance(results, list)
        assert len(results) == 2
        assert all("Title" in paper for paper in results)


# --- Test: LLM explanation call ---
def test_ask_llm_about_matches(sample_metadata):
    with patch("pubmed_fetcher.semantic_search.chat_with_llm", return_value="This is a test response."):
        result = semantic_search.ask_llm_about_matches("cancer research", sample_metadata)
        assert result is None  # it prints to console, doesn't return


# --- Test: FAISS + metadata fallback ---
def test_load_index_fallback(tmp_path):
    # Write fake cache file
    fake_cache = tmp_path / ".last_results.json"
    dummy_data = [{
        "Title": "Fallback Paper",
        "Abstract": "Fallback abstract.",
        "summary": "Fallback summary."
    }]
    fake_cache.write_text(json.dumps(dummy_data), encoding="utf-8")

    # Patch paths to use temporary test folder
    with patch("pubmed_fetcher.semantic_search.INDEX_PATH", str(tmp_path / "faiss_index.bin")), \
         patch("pubmed_fetcher.semantic_search.META_PATH", str(tmp_path / "metadata.json")), \
         patch("pubmed_fetcher.semantic_search.CACHE_FILE", str(fake_cache)):

        index, metadata = semantic_search.load_index()
        assert index is None
        assert isinstance(metadata, list)
        assert metadata[0]["Title"] == "Fallback Paper"


# --- Test: No metadata edge case ---
def test_search_returns_empty_if_no_metadata():
    with patch("pubmed_fetcher.semantic_search.load_index", return_value=(None, None)):
        results = semantic_search.search("irrelevant")
        assert results == []
