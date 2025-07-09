import os
import pytest
from unittest.mock import patch, Mock
from importlib import reload

# Force environment variable for all tests
os.environ["USE_LLM"] = "true"

from pubmed_fetcher import llm


# ------------------- summarize_with_llm tests -------------------

def test_summarize_with_llm_disabled(monkeypatch):
    monkeypatch.setenv("USE_LLM", "false")
    reload(llm)
    result = llm.summarize_with_llm("Some abstract")
    assert "disabled" in result.lower()
    monkeypatch.setenv("USE_LLM", "true")
    reload(llm)  # restore

def test_summarize_with_empty_abstract():
    result = llm.summarize_with_llm("   ")
    assert "empty" in result.lower()

@patch("requests.post")
def test_summarize_with_llm_success(mock_post):
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = {"response": "This is a summary."}
    result = llm.summarize_with_llm("A research abstract.")
    assert result == "This is a summary."

@patch("requests.post")
def test_summarize_with_llm_empty_response(mock_post):
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = {"response": ""}
    result = llm.summarize_with_llm("A research abstract.")
    assert "no summary" in result.lower()

@patch("requests.post", side_effect=Exception("Something went wrong"))
def test_summarize_with_llm_exception(mock_post):
    result = llm.summarize_with_llm("Abstract content")
    assert "unexpected" in result.lower()


# ------------------- chat_with_llm tests -------------------

def test_chat_with_llm_disabled(monkeypatch):
    monkeypatch.setenv("USE_LLM", "false")
    reload(llm)
    result = llm.chat_with_llm("What is AI?")
    assert "disabled" in result.lower()
    monkeypatch.setenv("USE_LLM", "true")
    reload(llm)

def test_chat_with_llm_empty_prompt():
    result = llm.chat_with_llm("   ")
    assert "prompt is empty" in result.lower()

@patch("requests.post")
def test_chat_with_llm_success_message_content(mock_post):
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = {
        "message": {"content": "This is the answer."}
    }
    result = llm.chat_with_llm("Explain AI")
    assert result == "This is the answer."

@patch("requests.post")
def test_chat_with_llm_fallback_response(mock_post):
    mock_post.return_value = Mock(status_code=200)
    mock_post.return_value.json.return_value = {"response": "Fallback response"}
    result = llm.chat_with_llm("Fallback test")
    assert result == "Fallback response"

@patch("requests.post", side_effect=Exception("Something broke"))
def test_chat_with_llm_exception(mock_post):
    result = llm.chat_with_llm("Some question")
    assert "unexpected" in result.lower()
