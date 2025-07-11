import os
from pathlib import Path
from pubmed_fetcher import config


def test_base_dir_exists():
    assert config.BASE_DIR.exists(), "BASE_DIR should exist."


def test_export_dir_created():
    assert config.EXPORT_DIR.exists(), "EXPORT_DIR should be created on import."
    assert config.EXPORT_DIR.is_dir(), "EXPORT_DIR should be a directory."


def test_vector_store_dir_created():
    assert config.RAG_VECTOR_STORE_PATH.exists(), "RAG vector store path should be created."
    assert config.RAG_VECTOR_STORE_PATH.is_dir(), "RAG vector store path should be a directory."


def test_default_values():
    assert config.PUBMED_DB == "pubmed"
    assert config.DEFAULT_FETCH_LIMIT == 5
    assert config.LLM_MODEL_NAME == "mistral"
    assert config.RAG_EMBEDDING_MODEL.startswith("sentence-transformers/")
