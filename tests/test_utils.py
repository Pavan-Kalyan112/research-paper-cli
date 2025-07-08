# tests/test_utils.py

import unittest
import os
from pubmed_fetcher.utils import save_as_csv, save_as_pdf, save_as_markdown

SAMPLE_DATA = [
    {
        "title": "Sample Paper",
        "authors": "John Doe, Jane Smith",
        "abstract": "This is a sample abstract.",
        "summary": "This is a summary."
    }
]

class TestUtils(unittest.TestCase):

    def test_save_csv_creates_file(self):
        filename = "test_output.csv"
        save_as_csv(SAMPLE_DATA, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_save_pdf_creates_file(self):
        filename = "test_output.pdf"
        save_as_pdf(SAMPLE_DATA, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

    def test_save_markdown_creates_file(self):
        filename = "test_output.md"
        save_as_markdown(SAMPLE_DATA, filename)
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)

if __name__ == "__main__":
    unittest.main()
