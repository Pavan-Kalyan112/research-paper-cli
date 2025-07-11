# tests/test_summary.py

import pytest
from unittest.mock import patch, Mock
from pubmed_fetcher.summary import summarize_abstract

def test_summarize_abstract_success():
    abstract = "This is a test abstract about machine learning in healthcare."

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "This paper discusses ML in healthcare."}

import pytest
from unittest.mock import patch
from pubmed_fetcher import summary


def test_summarize_abstract_llm_disabled(monkeypatch):
    from pubmed_fetcher import summary
    monkeypatch.setattr(summary, "USE_LLM", False)
    result = summary.summarize_abstract("This is a test abstract.")
    assert "disabled" in result.lower() or "🔇" in result


def test_summarize_abstract_empty_input():
    result = summary.summarize_abstract("")
    assert "No abstract" in result


@patch("requests.post")
def test_summarize_abstract_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "response": "This is a simplified summary."
    }

    result = summary.summarize_abstract("Complex biological text.")
    assert result == "This is a simplified summary."


@patch("requests.post")
def test_summarize_abstract_empty_response(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"response": ""}
    result = summary.summarize_abstract("Some content")
    assert "empty summary" in result


@patch("requests.post", side_effect=Exception("Server failure"))
def test_summarize_abstract_generic_exception(mock_post):
    result = summary.summarize_abstract("Some text")
    assert "Unexpected error" in result


@patch("requests.post", side_effect=Exception("Connection refused"))
def test_summarize_abstract_network_error(mock_post):
    result = summary.summarize_abstract("Another test abstract")
    assert "Network error" in result or "Unexpected error" in result
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
    from pubmed_fetcher import summary
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": ""}
    with patch("requests.post", return_value=mock_response):
        result = summary.summarize_abstract("Some abstract")
        assert "empty summary" in result.lower()