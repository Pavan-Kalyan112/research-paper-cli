# tests/test_summary.py

import pytest
from unittest.mock import patch, Mock
from pubmed_fetcher.summary import summarize_abstract

def test_summarize_abstract_success():
    abstract = "This is a test abstract about machine learning in healthcare."

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "This paper discusses ML in healthcare."}

    with patch("requests.post", return_value=mock_response):
        result = summarize_abstract(abstract)
        assert "ML in healthcare" in result

def test_summarize_abstract_empty_input():
    result = summarize_abstract("")
    assert "No abstract provided" in result

def test_summarize_abstract_network_error():
    with patch("requests.post", side_effect=Exception("Connection failed")):
        result = summarize_abstract("Some abstract")
        assert "error" in result.lower()

def test_summarize_abstract_llm_returns_nothing():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": ""}
    with patch("requests.post", return_value=mock_response):
        result = summarize_abstract("Some abstract")
        assert "no summary" in result.lower()
