import pytest
from unittest.mock import patch, MagicMock
import pubmed_fetcher.llm as llm


# -------- summarize_with_llm --------

def test_summarize_with_llm_valid():
    abstract = "Hair loss affects millions of people globally."

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Hair loss is a common condition..."}
    mock_response.status_code = 200

    with patch("pubmed_fetcher.llm.requests.post", return_value=mock_response):
        summary = llm.summarize_with_llm(abstract)
        assert "Hair loss is a common condition" in summary


def test_summarize_with_llm_empty():
    summary = llm.summarize_with_llm("")
    assert summary == "⚠️ Empty abstract provided."


def test_summarize_with_llm_timeout():
    with patch("pubmed_fetcher.llm.requests.post", side_effect=llm.requests.exceptions.Timeout):
        summary = llm.summarize_with_llm("Some abstract")
        assert "timed out" in summary.lower()


def test_summarize_with_llm_network_error():
    with patch("pubmed_fetcher.llm.requests.post", side_effect=llm.requests.exceptions.ConnectionError("Network down")):
        summary = llm.summarize_with_llm("Some abstract")
        assert "network error" in summary.lower()


# -------- chat_with_llm --------

def test_chat_with_llm_valid():
    prompt = "Explain CRISPR gene editing."

    mock_response = MagicMock()
    mock_response.json.return_value = {"message": {"content": "CRISPR is a gene editing technique..."}}
    mock_response.status_code = 200

    with patch("pubmed_fetcher.llm.requests.post", return_value=mock_response):
        response = llm.chat_with_llm(prompt)
        assert "CRISPR" in response


def test_chat_with_llm_empty():
    response = llm.chat_with_llm("")
    assert response == "⚠️ Prompt is empty."


def test_chat_with_llm_timeout():
    with patch("pubmed_fetcher.llm.requests.post", side_effect=llm.requests.exceptions.Timeout):
        response = llm.chat_with_llm("Explain DNA")
        assert "timed out" in response.lower()


def test_chat_with_llm_network_error():
    with patch("pubmed_fetcher.llm.requests.post", side_effect=llm.requests.exceptions.ConnectionError("No internet")):
        response = llm.chat_with_llm("Explain cells")
        assert "network error" in response.lower()


# -------- chat_with_retry --------

def test_chat_with_retry_success_on_first_try():
    with patch("pubmed_fetcher.llm.chat_with_llm", return_value="✅ Good response"):
        result = llm.chat_with_retry("test prompt", retries=3)
        assert "✅" in result


def test_chat_with_retry_fails_all_attempts():
    with patch("pubmed_fetcher.llm.chat_with_llm", return_value="⚠️ Failed"):
        result = llm.chat_with_retry("retry prompt", retries=2)
        assert "failed to respond" in result.lower()
