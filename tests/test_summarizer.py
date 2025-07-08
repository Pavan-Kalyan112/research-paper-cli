# tests/test_summarizer.py

import unittest
from pubmed_fetcher.summarizer import summarize_abstract

class TestSummarizer(unittest.TestCase):
    
    def test_summary_returns_string(self):
        abstract = "COVID-19 is a respiratory disease caused by a novel coronavirus."
        summary = summarize_abstract(abstract)
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary.strip()), 0)

    def test_summary_handles_empty_input(self):
        summary = summarize_abstract("")
        self.assertIsInstance(summary, str)

if __name__ == "__main__":
    unittest.main()
