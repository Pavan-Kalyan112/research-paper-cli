import numpy as np
from pubmed_fetcher import embedder

def test_get_embedding_model():
    model = embedder.get_embedding_model()
    assert model is not None

def test_embed_texts_output_shape():
    model = embedder.get_embedding_model()
    texts = ["Hair loss is a common condition.", "Minoxidil promotes hair growth."]
    embeddings = embedder.embed_texts(texts, model=model)
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] > 0  # vector size

def test_build_faiss_index():
    model = embedder.get_embedding_model()
    texts = ["Hair loss is a condition.", "Minoxidil treatment."]
    embeddings = embedder.embed_texts(texts, model=model)
    index = embedder.build_faiss_index(embeddings)
    assert index is not None
    assert hasattr(index, "search")

def test_embed_papers():
    papers = [
        {"Abstract": "This study investigates DHT blockers."},
        {"Abstract": "Aloe vera improves scalp health."}
    ]
    model = embedder.get_embedding_model()
    embeddings, metadata = embedder.embed_papers(papers, model=model)
    assert isinstance(embeddings, np.ndarray)
    assert len(metadata) == len(papers)
    assert embeddings.shape[0] == len(papers)
