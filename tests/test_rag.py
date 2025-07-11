import pytest
from pubmed_fetcher import rag

def test_rag_generate_answer_with_no_papers():
    query = "hair loss treatment"
    papers = []  # Empty input
    result = rag.generate_answer_with_context(query, papers)

    assert isinstance(result, str), "Output should be a string"
    assert "❌" in result or "No relevant papers" in result, "Should warn about missing context"

def test_rag_generate_answer_with_minimal_paper():
    query = "hair loss treatment"
    papers = [{
        "PubmedID": "123456",
        "Title": "Test Title",
        "Authors": "John Doe",
        "Abstract": "This is a test abstract.",
        "summary": "This is a test summary."
    }]
    result = rag.generate_answer_with_context(query, papers)

    assert isinstance(result, str), "Output should be a string"
    assert len(result) > 0, "Output should not be empty"
    
def test_rag_with_missing_file():
    """Test RAG gracefully handles missing input file."""
    result = rag.main(json_path="nonexistent.json", query="What is cancer?")
    assert result is None or isinstance(result, str)