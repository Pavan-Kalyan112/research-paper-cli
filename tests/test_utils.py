import os
from pubmed_fetcher.utils import save_as_csv

def test_save_as_csv(tmp_path):
    dummy_data = [{
        "title": "Sample Paper",
        "authors": "John Doe",
        "abstract": "This is an abstract.",
        "summary": "This is a summary."
    }]
    filepath = tmp_path / "output.csv"
    save_as_csv(dummy_data, filepath)
    assert filepath.exists()
