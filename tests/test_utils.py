import os
import tempfile
import pytest
from pubmed_fetcher.utils import save_results

# --- Sample Mock Data ---
mock_results = [
    {
        "PubmedID": "12345678",
        "Title": "Test Paper Title",
        "Authors": "Doe J, Smith A",
        "summary": "This is a summary.",
        "Publication Date": "2025-01-01",
        "CompanyAffiliation(s)": "Moderna Inc.",
        "Corresponding Author Email": "john.doe@example.com",
        "Abstract": "This is a long abstract about testing utilities in Python."
    }
]

empty_results = []


# --- File Creation Tests ---
@pytest.mark.parametrize("file_format, extension", [
    ("csv", "csv"),
    ("pdf", "pdf"),
    ("md", "md"),
    ("markdown", "md"),
])
def test_save_results_creates_file(file_format, extension):
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, f"output.{extension}")
        save_results(mock_results, filename, file_format)
        assert os.path.exists(filename), f"{file_format.upper()} file was not created."


# --- Empty Input ---
@pytest.mark.parametrize("file_format, extension", [
    ("csv", "csv"),
    ("pdf", "pdf"),
    ("md", "md"),
])
def test_save_empty_results(file_format, extension):
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, f"empty_output.{extension}")
        save_results(empty_results, filename, file_format)
        assert os.path.exists(filename), f"Empty {file_format.upper()} file was not created."


# --- Invalid Format ---
@pytest.mark.parametrize("bad_format", ["txt", "json", "exe"])
def test_save_results_invalid_format(bad_format):
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, f"output.{bad_format}")
        with pytest.raises(ValueError, match="Unsupported format"):
            save_results(mock_results, filename, bad_format)
