import os
import json
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, mock_open

from pubmed_fetcher import embedder


# ------------------ load_data ------------------

def test_load_data_file_not_exists(tmp_path, monkeypatch):
    fake_file = tmp_path / "nonexistent.json"
    monkeypatch.setattr(embedder, "SUMMARY_FILE", str(fake_file))
    assert embedder.load_data() == []

def test_load_data_success(monkeypatch):
    test_json = [{"Title": "Test"}]
    m = mock_open(read_data=json.dumps(test_json))
    monkeypatch.setattr(embedder, "SUMMARY_FILE", "some_file.json")
    with patch("builtins.open", m), patch("os.path.exists", return_value=True):
        data = embedder.load_data()
        assert data == test_json


# ------------------ embed_texts ------------------

@patch.object(embedder.model, "encode", return_value=np.array([[0.1, 0.2], [0.3, 0.4]]))
def test_embed_texts(mock_encode):
    texts = ["This is test 1", "Test 2"]
    embeddings = embedder.embed_texts(texts)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 2)
    mock_encode.assert_called_once()


# ------------------ build_faiss_index ------------------

def test_build_faiss_index_creates_index():
    embeddings = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    index = embedder.build_faiss_index(embeddings)
    assert isinstance(index, embedder.faiss.IndexFlatL2)
    assert index.ntotal == 2


# ------------------ save_index ------------------

@patch("builtins.open", new_callable=mock_open)
@patch("pubmed_fetcher.embedder.faiss.write_index")
def test_save_index(mock_write_index, mock_file):
    dummy_index = MagicMock()
    metadata = [{"PubmedID": "123"}]
    embedder.save_index(dummy_index, metadata)
    mock_write_index.assert_called_once()
    mock_file.assert_called_once_with(embedder.META_FILE, "w", encoding="utf-8")


# ------------------ main (integration-style smoke test) ------------------

@patch("pubmed_fetcher.embedder.embed_texts", return_value=np.array([[1.0, 2.0]], dtype=np.float32))
@patch("pubmed_fetcher.embedder.save_index")
@patch("pubmed_fetcher.embedder.load_data", return_value=[
    {
        "Title": "Test Title",
        "Authors": "John Doe",
        "summary": "Test summary",
        "PubmedID": "123",
        "Publication Date": "2025",
        "CompanyAffiliation(s)": "Pfizer",
        "Corresponding Author Email": "john@example.com",
        "Abstract": "Test abstract"
    }
])
def test_main_success(mock_load, mock_save, mock_embed):
    embedder.main()
    mock_load.assert_called_once()
    mock_embed.assert_called_once()
    mock_save.assert_called_once()
