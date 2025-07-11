import pytest
from unittest.mock import patch
from pubmed_fetcher.chat import chat_with_llm, chat_with_retry

# Mocked successful response
mock_response = {
    "message": {"content": "This is a mocked response from the LLM."}
}

@patch("pubmed_fetcher.chat.requests.post")
def test_chat_with_llm_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = mock_response

    prompt = "What is hair loss?"
    response = chat_with_llm(prompt)
    assert isinstance(response, str)
    assert "mocked response" in response.lower()

@patch("pubmed_fetcher.chat.requests.post")
def test_chat_with_llm_network_error(mock_post):
    mock_post.side_effect = Exception("Connection error")
    response = chat_with_llm("Test prompt")
    assert "LLM Error" in response or "Network error" in response

@patch("pubmed_fetcher.chat.chat_with_llm")
def test_chat_with_retry_success(mock_chat):
    mock_chat.return_value = "Valid response from retry"
    response = chat_with_retry("Retry this prompt", max_retries=2)
    assert "Valid response" in response

@patch("pubmed_fetcher.chat.chat_with_llm")
def test_chat_with_retry_failure(mock_chat):
    mock_chat.return_value = "❌ LLM Error: Model crashed"
    response = chat_with_retry("Bad model", max_retries=2)
    assert "❌ LLM failed to respond" in response
